import boto3
import psycopg2
from cryptography.fernet import Fernet
import json
from datetime import datetime
from localstack import config

# Create a function to generate an encryption key
def generate_key():
    return Fernet.generate_key()

# Create a function to initialize the encryption key
def initialize_key(key):
    return Fernet(key)

# Encrypt data using the encryption key
def encrypt_data(fernet, data):
    return fernet.encrypt(data.encode()).decode()

# Decrypt data using the encryption key
def decrypt_data(fernet, encrypted_data):
    return fernet.decrypt(encrypted_data.encode()).decode()

# Connect to LocalStack SQS
sqs = boto3.client('sqs', region_name='us-east-1', endpoint_url=f'http://localhost:4566/000000000000/login-queue')

# Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database='user_logins',
    user='postgres',
    password='postgres',
    port=5433
)

# Generate and initialize an encryption key
encryption_key = generate_key()
fernet = initialize_key(encryption_key)

def createEncryptInsert(message):
    try:
        # Extract data from the message
        data = json.loads(message['Body'])
        user_id = data['user_id']
        device_type = data['device_type']
        ip = data['ip']
        device_id = data['device_id']
        locale = data['locale']
        app_version = int(data['app_version'].replace(".", ""))

        # Encrypt PII fields
        encrypted_ip = encrypt_data(fernet, ip)
        encrypted_device_id = encrypt_data(fernet, device_id)

        create_date = datetime.now()

        # Insert encrypted Data into PostgreSQL
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_logins(user_id, device_type, encrypted_ip, encrypted_device_id, locale, app_version, create_date) VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (user_id, device_type, encrypted_ip, encrypted_device_id, locale, app_version, create_date))
        conn.commit()
        cursor.close()

    except Exception as e:
        print(f"Error processing message: {str(e)}")

def retrieveDecryptedData():
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, device_type, encrypted_ip, encrypted_device_id, locale, app_version, create_date FROM user_logins")
        rows = cursor.fetchall()
        for row in rows:
            user_id, device_type, encrypted_ip, encrypted_device_id, locale, app_version, create_date = row
            # Decrypt PII fields
            ip = decrypt_data(fernet, encrypted_ip)
            device_id = decrypt_data(fernet, encrypted_device_id)
            
            print(f"User ID: {user_id}, Device Type: {device_type}, IP: {ip}, Device ID: {device_id}, Locale: {locale}, App Version: {app_version}, Create Date: {create_date}")

    except Exception as e:
        print(f"Error retrieving data: {str(e)}")

def main():
    queue_url = 'http://localhost:4566/000000000000/login-queue'
    try:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=50
        )
        if 'Messages' in response:
            for message in response['Messages']:
                createEncryptInsert(message)
    
        # Retrieve and decrypt data from PostgreSQL
        #retrieveDecryptedData()

    except Exception as e:
        print("An error occurred:", str(e))

if __name__ == "__main__":
    main()

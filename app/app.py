

import boto3
import psycopg2
import hashlib
import json
from datetime import datetime
from localstack import config

# Create a function to hash PII data
def hash_data(data):
    sha256 = hashlib.sha256()
    sha256.update(data.encode('utf-8'))
    return sha256.hexdigest()

def createMaskInsert(message, conn):
    try:
        # Extract data from the message
        data = json.loads(message['Body'])
        user_id = data['user_id']
        device_type = data['device_type']
        ip = data['ip']
        device_id = data['device_id']
        locale = data['locale']
        app_version = int(data['app_version'].replace(".", ""))

        # Mask PII fields
        masked_ip = hash_data(ip)
        masked_device_id = hash_data(device_id)

        create_date = datetime.now()

        # Insert masked Data into PostgreSQL
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_logins(user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date) VALUES (%s,%s,%s,%s,%s,%s,%s)""",(user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date))
        conn.commit()
        cursor.close()

    except Exception as e:
        print(f"Error processing message: {str(e)}")

def main():
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

    queue_url = 'http://localhost:4566/000000000000/login-queue'
    try:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=5   #writing 5 records at a time
        )
        if 'Messages' in response:
            for message in response['Messages']:
                # Print the message body
                # print(message['Body'])
                d = json.loads(message['Body'])
                #Inserting only valid records with all 6 valid(not null) fields
                if len(d.keys()) == 6:
                    createMaskInsert(message, conn)
    except Exception as e:
        print("An error occurred:", str(e))

if __name__ == "__main__":
    main()
        

# SQStoPostgres Data Engineering Project 
## ETL from an SQS queue to Postgres database

The main objective of this project is to develop an ETL (Extract, Transform, Load) pipeline. This pipeline is designed to retrieve user login behavior data stored in a JSON format from an AWS SQS Queue, mask specific fields containing personal identifiable information (PII), and writes the transformed data to a PostgreSQL database.
# Project Setup
### Requirements
 *  python3  
 *	psql (in your local)  
 *	awscli (for local testing)  
 *	Docker  
 *	Docker-compose  
## Installations
* Install Docker in your local computer (I am using mac and I downloaded from the internet)  
  
* Install python packages like boto3 and psycopg2  
  `pip install boto3`   
  `pip install psycopg2`  
   
* Install postgres in your local.  
   `brew install postgres`  
  
*	We need boto3 to connect the sqs queue with our python script.  
*	And we need psycopg2 to connect our python script with the postgres database.  
*	After Setting up Docker, Pull the localstack image we have of the SQS Queue.  
`docker pull fetchdocker/data-takehome-localstack`  
  
* After pulling the image, Run the Container  
`docker run -d --name localstack -p 4566:4566 -e SERVICES=sqs fetchdocker/data-takehome-localstack`    
This command will start a LocalStack container named localstack, exposing port 4566 for SQS.  

* Read a message from the queue using `awslocal` :  
`awslocal sqs receive-message --queue-url http://localhost:4566/000000000000/login-queue`  

* Connect to the PostgreSQL database and Check if the table is created:  
`psql -d postgres -U postgres -p 5433 -h localhost -W`  
Then run the following command:  
`SELECT * FROM user_logins`;  


## Structure  
The project is structured in a following way:  
 *  `SQStoPostgres/` : The main application folder that contains the source code for the whole       pipeline. We need to give our commands here.  
 * `app/`: Its a sub directory inside the SQStoPostgres directory.  
 * `app.py`: The main program to run the pipeline. It contains all the process right from           reading the sqs message, masking it, and inserting the records into the postgres database.  
 * `docker-compose.yml`: Docker Compose configuration file to set up the local development      environment.  
 * `__init__.py`: Initializes the application package.

## Running the pipeline:
To run the pipeline, Execute the following command from the `SQStoPostgres/` directory.  
`python3 -m app.app`  
  
This command performs the following tasks:
* It retrieves messages from the SQS Queue,
* Processes these messages to extract and masks sensitive data as required,
* And then writes the resulting records into the PostgreSQL database.

After giving the command like this:  
  <img width="682" alt="Screen Shot 2023-09-14 at 3 55 15 PM" src="https://github.com/gnithin610/SQStoPostgres/assets/137355081/084e9239-63eb-4acb-af55-5e2cd61c52f4">
  You can see records adding into the postgres database like this:  
  <img width="1401" alt="Screen Shot 2023-09-14 at 2 29 59 AM" src="https://github.com/gnithin610/SQStoPostgres/assets/137355081/8cf5f8dc-d595-4064-84de-5b74f25432e5">


## Solutions (Set 1)
* We will read the messages from the queue using boto3 connection which was enabled after creating the container from the localstack image pulled by Docker.
* We used Dictionaries, Json loads, Exception handling, and lot more techniques to write the python script.
* We masked the data using a hashing technique called SHA256. It was imported from `hashlib` library and is encoded such that the data analysts can identify duplicate values in those fields.
* For connecting the database with the python script, we used `psycopg2` module. It connects and helps us insert the new records into the database.
* The application will run in the directory `SQStoPostgres/`.


## Solutions (Set 2)
#### Deploying the application
We can use a containerization service like kubernetes or any other cloud provided managed containerized services so that we can scale, manage, and monitor the application in a production environment.
#### Components to make it Production-Ready
* We can use AWS CloudWatch for managing the logs and performing the analysis
* We can have CI/CD pipeline for Deployment, building and testing the environment.
* We can use tools like Grafana or DataDog to track the health and performance of the application.
#### Scaling with growing Dataset
* We can add more EC2 instances to implement scaling horizontally and allowing data processing seamlessly.
* We can use a message broker like Apache Kafka to enable realtime streaming with high throughput handling. 
* We can also do several approaches to optimize the performance of the database like partitioning, indexing etc.
#### PII Recovery
* Performing the Hashing algorithm SHA256 is a one-way process and the original fields cannot be retrieved. Instead we need to store the original data in some other database. As per the Analytics purpose, This technique works. We can use other encrpytion techniques also in case we need to access. I am including another python file `appencrypt.py` in the directory. We can use that instead. 
#### Assumptions
* I had some password issues connecting to port 5432. So I connected to 5433 and written into it.
* Assuming the PII data is not needed to be recovered to the original, Hashing technique like sha256 is used.
* The provided Docker Compose file sets up the local development environment, and no additional configuration is required.
* The SQS Queue contains a consistent structure, without any unknown schema.  
* The python script is not designed for advanced datasets and features like scheduling etc.

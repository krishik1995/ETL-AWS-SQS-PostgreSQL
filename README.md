# ETL pipeline for processing SQS messages 

# Project Overview

This project involves a Dockerized pipeline for fetching data from AWS SQS, then transforming by masking certain Personally Identifiable Information (PII), and then loading it into a PostgreSQL database.



The application runs using the ETL (Extract, Transform, Load) strategy. Messages are seamlessly read from the queue using the AWS SDK, specifically the `boto3` library, which offers direct and efficient interactions with Amazon SQS. This ensures efficient polling and batch processing to optimize throughput. Data structures play a pivotal role in the pipeline; dictionaries and lists are predominantly used for their efficiency in storing and manipulating data. As privacy is paramount, PII data, specifically IP addresses and device IDs, are masked using AES encryption, ensuring that not only is the information secure, but duplicates can also be readily identified by comparing the encrypted values. The application establishes a steadfast connection to Postgres using the psycopg2 library, providing a seamless experience for writing and querying the database. With the power of Docker, the application is encapsulated within a container, ensuring consistent runtime environments and smooth deployment. The Docker setup, as outlined in the `docker-compose.yml`, combines services like LocalStack and Postgres, allowing the application to run in an interconnected environment while ensuring modular separation of concerns.


## Files in this project:

- **main.py**: The main driver script that coordinates the extraction, transformation, and loading process.
- **extractor.py**: Responsible for fetching data from an AWS Simple Queue Service (SQS) and ensuring that the messages conform to a specific structure.
- **transformer.py**: Contains functionality to mask PII from the data.
- **loader.py**: Handles insertion of the transformed data into a PostgreSQL database.
- **encryption_utils.py**: Contains utilities to handle encryption, specifically for masking PII.
- **aws_config.py**: Configuration details related to AWS services.
- **general_config.py**: General configuration details, like logging settings.
- **Dockerfile**: Contains instructions on how to build the Docker image for the application.
- **docker-compose.yml**: Defines and runs the multi-container Docker applications; includes configurations for Localstack, PostgreSQL, and the main app.
- **etl_logs.log**: A log file that captures information, warnings, errors, and other significant events during the ETL process.

### Data Validation 

This project utilizes data validation checks in each phase, extraction, transformation and loading to ensure quality.

### Encryption Strategy

The project employs an AES encryption strategy to mask Personally Identifiable Information (PII), specifically for IP and device ID. AES, or Advanced Encryption Standard, provides strong symmetric encryption, ensuring both security and reversibility of the data. The encryption key used is securely managed via environment variables.


## How to run this Dockerized application:

1. Clone the repository from GitHub.
   ```bash
   git clone <repository_url>
   ```
3. Ensure you have Docker and Docker-Compose installed on your machine.
4. Navigate to the project directory where the `docker-compose.yml` file is located.
5. Run the following command in the terminal to build the Docker images and start the multi-container application. This will start Localstack, PostgreSQL, and the main 
   application.
   ``` bash
   docker-compose up --build
   ```
   *Note* The application waits for the containers to be built. Application run starts after 10 - 20 seconds after the containers have been built to ensure proper integration. 
7. Once the application is running, you can monitor the `etl_logs.log` file for detailed logs of the ETL process.
8. To shut down the application and the associated services, run
   ``` bash
   docker-compose down
   ``` 

Ensure to replace placeholders like `<repository_url>` with the specific details relevant to your repository.
   

## Production Deployment strategy 

To deploy this Dockerized application in production, I would use a Kubernetes cluster. Kubernetes can manage, scale, and deploy Docker containers. A CI/CD pipeline would be established for automatic testing, building, and deployment of changes to the application. Deploying using Kubernetes will also allow easy scaling of the application based on load.

## Additional components to consider for production

- **Scheduling**: Utilize tools like Airflow to efficiently automate scheduling and scaling this application.
- **Error Handling & Recovery**: Improve robustness by adding error handling and recovery mechanisms.
- **Monitoring & Logging**: Integrate with platforms like Prometheus for monitoring and ELK Stack for logging within the Docker containers.
- **Security**: Implement strict IAM roles, security groups, and data encryption both at rest and in transit. Additionally, secure Docker container communication.
- **Automated Testing**: Implement unit tests, integration tests, and end-to-end tests in the Docker environment to ensure code quality and functionality.
- **Backup & Recovery**: Automated backup solutions for the PostgreSQL database container and a disaster recovery plan.

## Scalability
We could consider adding the following components to make sure that our application is scalable.
- **Horizontal Scaling**: Kubernetes can help scale out by adding more application replicas as the dataset grows.
- **Database Optimization**: Implement sharding, partitioning, and indexing in PostgreSQL to accommodate a larger dataset.
- **Load Balancers**: Deploy a load balancer to distribute incoming data to multiple application instances.
- **Auto-Scaling**: Use Kubernetes auto-scaling based on CPU or memory usage to handle varying loads.

## PII Recovering Strategy for Data Analysts/Scientists.

Since the PII is masked using AES encryption strategy, it can be recovered using the decryption method (Included in encryption_utils.py) provided the correct encryption key is available. Always store encryption keys securely and separate them from the data in a Kubernetes secret or an AWS Key Management Service.

## Assumptions
- **Message Structure**: The Data Validity checks are built on the assumption that the SQS Queue contains JSON data with a consistent structure, containing fields like user_id, 
                          device_type, ip, device_id, locale, app_version, and create_date.
- **PostgreSQL database** - The database is set up with the correct table schema to store the processed records                         
  
- **App Version**: Assumed that app version is required to be converted to integer for downstream process. **Suggestion** Decompose the app version into separate INTEGER columns, e.g., 
                   2.3.9 can be decomposed to major_version, minor_version, and patch_version to capture complete information. Additionally, we could consider converting it into 
                   varchar for simple storage allowing more flexibility for the data analysts/scientists to perform their transformations in the later stages.
- **Data Source**: Assumed that the main source of data is the AWS SQS service simulated by Localstack in a Docker environment.
- **Data Volume**: Assumed that data volume is moderate and doesn't require immediate parallel processing or streaming solutions.



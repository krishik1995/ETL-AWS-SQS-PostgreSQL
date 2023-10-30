"""
AWS Configuration
"""
# Configuration settings for various components
AWS_CONFIG = {
    'region_name': 'us-east-1',            # AWS region where services are deployed
    'endpoint_url': 'http://localstack:4566',  # Endpoint URL for the service 
    'queue_url': 'http://localstack:4566/000000000000/login-queue',  # URL for the SQS queue used for login
    'MaxNumberOfMessages': 20           # Maximum number of messages to retrieve from the queue at once
}



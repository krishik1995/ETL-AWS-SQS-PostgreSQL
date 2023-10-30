from multiprocessing.connection import wait
import boto3
import logging
import json
from aws_config import AWS_CONFIG
from general_config import GENERAL_CONFIG
from jsonschema import validate, ValidationError

# Load the JSON configuration for AWS credentials and other settings
with open('pwd.json', 'r') as file:
    pwd = json.load(file)

# Setting up logging configuration
# This will handle error logs and data validity checks
logging.basicConfig(filename=GENERAL_CONFIG['filename'], level=logging.INFO)

# Defining Message Schema for Data Validation.
MESSAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "user_id": {
            "type": "string",
            "minLength": 1  # Ensure user_id is not empty
        },
        "device_type": {
            "type": ["string", "null"]
        },
        "ip": {
            "type": ["string", "null"]
        },
        "device_id": {
            "type": ["string", "null"]
        },
        "locale": {
            "type": ["string", "null"]
        },
        "app_version": {
            "type": ["string", "null"]
        }
    },
    "required": ["user_id", "device_type", "ip", "device_id", "locale", "app_version"]
}




def validate_message_structure(data):
    """
    Validate the provided message structure against a predefined schema.

    Args:
    - data (dict): The message to validate.
    
    Returns:
    - bool: True if the message is valid, False otherwise.
    """
    try:
        validate(data, MESSAGE_SCHEMA)
        return True
    except ValidationError as ve:
        logging.warning(f"Message validation error: {ve}. Full message structure: {data}")
        return False

def fetch_from_sqs(queue_url):
    """ Fetch messages from an SQS queue and validate their structure. """
    try:
        # Configure SQS client with AWS config values.
        sqs = boto3.client('sqs',
                   endpoint_url=AWS_CONFIG['endpoint_url'],
                   aws_access_key_id=pwd['aws_access_key_id'],
                   aws_secret_access_key=pwd['aws_secret_access_key'],
                   region_name=AWS_CONFIG['region_name'])
        messages = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=AWS_CONFIG['MaxNumberOfMessages'], WaitTimeSeconds=20)
        messages = messages.get('Messages', [])

        # List to store valid messages
        valid_messages = []

        # Reading fetched messages
        for message in messages:
            data_str = message['Body']
            try:
                data = json.loads(data_str)
                is_valid = validate_message_structure(data) 
                if is_valid:
                    valid_messages.append({'Body': data, 'ReceiptHandle': message['ReceiptHandle']})
                else:
                    logging.warning(f"Invalid message structure: {data_str}")
            except json.JSONDecodeError:
                logging.error(f"Error decoding JSON: {data_str}")
        total_recieved=len(messages)            
        return (total_recieved, valid_messages)        
        
    except Exception as e:
        logging.error(f"Error fetching messages from SQS: {e}")
        return []


def delete_message_from_sqs(queue_url, receipt_handle):
    """
    Delete a message from the SQS queue.

    Args:
    - queue_url (str): The URL of the SQS queue.
    - receipt_handle (str): The receipt handle of the message to delete.
    """
    try:
        sqs = boto3.client('sqs',
                   endpoint_url=AWS_CONFIG['endpoint_url'],
                   aws_access_key_id=pwd['aws_access_key_id'],
                   aws_secret_access_key=pwd['aws_secret_access_key'],
                   region_name=AWS_CONFIG['region_name'])

        sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
        #logging.info(f"Successfully deleted message with ReceiptHandle: {receipt_handle}") 

    except Exception as e:
        logging.error(f"Error deleting message from SQS: {e}")
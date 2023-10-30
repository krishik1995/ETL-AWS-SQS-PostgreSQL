import time
import json
import boto3
from aws_config import AWS_CONFIG
from extractor import fetch_from_sqs, delete_message_from_sqs
from general_config import GENERAL_CONFIG
from transformer import mask_pii
from loader import insert_to_postgres
from encryption_utils import AESCipher
import logging

# Setting up logging
logging.basicConfig(filename=GENERAL_CONFIG['filename'], level=logging.INFO)

# Load the JSON configuration
with open('pwd.json', 'r') as file:
    pwd = json.load(file)

# Setting maximum retires and return delay for check_sqs_service 
maximum_tries = 5
retry_delay=15

def check_sqs_service(queue_url, max_retries=maximum_tries, retry_delay=retry_delay):
    """Check if SQS service is up and the queue is visible. Retries for a set number of times if there's an exception."""
    
    retries = 0
    while retries < max_retries:
        try:
            sqs = boto3.client('sqs',
                   endpoint_url=AWS_CONFIG['endpoint_url'],
                   aws_access_key_id=pwd['aws_access_key_id'],
                   aws_secret_access_key=pwd['aws_secret_access_key'],
                   region_name=AWS_CONFIG['region_name'])

            response = sqs.list_queues()
            if response.get('QueueUrls') and queue_url in response['QueueUrls']:
                return True
            else:
                logging.warning(f"Queue not found on attempt {retries + 1}. Retrying in {retry_delay} seconds.")
                retries += 1
                time.sleep(retry_delay)

        except Exception as e:
            retries += 1
            #logging.error(f"Error checking SQS service. Retry {retries}/{max_retries}: {e}")
            time.sleep(retry_delay)

    # If all retries are exhausted and we haven't returned yet
    logging.error("All retries exhausted when checking SQS service.")
    return False



def main():
    queue_url = AWS_CONFIG['queue_url']
    cipher = AESCipher(password=pwd['aes_password'])
   
    total_extracted = 0
    total_transformed = 0
    total_loaded = 0
    while True:
        # Fetch a batch of messages.
        total_received, messages = fetch_from_sqs(queue_url)
        
        # If there are no messages, exit the loop.
        if not messages:
            break
        total_extracted += total_received

        for message in messages:
            data_str = message['Body']
            receipt_handle = message['ReceiptHandle'] # Extracting reciept_handle required to delete message once processed and inserted in the database
            try:
                #data = json.loads(data_str)
                transformed_data = mask_pii(data_str, cipher)

                if transformed_data:
                    total_transformed += 1
                    success = insert_to_postgres(transformed_data)
                    if success:
                        total_loaded += 1
                        delete_message_from_sqs(queue_url,receipt_handle)
                    

            except (json.JSONDecodeError, Exception) as e:  # Catching JSON errors and other exceptions.
                logging.error(f"Error processing message: {e}")

    logging.info(f"Total messages extracted: {total_extracted}")
    logging.info(f"Total messages transformed: {total_transformed}")
    logging.info(f"Total messages loaded: {total_loaded}")
    
    # Printing message counts to terminal
    print(f"Total messages extracted: {total_extracted}")
    print(f"Total messages transformed: {total_transformed}")
    print(f"Total messages loaded: {total_loaded}")
    print("Application run completed. Please check the log files for more information.")


if __name__ == "__main__":  
    try:
        queue_url = AWS_CONFIG['queue_url']
        if check_sqs_service(queue_url):
            main()
        else:
            print("Unable to access SQS service after retries or the queue is not visible. Please check logs for more details.")
    except Exception as e:
        print(f"An error occurred: {e}")
 

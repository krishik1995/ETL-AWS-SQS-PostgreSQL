from datetime import datetime
import psycopg2
import logging
import json
from db_config import DB_CONFIG
from general_config import GENERAL_CONFIG

# Load the JSON configuration
with open('pwd.json', 'r') as file:
    pwd = json.load(file)


def setup_logging():
    """Configures logging based on the general configuration."""
    logging.basicConfig(filename=GENERAL_CONFIG['filename'], level=logging.INFO)


def insert_to_postgres(data):
    """
    Insert transformed data into a PostgreSQL database.

    Args:
    - data (dict): The transformed data to insert.

    Returns:
    - bool: True if the insertion was successful, False otherwise.
    """
    try:
        with psycopg2.connect(dbname=DB_CONFIG['dbname'], user=pwd['db_user'], password=pwd['db_password'], host=DB_CONFIG['host'], port=DB_CONFIG['port']) as conn:
            with conn.cursor() as cursor:
                query = """
                    INSERT INTO user_logins(user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                # Handle app_version datatype
                major_version = None
                if "app_version" in data:
                    major_version = int(data["app_version"].split(".")[0])
                
                # Get the current date
                current_date = datetime.now().date()
                cursor.execute(query, (data["user_id"], data["device_type"], data["masked_ip"], data["masked_device_id"], data["locale"], major_version, current_date))
                conn.commit()
                
                return True  # Successful insertion
    except psycopg2.Error as e:
        logging.error(f"Database error while inserting into Postgres: {e.pgerror} . Full Message Structure: {data}")
        return False
    except ValueError as e:
        logging.warning(f"Data value error while processing: {e}. Full Message Structure: {data}")
        return False
    except Exception as e:
        logging.critical(f"Unexpected error while inserting data: {e}. Full Message Structure: {data}")
        return False
            


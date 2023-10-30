from encryption_utils import AESCipher
import logging
from general_config import GENERAL_CONFIG

# Setting up logging
logging.basicConfig(filename=GENERAL_CONFIG['filename'], level=logging.INFO)

def mask_pii(data, cipher):
    """
    Encrypt PII data for security.

    Args:
    - data (dict): The raw data containing PII.
    - cipher (AESCipher): An instance of AESCipher for encryption.

    Returns:
    - dict: The data with encrypted PII.
    """
    if "device_id" in data:
        try:
            encrypted_device_id = cipher.encrypt(data["device_id"])
            data["masked_device_id"] = encrypted_device_id
        except Exception as e:
            logging.warning(f"Error encrypting 'device_id': {e}")
            data["masked_device_id"] = None
    
    if "ip" in data:
        try:
            encrypted_ip = cipher.encrypt(data["ip"])
            data["masked_ip"] = encrypted_ip
        except Exception as e:
            logging.warning(f"Error encrypting 'ip': {e}")
            data["masked_ip"] = None
    
    return data

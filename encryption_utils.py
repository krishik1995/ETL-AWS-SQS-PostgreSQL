from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64

# A fixed salt for the key derivation function. Ensure this remains secure and constant!
FIXED_SALT = b'1234567890123456'

class AESCipher:
    """
    This class provides methods to encrypt and decrypt data using the AES algorithm.
    The encryption used here is symmetrical, which means the same key used for encryption 
    is used for decryption.
    """
    def __init__(self, password: str):
        """
        Initialize the AESCipher object.
        
        Args:
        - password (str): The password to be used for key derivation.
        """
        # Create a Key Derivation Function instance.
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=FIXED_SALT,
            iterations=100000,
            backend=default_backend()
        )
        
        # Derive a key using the provided password and the KDF.
        self.key = kdf.derive(password.encode())

    def encrypt(self, data: str) -> str:
        """
        Encrypt the provided data using AES encryption.
        
        Args:
        - data (str): The data to be encrypted.
        
        Returns:
        - str: The encrypted data, encoded in base64.
        """
        cipher = Cipher(algorithms.AES(self.key), modes.ECB(), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # Pad data to fit the block size.
        padded_data = data.ljust(16)
        
        # Encrypt the padded data.
        ct = encryptor.update(padded_data.encode()) + encryptor.finalize()
        
        # Return the encrypted data encoded as a base64 string (trimmed to a max length of 256 characters).
        return base64.b64encode(ct).decode('utf-8')[:256]

    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt the provided encrypted data.
        
        Args:
        - encrypted_data (str): The data to be decrypted, encoded in base64.
        
        Returns:
        - str: The decrypted data.
        """
        # Decode the encrypted data from base64.
        decoded_data = base64.b64decode(encrypted_data)
        
        cipher = Cipher(algorithms.AES(self.key), modes.ECB(), backend=default_backend())
        decryptor = cipher.decryptor()
        
        # Decrypt and return the data, removing any added padding.
        return decryptor.update(decoded_data).decode('utf-8').rstrip()


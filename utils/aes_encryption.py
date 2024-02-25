from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import hashlib

# Fungsi untuk medapatkan key dari plain text untuk digunakan di fungsi encrypt_data dan decrypt_data
def generate_key_from_password(password):
    # Konversi password ke byte
    password_bytes = password.encode('utf-8')
    # Gunakan fungsi hash SHA-256 untuk menghasilkan kunci
    hashed_key = hashlib.sha256(password_bytes).digest()
    return hashed_key

# Fungsi untuk melakukan encrypt data dari plain text
def encrypt_data(data, key):
    cipher = Cipher(algorithms.AES(key), modes.CFB(b'\0' * 16), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(data.encode()) + encryptor.finalize()
    return base64.b64encode(encrypted_data).decode()

# Fungsi untuk melakukan decrypt data ke plain text
def decrypt_data(encrypted_data, key):
    encrypted_data = base64.b64decode(encrypted_data.encode())
    cipher = Cipher(algorithms.AES(key), modes.CFB(b'\0' * 16), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
    return decrypted_data.decode()


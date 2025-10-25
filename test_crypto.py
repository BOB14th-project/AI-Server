"""
Test file with vulnerable cryptography for PQC Inspector testing
"""

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import hashlib

# Vulnerable RSA key generation
def generate_rsa_keypair():
    """Generate 2048-bit RSA key pair (quantum vulnerable)"""
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key

# Vulnerable encryption function
def encrypt_data(message, public_key):
    """Encrypt data using RSA (quantum vulnerable)"""
    rsa_key = RSA.import_key(public_key)
    cipher = PKCS1_OAEP.new(rsa_key)
    encrypted = cipher.encrypt(message.encode())
    return encrypted

# Korean SEED algorithm usage
def use_seed_cipher():
    """Using SEED-128 cipher (quantum vulnerable)"""
    # Simulated SEED usage
    config = {
        "cipher": "SEED-128-CBC",
        "key_size": 128
    }
    return config

if __name__ == "__main__":
    # Test RSA
    priv, pub = generate_rsa_keypair()
    print("RSA keys generated")

    # Test encryption
    msg = "Secret message"
    encrypted = encrypt_data(msg, pub)
    print(f"Encrypted: {encrypted.hex()[:50]}...")

    # Test SEED
    seed_config = use_seed_cipher()
    print(f"SEED config: {seed_config}")

"""Field-level encryption for parent contact details (Fernet = AES-128-CBC + HMAC)."""
import os

from cryptography.fernet import Fernet

_KEY = os.environ.get("USCIC_FERNET_KEY") or Fernet.generate_key().decode()
_f = Fernet(_KEY.encode())


def encrypt(value: str) -> str:
    return _f.encrypt(value.encode()).decode()


def decrypt(token: str) -> str:
    return _f.decrypt(token.encode()).decode()

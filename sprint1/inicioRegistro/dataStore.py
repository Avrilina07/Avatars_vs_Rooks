import os
import json
import base64
import hashlib
import hmac
from typing import Optional, Tuple
import logging

# Simple local data store for users in datos.json
# NOTE: This implements password hashing (PBKDF2) and a lightweight XOR-based
# encoding for the remaining user data so it isn't stored as plain JSON.
# This is NOT a replacement for proper encryption. If you want strong
# encryption, use a library such as 'cryptography' and store a real key.

BASE_DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(BASE_DIR, 'datos.json')

# Secret used for the simple XOR encoding; can be overridden with env var
SECRET_KEY = os.environ.get('APP_SECRET_KEY', 'dev-secret-change-me')

# Try to use cryptography.Fernet when available for proper encryption. If not,
# fall back to the lightweight XOR obfuscation implemented below.
try:
    from cryptography.fernet import Fernet
    _FERNET_AVAILABLE = True
except Exception:
    _FERNET_AVAILABLE = False

def _deriveKey() -> bytes:
    # Derive a fixed-length key from SECRET_KEY
    return hashlib.sha256(SECRET_KEY.encode('utf-8')).digest()

def _xorEncrypt(raw: bytes) -> str:
    key = _deriveKey()
    out = bytearray()
    for i, b in enumerate(raw):
        out.append(b ^ key[i % len(key)])
    return base64.b64encode(bytes(out)).decode('ascii')

def _xorDecrypt(b64: str) -> bytes:
    enc = base64.b64decode(b64)
    key = _deriveKey()
    out = bytearray()
    for i, b in enumerate(enc):
        out.append(b ^ key[i % len(key)])
    return bytes(out)


def _getFernet():
    if not _FERNET_AVAILABLE:
        return None
    # Derive a 32-byte key and urlsafe-base64 encode for Fernet
    key = hashlib.sha256(SECRET_KEY.encode('utf-8')).digest()
    fkey = base64.urlsafe_b64encode(key)
    return Fernet(fkey)


def _encryptBytes(raw: bytes) -> str:
    """Encrypt bytes and return a storable ASCII string."""
    f = _getFernet()
    if f is not None:
        try:
            return f.encrypt(raw).decode('ascii')
        except Exception:
            logging.exception('Fernet encryption failed, falling back to XOR')
    return _xorEncrypt(raw)


def _decryptBytes(stored: str) -> bytes:
    f = _getFernet()
    if f is not None:
        try:
            return f.decrypt(stored.encode('ascii'))
        except Exception:
            logging.exception('Fernet decryption failed, falling back to XOR')
    return _xorDecrypt(stored)

def _readAll() -> list:
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def _writeAll(data: list):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _hashPassword(password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
    if salt is None:
        salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 200_000)
    return salt, dk

def saveUser(username: str, password: str, other_data: dict) -> None:
    """Save a new user. Raises ValueError if username already exists."""
    users = _readAll()
    for u in users:
        if u.get('username') == username:
            raise ValueError('User already exists')

    salt, pw_hash = _hashPassword(password)
    enc = _encryptBytes(json.dumps(other_data, ensure_ascii=False).encode('utf-8'))
    record = {
        'username': username,
        'salt': salt.hex(),
        'pwHash': pw_hash.hex(),
        'data': enc
    }
    users.append(record)
    _writeAll(users)


def findUser(username: str) -> Optional[dict]:
    users = _readAll()
    for u in users:
        if u.get('username') == username:
            return u
    return None



def verifyUser(username: str, password: str) -> Tuple[bool, Optional[dict]]:
    """Verify credentials. Returns (True, other_data_dict) if OK, (False, None) otherwise."""
    rec = findUser(username)
    if not rec:
        return False, None
    try:
        salt = bytes.fromhex(rec.get('salt', ''))
        expected = bytes.fromhex(rec.get('pwHash', ''))
    except Exception:
        return False, None
    test_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 200_000)
    if hmac.compare_digest(test_hash, expected):
        try:
            raw = _decryptBytes(rec.get('data', ''))
            other = json.loads(raw.decode('utf-8'))
        except Exception:
            other = None
        return True, other
    return False, None


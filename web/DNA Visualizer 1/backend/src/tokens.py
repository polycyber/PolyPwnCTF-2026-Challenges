import jwt
from src.constants import *

def encode_token(payload: dict) -> str:
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def decode_token(encoded_jwt):
    if not encoded_jwt:
        print("No token provided to decode")
        return None
    decoded = jwt.decode(encoded_jwt, SECRET_KEY, algorithms=["HS256"])
    return decoded
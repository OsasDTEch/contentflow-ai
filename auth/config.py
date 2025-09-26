import os

import bcrypt
import hashlib
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()



SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS'))

pwd_context=CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
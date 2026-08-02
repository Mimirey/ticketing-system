from datetime import datetime,timedelta
from jose import jwt

import os
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORTHM = os.getenv("ALGORITHM")

def create_access_token(data: dict, expires_minutes: int = 60):
    payload= data.copy()
    expire= datetime.utcnow() + timedelta(minutes=expires_minutes)
    payload.update({"exp": expire})

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORTHM
    )
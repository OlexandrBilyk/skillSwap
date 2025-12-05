import jwt
from jwt import PyJWTError
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from fastapi.requests import Request
from fastapi import HTTPException, status

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGHORITM')

def create_access(data: dict):
    payload = data.copy()
    payload['exp'] = datetime.now() + timedelta(minutes=30)
    payload['type'] = 'access'
    return jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)

def create_refresh(data: dict):
    payload = data.copy()
    payload['exp'] = datetime.now() + timedelta(days=1)
    payload['type'] = 'refresh'
    return jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except PyJWTError:
        return None
    

def verify_user(req: Request):
    access = req.cookies.get('access_token')

    if access:
        payload = verify_token(access)

        if payload:
            return payload
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='UNAUTHORIZED')
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='UNAUTHORIZED')

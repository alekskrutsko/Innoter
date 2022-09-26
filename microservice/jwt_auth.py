import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from microservice.settings import settings

security = HTTPBearer()


async def has_access(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Function that is used to validate the token in the case that it requires it"""

    token = credentials.credentials

    try:
        payload = jwt.decode(token, key=settings.SECRET_KEY)
    except jwt.DecodeError as e:
        raise HTTPException(status_code=401, detail=str(e))

    return payload["id"]

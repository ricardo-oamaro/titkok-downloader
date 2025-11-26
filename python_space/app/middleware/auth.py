from fastapi import Header, HTTPException, status
from typing import Annotated
from app.config import settings


async def verify_api_key(x_api_key: Annotated[str | None, Header()] = None):
    """
    Verify API key from request header
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing"
        )
    
    if x_api_key not in settings.api_keys_list:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return x_api_key




import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from api.database import get_db
from api.config import get_settings
from api.models import MemberInfo

settings = get_settings()

# Tells FastAPI where the frontend should send the login request
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> MemberInfo:
    """Decodes the JWT and fetches the user from the database."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        member_id: str = payload.get("sub")
        if member_id is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
        
    user = db.get(MemberInfo, int(member_id))
    if user is None:
        raise credentials_exception
        
    return user


def require_admin_role(current_user: MemberInfo = Depends(get_current_user)) -> MemberInfo:
    """Blocks the request if the user is a regular member. Allows Admins and Masters."""
    # Notice we use `not in` to allow the master role to slip through the admin door!
    if current_user.role not in ["admin", "master"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Admin privileges required."
        )
    return current_user

def require_master_role(current_user: MemberInfo = Depends(get_current_user)) -> MemberInfo:
    """The Ultimate Lock: Blocks absolutely everyone except the Master."""
    if current_user.role != "master":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Master System privileges required. Access Denied."
        )
    return current_user
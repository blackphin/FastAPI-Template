# database Imports
from datetime import datetime, timedelta

# FastAPI Imports
from fastapi import Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

# Jose Imports (JWT)
from jose import JWTError, jwt
from pydantic import EmailStr

# Database Imports
from app.database import database
from app.database.tables.table_blacklist_tokens import BlacklistTokens
from app.database.tables.table_users import Users

# Auth Services
from app.routers.auth import schemas
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


def verify_user(user_email: EmailStr, scope: str):
    db = database.SessionLocal()

    user_details = db.query(Users.status, Users.user_id, Users.scopes).filter(
        Users.email == user_email).first()

    if user_details is None:
        return None

    elif user_details.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User set as inactive',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    elif scope not in user_details.scopes:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User does not have required role',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    db.close()

    return user_details


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_access_token(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)):
    db = database.SessionLocal()

    # Check if token is blacklisted
    db_token = db.query(BlacklistTokens).filter(
        BlacklistTokens.token == token).first()
    if db_token is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Logged Out Token", headers={"WWW-Authenticate": "Bearer"}
        )

    # Check if token scope is valid
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate credentials",
                            headers={"WWW-Authenticate": authenticate_value},)

    # Decode Token
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        # Token Data
        token_data = schemas.TokenData(
            token=token,
            user_id=payload.get("user_id"),
            scopes=payload.get("scopes", []),
            exp=payload.get("exp")
        )

    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Couldn't Verify JWT", headers={"WWW-Authenticate": "Bearer"}
        ) from exc

    # Verify Token Role
    for scope in token_data.scopes:
        if scope not in security_scopes.scopes:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Not enough permissions",
                                headers={"WWW-Authenticate": authenticate_value},)

    # Verify User from DB
    user = db.query(Users).filter(Users.user_id == token_data.user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found", headers={"WWW-Authenticate": "Bearer"}
        )

    db.close()

    return token_data


def get_current_user(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)):
    return verify_access_token(security_scopes, token).user_id

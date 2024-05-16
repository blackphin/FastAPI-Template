# FastAPI Imports
from fastapi import APIRouter, Depends, HTTPException, Request, Security, status
# from fastapi.responses import RedirectResponse

# Auth Imports
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.config import Config

# Database Imports
from sqlalchemy.orm import Session
from database.database import get_db
from database.tables.table_users import Users
from database.tables.table_blacklist_tokens import BlacklistTokens

# Auth Services
from . import schemas
from config import settings
from routers.auth.services import create_access_token, verify_access_token, verify_user

router = APIRouter(tags=['Authentication'], prefix='/auth')

# AuthLib Config
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')
config_data = {'GOOGLE_CLIENT_ID': settings.google_client_id,
               'GOOGLE_CLIENT_SECRET': settings.google_client_secret}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)


# Health Check
@router.get("/healthcheck", status_code=status.HTTP_200_OK)
def current_status():
    return {"status": "Auth Layer Active"}


# Login Route
@router.get('/login/{scope}')
async def login(request: Request, scope: str):
    redirect_uri = str(settings.redirect_url+scope)
    return await oauth.google.authorize_redirect(request, redirect_uri)


# Redirect Route
@router.get("/jwt/{scope}", response_model=schemas.Token)
async def jwt(request: Request, scope: str):
    # Decrypt Google Token
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate Authentication Token',
            headers={'WWW-Authenticate': 'Bearer'},
        ) from exc

    # Verify Google Email with DB
    user_email = token['userinfo']['email']

    user_details = verify_user(user_email, scope)

    if user_details is None:
        return RedirectResponse(
            url="https://www.google.com",
            # url="http://127.0.0.1:8000/api/auth/create_user",
            status_code=status.HTTP_302_FOUND,
            headers={"x-error": "Invalid credentials"}
        )

    access_token = create_access_token(
        data={"user_id": user_details.user_id, "scopes": [scope]}
    )

    return {"access_token": access_token, "token_type": "bearer", "scopes": [scope]}


# Logout Route
@router.get("/logout")
def logout(token_data: schemas.TokenData = Security(verify_access_token, scopes=['admin', 'user']), db: Session = Depends(get_db)):
    # token_data = verify_access_token(role, token)
    exp_time = token_data.exp
    log = BlacklistTokens(token=token_data.token, expiration=exp_time)
    db.add(log)
    db.commit()
    return {"status": "Logged out successfully"}


# Create User
@router.post('/create_user')
async def create_user(user_details: schemas.CreateUser, request: Request, db: Session = Depends(get_db)):
    # Decrypt Google Token
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate Authentication Token',
            headers={'WWW-Authenticate': 'Bearer'},
        ) from exc

    user_email = token['userinfo']['email']

    if db.query(Users).filter_by(email=user_email).first() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    new_user = Users(emp_no=user_details.user_id, name=user_details.name, email=user_email,
                     dept=user_details.dept)
    db.add(new_user)
    db.commit()

    access_token = create_access_token(
        data={"emp_no": user_details.user_id, "scopes": ['user']}
    )

    return {"status": "User created successfully", "access_token": access_token, "token_type": "bearer", "scopes": ['user']}

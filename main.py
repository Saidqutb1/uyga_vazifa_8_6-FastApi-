from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
import crud, models, schemas, utils
from database import SessionLocal, engine
from dependencies import get_db, get_current_user, add_token_to_blacklist
from datetime import timedelta
from fastapi.middleware.cors import CORSMiddleware
import logging

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Настройка CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Определение OAuth2 схемы
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/signup/", response_model=schemas.User)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    logger.info("Signup attempt for user: %s", user.username)
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info("Login attempt for user: %s", form_data.username)
    user = crud.authenticate_user(db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=utils.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = utils.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/password-reset-request/")
def password_reset_request(password_reset_request: schemas.PasswordResetRequest, db: Session = Depends(get_db)):
    logger.info("Password reset request for email: %s", password_reset_request.email)
    user = crud.get_user_by_email(db, email=password_reset_request.email)
    if not user:
        raise HTTPException(status_code=400, detail="Email not registered")
    reset_token = crud.create_reset_token(user)
    # Здесь вы бы отправили reset_token на email пользователя
    # Для примера возвращаем его напрямую
    return {"reset_token": reset_token}

@app.post("/password-reset-confirm/")
def password_reset_confirm(password_reset_confirm: schemas.PasswordResetConfirm, db: Session = Depends(get_db)):
    logger.info("Password reset confirm attempt")
    success = crud.reset_password(db, token=password_reset_confirm.reset_token, new_password=password_reset_confirm.new_password)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid token or token expired")
    return {"msg": "Password reset successful"}

@app.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    logger.info("Fetching current user data")
    return current_user

@app.post("/logout/")
def logout(current_user: schemas.User = Depends(get_current_user), token: str = Depends(oauth2_scheme)):
    add_token_to_blacklist(token)
    logger.info("Logout attempt for user: %s", current_user.username)
    return {"msg": "Logout successful"}

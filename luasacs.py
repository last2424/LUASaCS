import phonenumbers, psycopg2, bcrypt, secrets
from tabnanny import check
from pydantic import BaseModel
from fastapi import Depends, FastAPI, Header, Request, Response, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from email_validator import validate_email, EmailNotValidError
from app.core.db import *
from app.core.auth import *
from app.core.api import *
from app.core.config import *
from app.models.sqlmodels import *
from multiprocessing import Process

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def verify_superadmin_token(superadmin_token: str):
    if superadmin_token != SUPERADMIN_TOKEN:
        return {"status": "Permissions denied"}

async def verify_app_key(appuid: str = Form(), app_key: str = Form()):
    custom_app = await get_app(appuid=appuid)
    v = await verify_app(custom_app.secret_token, app_key)
    if v is False:
        return HTTPException(status_code=400, detail="App key is invalid")


@app.get("/install")
async def install():
    await create_db_and_tables()
    return {"Hello": "World"}

@app.post("/verify_cookie", dependencies=[Depends(verify_app_key)])
async def verify_cookie_auth(request: Request):
    if request.cookies.get("auth_token"):
        data = decode_access_token(str(request.cookies.get("auth_token")))
        if data:
            return True
    return False

@app.post("/verify_bearer", dependencies=[Depends(verify_app_key)])
async def verify_bearer_auth(auth_token: str = Header()):
    data = decode_access_token(auth_token)
    if data:
        return True
    return False

@app.post("/add_user", dependencies=[Depends(verify_app_key)])
async def add_user(username: str, email: str, phone: str, password: str, superadmin_token: str):
    await create_user(User(username=username, email=email, phone=phone, password=hash_password(password)))
    return {"status": "ok"}

@app.post("/add_user_superadmin", dependencies=[Depends(verify_superadmin_token)])
async def add_user_superadmin(username: str, email: str, phone: str, password: str, superadmin_token: str):
    await create_user(User(username=username, email=email, phone=phone, password=hash_password(password)))
    return {"status": "ok"}

@app.post("/add_app", dependencies=[Depends(verify_superadmin_token)])
async def add_app(appname: str, superadmin_token: str):
    appuid = secrets.token_hex(8)
    keys = await generate_key()
    await create_app(App(appname=appname, appuid=appuid, secret_token=keys["private_key"]))
    return {"status": "ok", "appuid": appuid, "public_key": keys["public_key"]}

@app.post("/auth", dependencies=[Depends(verify_app_key)])
async def auth(request: Request, login: str = Form(), password: str = Form(), redirect: Union[str, None] = "/main", user_agent: Union[str, None] = Header(default=None)):
    auth_data = {"type": "username", "status": -1, "user_agent": user_agent, "ip": request.client.host, "redirect": redirect}
    if len(login) == 0 or len(password) == 0:
        auth_data["status"] = 1
        return auth_data
    
    email_validation = await check_email(login)
    phone_validation = await check_phone(login)
    if email_validation is not False:
        auth_data["type"] = "email"

    if phone_validation is not False:
        auth_data["type"] = "phone"

    try:
        user = await get_user(login)
        if user:
            if verify_password(password, user.password):
                auth_data["status"] = 0
                auth_data["auth_token"] = create_refresh_token(user.email, request.client.host, user_agent)
            else:
                auth_data["status"] = 7
        else:
            auth_data["status"] = 8
    except Exception as e:
        print(e)
        auth_data["status"] = 9

    return JSONResponse(auth_data)

@app.post("/get_user_by_jwt", dependencies=[Depends(verify_app_key)])
async def get_user_by_jwt(request: Request):
    if request.cookies.get("auth_token"):
        data = decode_access_token(str(request.cookies.get("auth_token")))
        email = json.loads(data['sub'])['email']
        user = await get_user(email)
        return JSONResponse({"id": user.id, "email": user.email, "phone": user.phone, "username": user.username})

async def check_email(email: str):
    try:
        return validate_email(email)
    except:
        return False

async def check_phone(phone: str):
    try:
        return phonenumbers.parse(phone, "RU")
    except:
        return False
import phonenumbers, psycopg2, bcrypt
from tabnanny import check
from pydantic import BaseModel
from fastapi import Depends, FastAPI, Header, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from email_validator import validate_email, EmailNotValidError
from app.core.db import *
from app.core.auth import *
from app.models.sqlmodels import *

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

class AuthData(BaseModel):
    login: str
    password: str
    redirect: Union[str, None] = "/main"

async def verify_cookie_auth(request: Request):
    if request.cookies.get("auth_token"):
        data = decode_access_token(str(request.cookies['auth_token']))
        if data:
            return HTTPException(status_code=200)
    return RedirectResponse("/")


async def verify_bearer_auth(auth_token: str = Header()):
    data = decode_access_token(auth_token)
    if data:
        return HTTPException(status_code=200)
    raise HTTPException(status_code=400, detail="Auth Token invalid")

@app.get("/")
async def read_root(request: Request):
    if request.cookies.get("auth_token"):
        return RedirectResponse("/main")
    return templates.TemplateResponse("main.html", headers={"Cache-Control": "no-cache, no-store, must-revalidate"}, context={"request": request})

@app.get("/main", dependencies=[Depends(verify_cookie_auth)])
async def read_main(request: Request):
    return templates.TemplateResponse("main.html", headers={"Cache-Control": "no-cache, no-store, must-revalidate"}, context={"request": request})

@app.get("/install")
async def install():
    await create_db_and_tables()
    return {"Hello": "World"}

@app.post("/add_user")
async def add_user(username: str, email: str, phone: str, password: str):
    await create_user(User(username=username, email=email, phone=phone, password=hash_password(password)))
    return {"status": "ok"}

@app.post("/auth")
async def auth(authData: AuthData, request: Request, user_agent: Union[str, None] = Header(default=None)):
    auth_data = {"type": "username", "status": -1, "user_agent": user_agent, "ip": request.client.host, "redirect": authData.redirect}
    if len(authData.login) == 0 or len(authData.password) == 0:
        auth_data["status"] = 1
        return auth_data
    
    email_validation = await check_email(authData.login)
    phone_validation = await check_phone(authData.login)
    if email_validation is not False:
        auth_data["type"] = "email"

    if phone_validation is not False:
        auth_data["type"] = "phone"

    try:
        user = await get_user(authData.login)
        if user:
            if verify_password(authData.password, user.password):
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
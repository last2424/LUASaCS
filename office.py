import phonenumbers, psycopg2, bcrypt, secrets, requests, json
from tabnanny import check
from pydantic import BaseModel
from fastapi import Depends, FastAPI, Header, Request, Response
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

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

appuid = "2e5c884eef5aea69"
app_secret = "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC5E6oKBUSmQxI7HEEsV9xxo8VM\nQkY8lOLs1bexuA6e86X/5XMcAu0Ab53xFfRVq+g3e/K0fGIuACkvEtvUlAc2Nfgp\nCE4TgU1tZ/1WQq/l9H9PFlOPpA2GiS0WCkELLOjgu37/F/lJNKXOUuNPV+Fq5AOY\nLacchIv3q05YpaBkxwIDAQAB\n-----END PUBLIC KEY-----"

class AuthData(BaseModel):
    login: str
    password: str
    redirect: Union[str, None] = "/main"

async def verify_cookie_auth(request: Request):
    r = requests.post('http://127.0.0.1:5001/verify_cookie', data={'auth_token': request.cookies.get("auth_token"), 'appuid': appuid, 'app_key': app_secret}, headers=request.headers, cookies=request.cookies)
    if r.json():
        return HTTPException(status_code=200)
    return RedirectResponse("/")


async def verify_bearer_auth(request: Request):
    r = requests.post('http://127.0.0.1:5001/verify_bearer', data={'appuid': appuid, 'app_key': app_secret}, headers=request.headers, cookies=request.cookies)
    if r.json():
        return HTTPException(status_code=200)
    raise HTTPException(status_code=400, detail="Auth Token invalid")

@app.get("/")
async def read_root(request: Request):
    if request.cookies.get("auth_token"):
        return RedirectResponse("/main")
    return templates.TemplateResponse("main.html", headers={"Cache-Control": "no-cache, no-store, must-revalidate"}, context={"request": request})

@app.get("/main", dependencies=[Depends(verify_cookie_auth)])
async def read_main(request: Request):
    return templates.TemplateResponse("cabinet.html", headers={"Cache-Control": "no-cache, no-store, must-revalidate"}, context={"request": request})

@app.post("/auth")
async def office_auth(authData: AuthData, request: Request, user_agent: Union[str, None] = Header(default=None)):
    r = requests.post('http://127.0.0.1:5001/auth', json={'login': authData.login, 'password': authData.password, 'redirect': '/main', 'user_agent': user_agent, 'appuid': appuid, 'app_key': app_secret})
    return r.json()
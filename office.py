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
from app.models.officesqlmodels import *
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

async def verify_cookie_auth(request: Request) -> Response:
    r = requests.post('http://127.0.0.1:5001/verify_cookie', data={'appuid': appuid, 'app_key': app_secret}, headers=request.headers, cookies=request.cookies)
    if r.json() is True:
        return HTTPException(status_code=200)
    raise HTTPException(status_code=302, detail="Not authorized", headers = {"Location": "/"} )

async def verify_bearer_auth(request: Request):
    r = requests.post('http://127.0.0.1:5001/verify_bearer', data={'appuid': appuid, 'app_key': app_secret}, headers=request.headers, cookies=request.cookies)
    if r.json() is True:
        return HTTPException(status_code=200)
    raise HTTPException(status_code=400, detail="Auth Token invalid")

@app.get("/")
async def read_root(request: Request):
    if request.cookies.get("auth_token"):
        return RedirectResponse("/main")
    return templates.TemplateResponse("main.html", headers={"Cache-Control": "no-cache, no-store, must-revalidate"}, context={"request": request})

@app.get("/main", dependencies=[Depends(verify_cookie_auth)])
async def read_main(request: Request):
    r = requests.post('http://127.0.0.1:5001/get_user_by_jwt', data={'appuid': appuid, 'app_key': app_secret}, cookies=request.cookies)
    res = r.json()
    user = await get_user(res['id'])
    if user:
        permissions = await get_permissions(res['id'])
        return templates.TemplateResponse("cabinet.html", headers={"Cache-Control": "no-cache, no-store, must-revalidate"}, context={"request": request, "username": res['username'], "email": res['email'], "phone": res['phone'], "firstname": user.firstname, "lastname": user.lastname, "fathername": user.fathername, "permissions": permissions})
    return templates.TemplateResponse("cabinet.html", headers={"Cache-Control": "no-cache, no-store, must-revalidate"}, context={"request": request, "username": res['username'], "email": res['email'], "phone": res['phone'], "firstname": None, "lastname": None, "fathername": None, "permissions": None})
    
@app.get("/rm_support", dependencies=[Depends(verify_cookie_auth)])
async def read_rm_support(request: Request):
    return templates.TemplateResponse("module1.html", headers={"Cache-Control": "no-cache, no-store, must-revalidate"}, context={"request": request})

@app.post("/auth")
async def office_auth(authData: AuthData, request: Request, user_agent: Union[str, None] = Header(default=None)):
    r = requests.post('http://127.0.0.1:5001/auth', data={'appuid': appuid, 'app_key': app_secret, 'login': authData.login, 'password': authData.password, 'redirect': '/main', 'user_agent': user_agent})
    return r.json()

@app.post("/fb_auth", dependencies=[Depends(verify_cookie_auth)])
async def filebrowser_check_auth(request: Request):
    return {"status": True}

@app.post("/fb_admin", dependencies=[Depends(verify_cookie_auth)])
async def filebrowser_check_admin(request: Request):
    return {"is_admin": await check_admin(request, "fb")}

@app.post("/fb_edit", dependencies=[Depends(verify_cookie_auth)])
async def filebrowser_check_editor(request: Request):
    return {"is_edit": await check_edit(request, "fb")}


async def check_admin(request: Request, sub: str = "access"):
    r = requests.post('http://127.0.0.1:5001/get_user_by_jwt', data={'appuid': appuid, 'app_key': app_secret}, cookies=request.cookies)
    res = r.json()
    is_admin = await is_permission(res['id'], "permission.{sub}.admin")
    return is_admin

async def check_edit(request: Request, sub: str = "access"):
    r = requests.post('http://127.0.0.1:5001/get_user_by_jwt', data={'appuid': appuid, 'app_key': app_secret}, cookies=request.cookies)
    res = r.json()
    is_edit = await is_permission(res['id'], "permission.{sub}.edit")
    return is_edit

@app.get("/install")
async def install():
    await create_db_and_tables()
    return {"Hello": "World"}

@app.post("/add_user")
async def add_user(uid: int, firstname: str, lastname: str, fathername: str):
    await create_user(OfficeUser(uid=uid, firstname=firstname, lastname=lastname, fathername=fathername))
    return {"status": "ok"}
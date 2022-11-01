import phonenumbers, psycopg2, bcrypt
from tabnanny import check
from fastapi import FastAPI, Header, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from email_validator import validate_email, EmailNotValidError
from app.core.db import *
from app.core.auth import *
from app.models.sqlmodels import *

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

#async def login_required(f):
#	def wrapped(*args, **kwargs):
#		if 'authorised' not in session:
#			return render_template('login.html')
#		return f(*args, **kwargs)
#	return wrapped

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("main.html", headers={"Cache-Control": "no-cache, no-store, must-revalidate"}, context={"request": request})

@app.get("/install")
async def install():
    await create_db_and_tables()
    return {"Hello": "World"}

@app.post("/auth")
async def auth(login: str, password: str, request: Request, user_agent: Union[str, None] = Header(default=None)):
    auth_data = {"type": "username", "status": -1, "user_agent": user_agent, "ip": request.client.host}
    
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
        if user and len(user) > 0:
            if hash_password(password, data[4]):
                auth_data["status"] == 0
                auth_data["auth_token"] = create_refresh_token(user.email, request.client.host, user_agent)
    except Exception as e:
        auth_data["status"] == 9

    return auth_data

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
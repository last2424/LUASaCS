import phonenumbers, psycopg2, bcrypt
from tabnanny import check
from fastapi import FastAPI
from email_validator import validate_email, EmailNotValidError
from db import *

app = FastAPI()

#async def login_required(f):
#	def wrapped(*args, **kwargs):
#		if 'authorised' not in session:
#			return render_template('login.html')
#		return f(*args, **kwargs)
#	return wrapped

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/auth")
async def auth(login: str, password: str):
    auth_data = {"type": "username", "status": -1}
    print(login)
    email_validation = await check_email(login)
    phone_validation = await check_phone(login)
    
    if email_validation is not False:
        auth_data["type"] = "email"

    if phone_validation is not False:
        auth_data["type"] = "phone"

    try:
        data = fetch_one(psycopg2, "users", auth_data["type"], login)

        if data and len(data) > 0:
            if check_password(password, data[4]):
                auth_data["status"] == 0
                auth_data["auth_token"] = "none"
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

async def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password.encode('utf8'), hashed_password.encode('utf8'))
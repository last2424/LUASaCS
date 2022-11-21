from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine, select, or_

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    phone: str
    password: str

class App(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    appname: str
    appuid: str
    secret_token: str

postgre_url = f"postgresql://postgres:123@localhost/luas"

engine = create_engine(postgre_url, echo=True)

async def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

async def create_user(user: User):
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)

async def create_app(app: App):
    with Session(engine) as session:
        session.add(app)
        session.commit()
        session.refresh(app)

async def get_user(login: str):
    with Session(engine) as session:
        statement = select(User).where(or_(User.username == login, User.email == login, User.phone == login))
        user = session.exec(statement).first()
        return user

async def get_app(appuid: str):
    with Session(engine) as session:
        statement = select(App).where(App.appuid == appuid)
        app = session.exec(statement).first()
        return app   
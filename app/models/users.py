from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    phone: str
    password: str

postgre_url = f"postgresql://postgres:123@localhost/luas"

engine = create_engine(postgre_url, echo=True)

async def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

async def create_user(user: User):
    with Session(engine) as session:
        session.add(user)
        await session.commit()
        await session.refresh(user)
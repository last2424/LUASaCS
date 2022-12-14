from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine, select, or_

class OfficeUser(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    uid: int
    firstname: str
    lastname: str
    fathername: str

class Permission(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    per_name: str
    per_enabled: bool
    per_local: str

postgre_url = f"postgresql://postgres:123@localhost/office"

engine = create_engine(postgre_url, echo=True)

async def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

async def create_user(user: OfficeUser):
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)

async def create_permission(permission: Permission):
    with Session(engine) as session:
        session.add(permission)
        session.commit()
        session.refresh(permission)

async def get_user(uid: int):
    with Session(engine) as session:
        statement = select(OfficeUser).where(OfficeUser.uid == uid)
        user = session.exec(statement).first()
        return user

async def get_permissions(user_id: int):
    with Session(engine) as session:
        statement = select(Permission).where(Permission.user_id == user_id)
        permissions = session.exec(statement)
        return permissions

async def is_permission(user_id: int, per_name: str):
    with Session(engine) as session:
        statement = select(Permission).where(Permission.user_id == user_id, Permission.per_name == per_name)
        permission = session.exec(statement).first()
        if permission:
            return permission.per_enabled
        return False
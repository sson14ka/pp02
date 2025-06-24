import datetime

from sqlalchemy import create_engine, Column, Integer, VARCHAR, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import declarative_base, mapped_column, Mapped


engine = create_engine('postgresql+psycopg2://postgres:password@localhost:5432/docsystem')
engine.connect()
print(engine)

Base = declarative_base()

class RolesORM(Base):
    __tablename__ = 'roles'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

class UsersORM(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    name: Mapped[str]
    surname: Mapped[str]
    patronymic: Mapped[str | None]
    email: Mapped[str] = mapped_column(unique=True)
    hash_password: Mapped[str]
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"))

class DocumentsORM(Base):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    title: Mapped[str]
    category: Mapped[str]
    cration_date: Mapped[datetime.datetime]
    security_level: Mapped[int]
    file_path: Mapped[str]
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
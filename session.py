from sqlalchemy.orm import sessionmaker
from orm import engine
from orm import UsersORM, RolesORM
import bcrypt

Session = sessionmaker(bind=engine)
session = Session()

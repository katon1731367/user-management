from database import Base, engine
from sqlalchemy import Column, Integer, String, DateTime, LargeBinary
from sqlalchemy import MetaData, Table
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from datetime import datetime

# Model users untuk menampung data user
class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    full_name = Column(String)
    password = Column(String, nullable=True)
    phone_number = Column(String)

# Model Task  untuk menampung data Task yang dimiliki oleh user
class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    title = Column(String(120), nullable=False)
    encrypted_description = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('Users', backref='tasks')

metadata = MetaData()
# Model log untuk menampung data log
logs_table = Table(
    'logs',
    metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('operation', String),
    Column('data', String),
    Column('timestamp', DateTime, default=datetime.utcnow())
)
metadata.create_all(engine)



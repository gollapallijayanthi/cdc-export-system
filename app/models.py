from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, String, Boolean, TIMESTAMP

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    name = Column(String)
    email = Column(String)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    is_deleted = Column(Boolean)
from sqlalchemy import String, TIMESTAMP

class Watermark(Base):
    __tablename__ = "watermarks"

    consumer_id = Column(String, primary_key=True)
    last_exported_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
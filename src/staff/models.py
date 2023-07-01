from database import Base, metadata
from sqlalchemy import Integer, Column, String


class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True)
    name = Column("name", String(100), nullable=False, unique=True)

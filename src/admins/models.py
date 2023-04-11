from src.database import Base
from sqlalchemy import Integer, Column, String, Table
from src.database import metadata


class Section(Base):
    __tablename__ = "sections"
    id = Column(Integer, primary_key=True)
    name = Column("name", String(100), nullable=False)



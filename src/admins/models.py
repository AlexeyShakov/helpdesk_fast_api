from database import Base, metadata
from sqlalchemy import Integer, Column, String


class Section(Base):
    __tablename__ = "sections"
    id = Column(Integer, primary_key=True)
    name = Column("name", String(100), nullable=False)



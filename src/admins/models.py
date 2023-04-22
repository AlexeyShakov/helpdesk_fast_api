from database import Base, metadata
from sqlalchemy import Integer, Column, String, ForeignKey
from sqlalchemy.orm import relationship


class Section(Base):
    __tablename__ = "sections"
    id = Column(Integer, primary_key=True)
    name = Column("name", String(100), nullable=False)

    topics = relationship("Topic", back_populates="section")

class Topic(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True)
    name = Column("name", String(100), nullable=False)
    section_id = Column(Integer, ForeignKey("sections.id"))

    section = relationship("Section", back_populates="topics", lazy="joined")




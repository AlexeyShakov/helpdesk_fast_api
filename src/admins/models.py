from database import Base, metadata
from sqlalchemy import Integer, Column, String, ForeignKey, Boolean, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy_utils import ChoiceType
import enum


class TemplateFieldChoices(enum.Enum):
    SELECT = "select"
    STRING = "string"


class Topic(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True)
    name = Column("name", String(100), nullable=False)
    # Для связи один ко многим
    categories = relationship("Category", back_populates="topic")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column("name", String(100), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)

    topic = relationship("Topic", back_populates="categories", lazy="joined")


"""
У одного шаблона может быть несколько полей. Следовательно, в объекте поля мы должны сделать ссылку на объект шаблона
"""

class Template(Base):
    __tablename__ = "templates"
    id = Column(Integer, primary_key=True)
    name = Column("name", String(100), nullable=False)

    # template_fields = relationship("TemplateField", back_populates="template")


class TemplateField(Base):
    __tablename__ = "template_fields"
    id = Column(Integer, primary_key=True)
    queue_index = Column("queue_index", Integer, nullable=False)
    name = Column("name", String(150), nullable=False)
    required = Column("required", Boolean, nullable=False)
    type = Column(Enum(TemplateFieldChoices), nullable=False)
    data = Column(JSON, nullable=True)
    # template_id = Column(Integer, ForeignKey("templates.id"))
    #
    # template = relationship("Template", back_populates="template_fields", lazy="joined")


from admins.enums import TemplateFieldChoices
from database import Base, metadata
from sqlalchemy import Integer, Column, String, ForeignKey, Boolean, Enum, JSON
from sqlalchemy.orm import relationship


class Topic(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True)
    name = Column("name", String(100), nullable=False)
    # Для связи один ко многим
    categories = relationship("Category", back_populates="topic")


class Template(Base):
    __tablename__ = "templates"
    id = Column(Integer, primary_key=True)
    name = Column("name", String(100), nullable=False)

    categories = relationship("Category", back_populates="template")
    template_fields = relationship("TemplateField", cascade="all,delete", back_populates="template")


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column("name", String(100), nullable=False)
    time_of_life = Column(JSON, nullable=False)
    notification_repeat = Column(JSON, nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=True)

    template = relationship("Template", back_populates="categories", lazy="joined")
    topic = relationship("Topic", back_populates="categories", lazy="joined")


class TemplateField(Base):
    __tablename__ = "template_fields"
    id = Column(Integer, primary_key=True)
    queue_index = Column("queue_index", Integer, nullable=False)
    name = Column("name", String(150), nullable=False)
    required = Column("required", Boolean, nullable=False)
    type = Column(Enum(TemplateFieldChoices), nullable=False)
    data = Column(JSON, nullable=True)
    template_id = Column(Integer, ForeignKey("templates.id"))

    template = relationship("Template", back_populates="template_fields", lazy="joined")
    template_field_answers = relationship("TemplateFieldAnswer", cascade="all,delete", back_populates="template_field")


class TemplateFieldAnswer(Base):
    __tablename__ = "template_field_answers"
    id = Column(Integer, primary_key=True)
    label = Column(String(200), nullable=False)
    value = Column(JSON)
    template_field_id = Column(Integer, ForeignKey("template_fields.id"))

    template_field = relationship("TemplateField", back_populates="template_field_answers", lazy="joined")




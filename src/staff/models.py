from sqlalchemy.orm import relationship

from database import Base, metadata
from sqlalchemy import Integer, Column, String, ForeignKey, Enum

from staff.enums import UserRoleChoices


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    name = Column("name", String(100), nullable=False, unique=True)
    users = relationship("User", back_populates="group")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column("username", String(200), nullable=False, unique=True)
    last_name = Column("last_name", String(200), nullable=False)
    first_name = Column("first_name", String(200), nullable=False)
    surname = Column("surname", String(200), nullable=False)
    phone = Column("phone", String(200), nullable=False, unique=True)
    email = Column("email", String(200), nullable=False, unique=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    role = Column(Enum(UserRoleChoices), nullable=True)

    # This field corresponds to the id from the main service
    main_id = Column(Integer, nullable=False)

    group = relationship("Group", back_populates="users", lazy="joined")

    # I have to link Category and User with foreign key here. So User might be stuff only in one category, or it's
    # a user who uses helpdesk(category == None)

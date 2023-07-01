import datetime

from sqlalchemy.orm import relationship

from database import Base, metadata
from sqlalchemy import Integer, Column, String, ForeignKey, Enum, Text, DateTime, Boolean

from tickets.enums import TicketStatusChoice, GradeChoice


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True)
    status = Column(Enum(TicketStatusChoice), nullable=False, default=TicketStatusChoice.NEW)
    grade = Column(Enum(GradeChoice), nullable=True, default=None)
    title = Column("title", String(200), nullable=False)
    description = Column(Text, nullable=False)
    created = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, nullable=True, default=None)
    in_work_date = Column(DateTime, nullable=True, default=None)
    closed_date = Column(DateTime, nullable=True, default=None)
    is_overdue = Column(Boolean, default=False)
    # answers
    # files

    specialist_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    specialist = relationship("User", lazy="joined", foreign_keys=[specialist_id])
    creator = relationship("User", lazy="joined", foreign_keys=[creator_id])
    category = relationship("Category", back_populates="tickets", lazy="joined")
    topic = relationship("Topic", back_populates="tickets", lazy="joined")

from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from db.base import Base

team_members = Table(
    "team_members",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("team_id", Integer, ForeignKey("teams.id"), primary_key=True),
)

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    guild_id = Column(String, nullable=False)
    channel_id = Column(String, nullable=True)  # The configured team channel
    leader_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Team Leader

    # Relationships
    leader = relationship("User", back_populates="led_teams", foreign_keys=[leader_id])
    members = relationship("User", secondary=team_members, back_populates="teams")  # Many-to-Many
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from db.base import Base
from db.models.team import team_members


user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    emp_id = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    guild_id = Column(String, nullable=True)

    # Relationships
    teams = relationship("Team", secondary=team_members, back_populates="members")  # Many-to-Many
    led_teams = relationship("Team", back_populates="leader", foreign_keys="Team.leader_id")
    manager = relationship("User", remote_side=[id], back_populates="subordinates", foreign_keys=[manager_id])
    subordinates = relationship("User", back_populates="manager", foreign_keys=[manager_id])
    
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    rewards = relationship("Reward", back_populates="user", cascade="all, delete-orphan")
    reward_transactions = relationship("RewardTransaction", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

# User.led_team = relationship('Team', back_populates='leader', uselist=False, foreign_keys=[Team.leader_id])
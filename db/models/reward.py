from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum as SqlEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from db.base import Base

class RewardReason(str, Enum):
    TASK_COMPLETION = 'Task Completion'
    STREAK_BONUS = 'Streak Bonus'
    MANAGER_AWARD = 'Manager Award'
    ADMIN_ADJUSTMENT = 'Admin Adjustment'
    # Extend with additional reasons as needed

class Reward(Base):
    __tablename__ = 'rewards'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    kudos = Column(Integer, nullable=False)
    streak = Column(Integer, nullable=False)
    date_awarded = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='rewards')

class RewardTransaction(Base):
    __tablename__ = 'reward_transactions'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    transaction_type = Column(SqlEnum('credit', 'debit', name='transaction_type'), nullable=False)
    kudos_amount = Column(Integer, nullable=False)
    reason = Column(SqlEnum(RewardReason), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='reward_transactions')
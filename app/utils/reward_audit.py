from sqlalchemy.orm import Session
from db.models.reward import RewardTransaction, RewardReason

def add_reward_transaction(db: Session, user_id: int, amount: int, transaction_type: str, reason: RewardReason):
    """
    Adds a new reward transaction to the database.

    Args:
        db (Session): SQLAlchemy database session.
        user_id (int): ID of the user receiving the reward.
        amount (int): Kudos amount (positive for credit, negative for debit).
        transaction_type (str): 'credit' or 'debit'.
        reason (RewardReason): Enum reason for the transaction.

    Returns:
        None
    """
    if transaction_type not in ["credit", "debit"]:
        raise ValueError("Invalid transaction_type. Use 'credit' or 'debit'.")

    transaction = RewardTransaction(
        user_id=user_id,
        transaction_type=transaction_type,
        kudos_amount=amount,
        reason=reason
    )
    db.add(transaction)
    db.commit()
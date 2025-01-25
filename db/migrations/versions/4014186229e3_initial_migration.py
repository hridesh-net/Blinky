"""Initial migration

Revision ID: 4014186229e3
Revises: 
Create Date: 2025-01-24 12:27:37.557705

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4014186229e3"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # --------------------------------------------
    # 1. Create All Tables (No FK Constraints Yet)
    # --------------------------------------------

    # permissions
    op.create_table(
        "permissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_permissions_id"), "permissions", ["id"], unique=False)

    # roles
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_roles_id"), "roles", ["id"], unique=False)

    # users (remove FK lines here, only columns)
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("emp_id", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("team_id", sa.Integer(), nullable=True),
        sa.Column("manager_id", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_emp_id"), "users", ["emp_id"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    # teams (remove FK lines here, only columns)
    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("leader_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_teams_id"), "teams", ["id"], unique=False)

    # audit_logs (remove FK lines here, only columns)
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("model_name", sa.String(), nullable=False),
        sa.Column("record_id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_logs_id"), "audit_logs", ["id"], unique=False)

    # notifications (remove FK lines here, only columns)
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notifications_id"), "notifications", ["id"], unique=False)

    # reward_transactions (remove FK lines here, only columns)
    op.create_table(
        "reward_transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "transaction_type",
            sa.Enum("credit", "debit", name="transaction_type"),
            nullable=False,
        ),
        sa.Column("kudos_amount", sa.Integer(), nullable=False),
        sa.Column(
            "reason",
            sa.Enum(
                "TASK_COMPLETION",
                "STREAK_BONUS",
                "MANAGER_AWARD",
                "ADMIN_ADJUSTMENT",
                name="rewardreason",
            ),
            nullable=False,
        ),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_reward_transactions_id"), "reward_transactions", ["id"], unique=False
    )

    # rewards (remove FK lines here, only columns)
    op.create_table(
        "rewards",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("kudos", sa.Integer(), nullable=False),
        sa.Column("streak", sa.Integer(), nullable=False),
        sa.Column("date_awarded", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_rewards_id"), "rewards", ["id"], unique=False)

    # role_permissions (remove FK lines here, only columns)
    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("permission_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("role_id", "permission_id"),
    )

    # tasks (remove FK lines here, only columns)
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("is_completed", sa.Boolean(), nullable=True),
        sa.Column(
            "priority",
            sa.Enum("LOW", "MEDIUM", "HIGH", name="taskpriority"),
            nullable=True,
        ),
        sa.Column("due_date", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tasks_id"), "tasks", ["id"], unique=False)

    # --------------------------------------------
    # 2. Add All Foreign Key Constraints Separately
    # --------------------------------------------

    # users.manager_id -> users.id
    op.create_foreign_key(
        "fk_users_manager_id_users",
        source_table="users",
        referent_table="users",
        local_cols=["manager_id"],
        remote_cols=["id"],
    )
    # users.team_id -> teams.id
    op.create_foreign_key(
        "fk_users_team_id_teams",
        source_table="users",
        referent_table="teams",
        local_cols=["team_id"],
        remote_cols=["id"],
    )

    # teams.leader_id -> users.id
    op.create_foreign_key(
        "fk_teams_leader_id_users",
        source_table="teams",
        referent_table="users",
        local_cols=["leader_id"],
        remote_cols=["id"],
    )

    # audit_logs.user_id -> users.id
    op.create_foreign_key(
        "fk_audit_logs_user_id_users",
        source_table="audit_logs",
        referent_table="users",
        local_cols=["user_id"],
        remote_cols=["id"],
    )

    # notifications.user_id -> users.id
    op.create_foreign_key(
        "fk_notifications_user_id_users",
        source_table="notifications",
        referent_table="users",
        local_cols=["user_id"],
        remote_cols=["id"],
    )

    # reward_transactions.user_id -> users.id
    op.create_foreign_key(
        "fk_reward_transactions_user_id_users",
        source_table="reward_transactions",
        referent_table="users",
        local_cols=["user_id"],
        remote_cols=["id"],
    )

    # rewards.user_id -> users.id
    op.create_foreign_key(
        "fk_rewards_user_id_users",
        source_table="rewards",
        referent_table="users",
        local_cols=["user_id"],
        remote_cols=["id"],
    )

    # role_permissions.role_id -> roles.id
    op.create_foreign_key(
        "fk_role_permissions_role_id_roles",
        source_table="role_permissions",
        referent_table="roles",
        local_cols=["role_id"],
        remote_cols=["id"],
    )

    # role_permissions.permission_id -> permissions.id
    op.create_foreign_key(
        "fk_role_permissions_permission_id_permissions",
        source_table="role_permissions",
        referent_table="permissions",
        local_cols=["permission_id"],
        remote_cols=["id"],
    )

    # tasks.user_id -> users.id
    op.create_foreign_key(
        "fk_tasks_user_id_users",
        source_table="tasks",
        referent_table="users",
        local_cols=["user_id"],
        remote_cols=["id"],
    )


def downgrade():
    # First drop all foreign key constraints in reverse order
    op.drop_constraint("fk_tasks_user_id_users", "tasks", type_="foreignkey")
    op.drop_constraint(
        "fk_role_permissions_permission_id_permissions",
        "role_permissions",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_role_permissions_role_id_roles", "role_permissions", type_="foreignkey"
    )
    op.drop_constraint("fk_rewards_user_id_users", "rewards", type_="foreignkey")
    op.drop_constraint(
        "fk_reward_transactions_user_id_users",
        "reward_transactions",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_notifications_user_id_users", "notifications", type_="foreignkey"
    )
    op.drop_constraint("fk_audit_logs_user_id_users", "audit_logs", type_="foreignkey")
    op.drop_constraint("fk_teams_leader_id_users", "teams", type_="foreignkey")
    op.drop_constraint("fk_users_team_id_teams", "users", type_="foreignkey")
    op.drop_constraint("fk_users_manager_id_users", "users", type_="foreignkey")

    # Then drop tables in reverse order of creation
    op.drop_index(op.f("ix_tasks_id"), table_name="tasks")
    op.drop_table("tasks")
    op.drop_table("role_permissions")
    op.drop_index(op.f("ix_rewards_id"), table_name="rewards")
    op.drop_table("rewards")
    op.drop_index(op.f("ix_reward_transactions_id"), table_name="reward_transactions")
    op.drop_table("reward_transactions")
    op.drop_index(op.f("ix_notifications_id"), table_name="notifications")
    op.drop_table("notifications")
    op.drop_index(op.f("ix_audit_logs_id"), table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_index(op.f("ix_teams_id"), table_name="teams")
    op.drop_table("teams")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_emp_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_roles_id"), table_name="roles")
    op.drop_table("roles")
    op.drop_index(op.f("ix_permissions_id"), table_name="permissions")
    op.drop_table("permissions")

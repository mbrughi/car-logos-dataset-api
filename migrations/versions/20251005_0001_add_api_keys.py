from alembic import op
import sqlalchemy as sa

revision = "20251005_0001"
down_revision = "f8cf950d202b"  # <-- metti qui l'ultima tua revision id
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "api_keys",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_api_keys_key", "api_keys", ["key"], unique=True)

def downgrade():
    op.drop_index("ix_api_keys_key", table_name="api_keys")
    op.drop_table("api_keys")

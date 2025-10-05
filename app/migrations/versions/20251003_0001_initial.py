from alembic import op
import sqlalchemy as sa

revision = "20251003_0001"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "brands",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("country", sa.String(length=2), nullable=True),
    )
    op.create_index("ix_brands_slug", "brands", ["slug"], unique=True)
    op.create_index("ix_brands_name", "brands", ["name"])

def downgrade():
    op.drop_index("ix_brands_name", table_name="brands")
    op.drop_index("ix_brands_slug", table_name="brands")
    op.drop_table("brands")

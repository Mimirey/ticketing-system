"""fix missing company applications table

Revision ID: 6ed0c5060bf3
Revises: 3d856af73d20
Create Date: 2026-10-15 14:43:40.100310

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ed0c5060bf3'
down_revision: Union[str, Sequence[str], None] = '3d856af73d20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if "company_applications" not in inspector.get_table_names():
        op.create_table(
            "company_applications",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "company_id",
                sa.Integer(),
                sa.ForeignKey("companies.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "application_id",
                sa.Integer(),
                sa.ForeignKey("applications.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.UniqueConstraint(
                "company_id",
                "application_id",
                name="uq_company_application",
            ),
        )

    columns = {
        col["name"]
        for col in inspector.get_columns("applications")
    }

    if "company_id" in columns:
        op.execute("""
            INSERT INTO company_applications (company_id, application_id)
            SELECT company_id, id
            FROM applications
            WHERE company_id IS NOT NULL
            ON CONFLICT (company_id, application_id) DO NOTHING
        """)


def downgrade() -> None:
    op.drop_table("company_applications")

"""change application company to many-to-many

Revision ID: 3d856af73d20
Revises: 7909f2b4bc7d
Create Date: 2026-10-15 14:16:47.579561

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d856af73d20'
down_revision: Union[str, Sequence[str], None] = '7909f2b4bc7d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
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
    op.execute("""
        INSERT INTO company_applications (company_id, application_id)
        SELECT company_id, id
        FROM applications
        WHERE company_id IS NOT NULL
    """)
    op.drop_constraint(
        "applications_company_id_fkey",
        "applications",
        type_="foreignkey",
    )
    op.drop_column("applications", "company_id")


def downgrade() -> None:
    op.add_column(
        "applications",
        sa.Column("company_id", sa.Integer(), nullable=True),
    )
    op.execute("""
        UPDATE applications
        SET company_id = (
            SELECT ca.company_id
            FROM company_applications ca
            WHERE ca.application_id = applications.id
            ORDER BY ca.company_id
            LIMIT 1
        )
    """)
    op.create_foreign_key(
        "applications_company_id_fkey",
        "applications",
        "companies",
        ["company_id"],
        ["id"],
    )

    op.drop_table("company_applications")#

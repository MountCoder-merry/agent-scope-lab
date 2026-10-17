"""persist deterministic experiment input data for repeatable runs"""

import sqlalchemy as sa
from alembic import op

revision = "0002_experiment_input"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("experiments", sa.Column("input_json", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("experiments", "input_json")

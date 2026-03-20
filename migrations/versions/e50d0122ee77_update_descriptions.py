"""update descriptions

Revision ID: e50d0122ee77
Revises: 9c2a1af65368
Create Date: 2026-03-18 14:50:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e50d0122ee77'
down_revision = '9c2a1af65368'
branch_labels = None
depends_on = None

def upgrade():
    # --- RecordedClass ---
    with op.batch_alter_table('recorded_class', schema=None) as batch_op:
        # 1. Add column as nullable (so existing rows can have NULL)
        batch_op.add_column(sa.Column('description', sa.Text(), nullable=True))
    
    # 2. Update existing rows with a placeholder description
    op.execute("UPDATE recorded_class SET description = 'No description provided' WHERE description IS NULL")
    
    # 3. Alter column to NOT NULL
    with op.batch_alter_table('recorded_class', schema=None) as batch_op:
        batch_op.alter_column('description', nullable=False)

    # --- Material ---
    with op.batch_alter_table('material', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.Text(), nullable=True))
    
    op.execute("UPDATE material SET description = 'No description provided' WHERE description IS NULL")
    
    with op.batch_alter_table('material', schema=None) as batch_op:
        batch_op.alter_column('description', nullable=False)

    # --- Assignment ---
    with op.batch_alter_table('assignment', schema=None) as batch_op:
        # This column already exists, we just need to make it NOT NULL.
        # But there may be rows with NULL, so first set a default, then alter.
        op.execute("UPDATE assignment SET description = 'No description provided' WHERE description IS NULL")
        batch_op.alter_column('description', nullable=False)


def downgrade():
    # Remove the description columns (or revert to nullable for assignment)
    with op.batch_alter_table('recorded_class', schema=None) as batch_op:
        batch_op.drop_column('description')

    with op.batch_alter_table('material', schema=None) as batch_op:
        batch_op.drop_column('description')

    with op.batch_alter_table('assignment', schema=None) as batch_op:
        batch_op.alter_column('description', nullable=True)
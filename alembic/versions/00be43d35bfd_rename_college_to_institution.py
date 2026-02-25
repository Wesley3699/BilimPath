"""rename college to institution

Revision ID: 00be43d35bfd
Revises: 017be387a676
Create Date: 2026-02-25 22:46:03.326085

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# ЭТИ СТРОКИ ОБЯЗАТЕЛЬНЫ:
revision: str = '00be43d35bfd'
down_revision: Union[str, Sequence[str], None] = '017be387a676'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Переименовываем основную таблицу
    op.rename_table('colleges', 'institutions')
    
    # 2. Переименовываем колонки в связанных таблицах
    op.alter_column('groups', 'college_id', new_column_name='institution_id')
    op.alter_column('users', 'college_id', new_column_name='institution_id')

    # 3. Обновляем внешние ключи (Postgres переименует саму цель ссылки автоматически, 
    # но нам нужно обновить имена самих констрейнтов для порядка)
    # Удаляем старые FK (по старым именам) и создаем новые
    op.drop_constraint('groups_college_id_fkey', 'groups', type_='foreignkey')
    op.create_foreign_key(op.f('groups_institution_id_fkey'), 'groups', 'institutions', ['institution_id'], ['id'])
    
    op.drop_constraint('users_college_id_fkey', 'users', type_='foreignkey')
    op.create_foreign_key(op.f('users_institution_id_fkey'), 'users', 'institutions', ['institution_id'], ['id'])


def downgrade() -> None:
    # Делаем всё в обратном порядке
    op.drop_constraint(op.f('users_institution_id_fkey'), 'users', type_='foreignkey')
    op.create_foreign_key('users_college_id_fkey', 'users', 'colleges', ['institution_id'], ['id'])
    
    op.drop_constraint(op.f('groups_institution_id_fkey'), 'groups', type_='foreignkey')
    op.create_foreign_key('groups_college_id_fkey', 'groups', 'colleges', ['institution_id'], ['id'])

    op.alter_column('users', 'institution_id', new_column_name='college_id')
    op.alter_column('groups', 'institution_id', new_column_name='college_id')
    
    op.rename_table('institutions', 'colleges')
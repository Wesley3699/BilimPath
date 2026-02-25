import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Импорт твоего Base
from app.models.models import Base

# Это объект конфигурации Alembic
config = context.config

# Настройка логирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Метаданные моделей для autogenerate
target_metadata = Base.metadata

def do_run_migrations_sync(connection):
    """Синхронная часть выполнения миграций."""
    context.configure(
        connection=connection, 
        target_metadata=target_metadata,
        # Это поможет избежать проблем с типами в Postgres при генерации
        render_as_batch=False 
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Запуск миграций в 'online' режиме (асинхронно)."""
    
    # Создаем асинхронный движок из конфига alembic.ini
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        # Магия SQLAlchemy для запуска синхронного Alembic в асинхронном соединении
        await connection.run_sync(do_run_migrations_sync)

    await connectable.dispose()

def run_migrations_offline() -> None:
    """Запуск миграций в 'offline' режиме."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    # Важно: запускаем асинхронную функцию через asyncio.run
    try:
        asyncio.run(run_migrations_online())
    except (KeyboardInterrupt, SystemExit):
        pass
# alembic/env.py

from logging.config import fileConfig
from sqlalchemy import engine_from_config, create_engine, pool
from alembic import context
from app.db.base import Base  # Import Base with metadata
from app.core.config import settings

# Load Alembic config and setup logging
config = context.config
fileConfig(config.config_file_name)

# Set up the synchronous database URL
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL_SYNC)

# Set the metadata for autogeneration
target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

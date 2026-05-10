from sqlalchemy import create_engine, text

from app.core.config import get_settings
from app.db.base import Base
from app.models import entities  # noqa: F401


def main() -> None:
    settings = get_settings()
    engine = create_engine(settings.sync_database_url)
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
        Base.metadata.create_all(bind=connection)
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_companies_normalized_name_trgm "
                "ON companies USING gin (normalized_name gin_trgm_ops);"
            )
        )
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_lcas_job_title_trgm "
                "ON lcas USING gin (job_title gin_trgm_ops);"
            )
        )
    print("Database schema created successfully.")


if __name__ == "__main__":
    main()

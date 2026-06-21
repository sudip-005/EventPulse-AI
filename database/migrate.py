"""Apply the idempotent EventPulse schema to DATABASE_URL."""
import os
from pathlib import Path

import psycopg2


def main() -> None:
    database_url = os.environ["DATABASE_URL"].replace("postgres://", "postgresql://", 1)
    schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
    with psycopg2.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(schema)
    print("EventPulse database schema is ready.")


if __name__ == "__main__":
    main()

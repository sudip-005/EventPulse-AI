"""Load idempotent Railway demo data into DATABASE_URL."""
import os
from pathlib import Path

import psycopg2


def main() -> None:
    database_url = os.environ["DATABASE_URL"].replace("postgres://", "postgresql://", 1)
    seed_sql = Path(__file__).with_name("seed.sql").read_text(encoding="utf-8")
    with psycopg2.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(seed_sql)
    print("EventPulse demo data is ready.")


if __name__ == "__main__":
    main()

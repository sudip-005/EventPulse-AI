import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

# Load env variables from backend/.env
env_path = r"c:\Users\SUDIP MANNA\OneDrive\Desktop\EventPulseAI\backend\.env"
load_dotenv(dotenv_path=env_path)

db_url = os.getenv("DATABASE_URL")
print("Connecting to:", db_url)
engine = create_engine(db_url)

inspector = inspect(engine)

for table_name in ["predictions", "learning_records", "events", "roads"]:
    print(f"\nColumns in table '{table_name}':")
    try:
        columns = inspector.get_columns(table_name)
        for col in columns:
            print(f" - {col['name']}: {col['type']}")
    except Exception as e:
        print(f"Error inspecting '{table_name}': {e}")

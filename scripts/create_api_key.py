import os, secrets, sys
from pathlib import Path

# Fix path per import app.*
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
os.chdir(ROOT_DIR)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models import Base
from app.models.api_key import ApiKey

def main():
    if len(sys.argv) < 2:
        print("Uso: python scripts/create_api_key.py <name>")
        sys.exit(1)
    name = sys.argv[1]
    key = secrets.token_hex(32)  # 64 chars hex
    engine = create_engine(settings.sqlalchemy_url, pool_pre_ping=True, future=True)
    Base.metadata.create_all(engine, tables=[ApiKey.__table__])
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    with Session() as s:
        s.add(ApiKey(name=name, key=key, is_active=True))
        s.commit()
    print(f"[OK] API Key per '{name}':\n{key}\n")
    print(f"Usala nel header {settings.API_KEY_HEADER}: {key}")

if __name__ == "__main__":
    # per sicurezza: esegui dalla root del progetto, così carica .env
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    main()

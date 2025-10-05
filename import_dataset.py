from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable, Iterator

from sqlalchemy import select, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Re-use app settings and models
from app.config import settings
from app.models.brand import Brand
from app.models import Base


def slugify(s: str) -> str:
    s = s.strip().lower()
    # sostituisci qualsiasi cosa non alfanumerica con '-'
    s = re.sub(r"[^a-z0-9]+", "-", s, flags=re.IGNORECASE)
    s = s.strip("-")
    return s or "unknown"


def coerce_country(val) -> str | None:
    if not val:
        return None
    v = str(val).strip()
    # accetta solo ISO2 (2 lettere). Se altro formato, prova a ridurre.
    if re.fullmatch(r"[A-Za-z]{2}", v):
        return v.upper()
    return None


def iter_brand_rows(data) -> Iterator[dict]:
    """
    Prova ad estrarre (name, slug, country?) da formati comuni di data.json.
    Restituisce dizionari: {'name':..., 'slug':..., 'country':...}
    """
    def normalize_item(item: dict) -> dict | None:
        if not isinstance(item, dict):
            return None
        name = item.get("name") or item.get("brand") or item.get("title")
        slug = item.get("slug") or item.get("id")
        country = item.get("country") or item.get("iso2") or item.get("cc")

        if not name and slug:
            # se manca name prova a derivarlo da slug
            name = slug.replace("-", " ").title()
        if not slug and name:
            slug = slugify(name)

        if not name or not slug:
            return None

        return {
            "name": str(name).strip(),
            "slug": slugify(str(slug)),
            "country": coerce_country(country),
        }

    # Formati possibili:
    # 1) data = [ {...}, {...} ]
    if isinstance(data, list):
        for it in data:
            norm = normalize_item(it)
            if norm:
                yield norm
        return

    # 2) data = {"brands":[...]}
    if isinstance(data, dict) and "brands" in data and isinstance(data["brands"], list):
        for it in data["brands"]:
            norm = normalize_item(it)
            if norm:
                yield norm
        return

    # 3) data = {"fiat": {...}, "bmw": {...}}
    if isinstance(data, dict):
        for _, it in data.items():
            norm = normalize_item(it if isinstance(it, dict) else {})
            if norm:
                yield norm
        return

    # fallback: niente trovato
    return


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(
        description="Importa brand da data.json del fork car-logos-dataset in MySQL (tabella brands)."
    )
    parser.add_argument(
        "--json-path",
        required=True,
        help="Percorso al file data.json del fork (es. /var/www/car-logos-dataset/data.json)",
    )
    parser.add_argument(
        "--truncate",
        action="store_true",
        help="Svuota la tabella brands PRIMA di importare (attenzione!).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostra cosa farebbe senza scrivere nel DB.",
    )
    args = parser.parse_args()

    json_path = Path(args.json_path).resolve()
    if not json_path.exists():
        print(f"[ERRORE] File non trovato: {json_path}", file=sys.stderr)
        sys.exit(1)

    print(f"• Carico JSON da: {json_path}")
    data = load_json(json_path)
    rows = list(iter_brand_rows(data))
    if not rows:
        print("[ATTENZIONE] Nessun brand rilevato dal JSON. Verifica formati/chiavi.", file=sys.stderr)
        sys.exit(2)

    print(f"• Trovati {len(rows)} brand candidati nel JSON.")

    # Connessione DB usando la stessa URL dell'app
    db_url = settings.sqlalchemy_url
    print(f"• Connessione DB: {db_url}")
    engine = create_engine(db_url, pool_pre_ping=True, future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

    # Garantisce che la tabella esista (in caso l'utente non abbia lanciato alembic)
    # In produzione si usa Alembic; qui solo safe-guard.
    Base.metadata.create_all(engine, tables=[Brand.__table__])

    with SessionLocal() as session:
        if args.truncate:
            if args.dry_run:
                print("[-] DRY-RUN: Troncamento tabella brands (saltato).")
            else:
                print("[!] Troncamento tabella brands…")
                session.execute(text("DELETE FROM brands"))
                session.commit()

        inserted = 0
        updated = 0
        skipped = 0

        for r in rows:
            slug = r["slug"]
            name = r["name"]
            country = r.get("country")

            existing = session.execute(select(Brand).where(Brand.slug == slug)).scalar_one_or_none()
            if not existing:
                if args.dry_run:
                    print(f"[+] INSERT {slug}  name='{name}'  country='{country or ''}'")
                else:
                    b = Brand(slug=slug, name=name, country=country)
                    session.add(b)
                inserted += 1
            else:
                need_update = False
                if existing.name != name:
                    need_update = True
                    if args.dry_run:
                        print(f"[~] UPDATE {slug}  name: '{existing.name}' -> '{name}'")
                    else:
                        existing.name = name
                # aggiorna country solo se cambia e se valido (2 lettere o None)
                new_country = country
                if existing.country != new_country:
                    need_update = True
                    if args.dry_run:
                        print(f"[~] UPDATE {slug}  country: '{existing.country}' -> '{new_country}'")
                    else:
                        existing.country = new_country

                if need_update:
                    updated += 1
                else:
                    skipped += 1

        if args.dry_run:
            print(f"\n--- DRY-RUN COMPLETATO ---")
            print(f"Da inserire: {inserted}, da aggiornare: {updated}, invariati: {skipped}")
            session.rollback()
        else:
            session.commit()
            print(f"\n✓ Import completato.")
            print(f"Inseriti: {inserted}, Aggiornati: {updated}, Invariati: {skipped}")


if __name__ == "__main__":
    main()

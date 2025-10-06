# app/services/storage.py
from pathlib import Path
from typing import Optional
from app.config import settings

# === Percorsi principali ===
ROOT = Path(settings.STORAGE_ROOT)
LOGOS_ROOT = ROOT / "logos"
LOCAL_ROOT = ROOT / "local-logos"

# Estensioni supportate (ordine di preferenza)
EXTS = (".svg", ".png", ".webp", ".jpg", ".jpeg")


def _first_existing(candidates: list[Path]) -> Optional[Path]:
    """Ritorna il primo file esistente nella lista."""
    for p in candidates:
        if p.exists():
            return p
    return None


def find_variant_path(brand_slug: str, variant: str) -> Optional[Path]:
    """
    Restituisce il path del logo per una data variante.
    variant: 'thumb' | 'optimized' | 'original' | 'local'
    
    Struttura attesa:
      logos/<variant>/<brand>.<ext>
      local-logos/<brand>.<ext>
    """
    # Percorso base
    if variant == "local":
        base_dir = LOCAL_ROOT
    else:
        base_dir = LOGOS_ROOT / variant

    # Verifica presenza del file in una delle estensioni supportate
    candidates = [base_dir / f"{brand_slug}{ext}" for ext in EXTS]
    return _first_existing(candidates)


def to_rel_url(p: Path) -> str:
    """
    Converte un path assoluto in URL relativo servito sotto /static/...
    - local-logos → /static/local-logos/...
    - logos → /static/logos/...
    """
    p = p.resolve()
    if str(p).startswith(str(LOCAL_ROOT.resolve())):
        rel = p.relative_to(LOCAL_ROOT)
        return f"/static/local-logos/{rel.as_posix()}"

    rel = p.relative_to(LOGOS_ROOT)
    return f"/static/logos/{rel.as_posix()}"


def build_public_url(rel_url: str) -> str:
    """Costruisce l'URL pubblico completo basato su PUBLIC_BASE_URL."""
    base = settings.PUBLIC_BASE_URL.rstrip("/")
    return f"{base}{rel_url}"

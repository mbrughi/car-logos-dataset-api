from pathlib import Path
from typing import Optional
from app.config import settings

ROOT = Path(settings.STORAGE_ROOT)
LOGOS_ROOT = ROOT / "logos"
LOCAL_ROOT = ROOT / "local-logos"

# estensioni preferite in ordine
EXTS = (".svg", ".png", ".webp")

def _first_existing(candidates: list[Path]) -> Optional[Path]:
    for p in candidates:
        if p.exists():
            return p
    return None

def _find_in_dir(dirpath: Path) -> Optional[Path]:
    """Cerca 'logo.svg/png/webp'; se non esiste, prende il primo file con estensioni note."""
    if not dirpath.exists():
        return None
    # 1) nomi standard
    cand = _first_existing([dirpath / f"logo{ext}" for ext in EXTS])
    if cand:
        return cand
    # 2) qualunque file supportato (in ordine di estensione preferita)
    for ext in EXTS:
        found = sorted(dirpath.glob(f"*{ext}"))
        if found:
            return found[0]
    return None

def find_variant_path(brand_slug: str, variant: str) -> Optional[Path]:
    """
    variant: 'thumb' | 'optimized' | 'original' | 'local'
    """
    if variant == "local":
        return _find_in_dir(LOCAL_ROOT / brand_slug)

    # logos/<variant>/<brand_slug>/
    base = LOGOS_ROOT / variant / brand_slug
    return _find_in_dir(base)

def to_rel_url(p: Path) -> str:
    """
    Converte un path assoluto in URL relativo da esporre sotto /static/...
    - se viene da local-logos -> /static/local-logos/...
    - se viene da logos -> /static/logos/...
    """
    p = p.resolve()
    if str(p).startswith(str(LOCAL_ROOT.resolve())):
        rel = p.relative_to(LOCAL_ROOT)
        return f"/static/local-logos/{rel.as_posix()}"
    rel = p.relative_to(LOGOS_ROOT)
    return f"/static/logos/{rel.as_posix()}"

def build_public_url(rel_url: str) -> str:
    base = settings.PUBLIC_BASE_URL.rstrip("/")
    return f"{base}{rel_url}"

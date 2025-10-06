# app/routers/logos.py
from fastapi import APIRouter, HTTPException, Depends, Response
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.brand import Brand
from app.services.storage import find_variant_path, to_rel_url, build_public_url
from app.security.auth import require_api_key
from app.services.rate_limit import rate_limit_dep

router = APIRouter(
    prefix="/v1/logos", 
    tags=["logos"],
    dependencies=[Depends(require_api_key()), Depends(rate_limit_dep())],
    )

@router.get("/{brand_slug}")
def get_logo(brand_slug: str, response: Response, db: Session = Depends(get_db)):
    b = db.execute(select(Brand).where(Brand.slug == brand_slug)).scalar_one_or_none()
    if not b:
        raise HTTPException(status_code=404, detail="Brand not found")

    # 1) override locale (se presente)
    assets: dict[str, dict] = {}
    local_p = find_variant_path(brand_slug, "local")
    if local_p:
        rel = to_rel_url(local_p)
        assets["local"] = {"path": rel, "url": build_public_url(rel)}

    # 2) varianti dal dataset ufficiale
    for variant in ("thumb", "optimized", "original"):
        p = find_variant_path(brand_slug, variant)
        if p:
            rel = to_rel_url(p)
            assets[variant] = {"path": rel, "url": build_public_url(rel)}
        
    

    import logging
    logging.warning(f"DEBUG LOGO CHECK: brand_slug={brand_slug}, assets={assets}")

    if not assets:
        raise HTTPException(status_code=404, detail="Logo not available")

    response.headers["Cache-Control"] = "public, max-age=31536000, immutable"    

    return {
        "brand": {"slug": b.slug, "name": b.name, "country": b.country},
        "assets": assets,
        "cache": {"max_age": 31536000, "immutable": True},
    }

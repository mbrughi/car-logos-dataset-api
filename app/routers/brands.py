from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.brand import Brand
from app.security.auth import require_api_key
from app.services.rate_limit import rate_limit_dep
from app.schemas.brand import BrandOut

router = APIRouter(
    prefix="/v1/brands",
    tags=["brands"],
    dependencies=[Depends(require_api_key()), Depends(rate_limit_dep())],
)

@router.get("", response_model=list[BrandOut])
def list_brands(
    response: Response,
    db: Session = Depends(get_db),
    q: str | None = Query(default=None, description="Search by name/slug"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
):
    stmt = select(Brand)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(Brand.name.ilike(like), Brand.slug.ilike(like)))
    # count totale
    total = db.execute(
        select(func.count()).select_from(stmt.subquery())
    ).scalar() or 0
    # pagina
    items = db.execute(
        stmt.order_by(Brand.name.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
    ).scalars().all()

    response.headers["X-Total-Count"] = str(total)
    response.headers["X-Page"] = str(page)
    response.headers["X-Page-Size"] = str(page_size)
    # caching “leggera” per elenco (5 minuti)
    response.headers["Cache-Control"] = "public, max-age=300"

    return items

@router.get("/{slug}", response_model=BrandOut)
def get_brand(slug: str, db: Session = Depends(get_db)):
    b = db.execute(select(Brand).where(Brand.slug == slug)).scalar_one_or_none()
    if not b:
        raise HTTPException(status_code=404, detail="Brand not found")
    return b

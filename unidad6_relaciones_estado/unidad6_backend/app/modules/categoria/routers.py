from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import Session
from app.database import get_session
from . import schemas, services

# [Consigna TP6 - Parte A, inciso c & Rúbrica Backend]:
# Endpoints FastAPI de Categorías (GET /categorias, POST, PUT/{id}, DELETE/{id})
# integrados con inyección de dependencias de sesión (db: Session = Depends(get_session)).
router = APIRouter(prefix="/categorias", tags=["Categorías"])


# [Consigna TP6 - Rúbrica Backend]: POST /categorias - Alta de categoría con código 201 Created
@router.post(
    "/", response_model=schemas.CategoriaRead, status_code=status.HTTP_201_CREATED
)
def alta_categoria(
    categoria: schemas.CategoriaCreate,
    db: Session = Depends(get_session),
):
    return services.crear(db, categoria)


# [Consigna TP6 - Rúbrica Backend]: GET /categorias - Listado de categorías con código 200 OK
@router.get(
    "/", response_model=List[schemas.CategoriaRead], status_code=status.HTTP_200_OK
)
def listar_categorias(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=50),
    db: Session = Depends(get_session),
):
    return services.obtener_todas(db, skip, limit)


# [Consigna TP6 - Rúbrica Backend]: GET /categorias/{id} - Detalle de categoría por ID con código 200 OK (o 404)
@router.get(
    "/{id}", response_model=schemas.CategoriaRead, status_code=status.HTTP_200_OK
)
def detalle_categoria(
    id: int = Path(..., gt=0),
    db: Session = Depends(get_session),
):
    categoria = services.obtener_por_id(db, id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada"
        )
    return categoria


# [Consigna TP6 - Rúbrica Backend]: PUT /categorias/{id} - Actualización de categoría con código 200 OK (o 404)
@router.put(
    "/{id}", response_model=schemas.CategoriaRead, status_code=status.HTTP_200_OK
)
def actualizar_categoria(
    categoria: schemas.CategoriaCreate,
    id: int = Path(..., gt=0),
    db: Session = Depends(get_session),
):
    actualizada = services.actualizar_total(db, id, categoria)
    if not actualizada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada"
        )
    return actualizada


@router.put(
    "/{id}/desactivar",
    response_model=schemas.CategoriaRead,
    status_code=status.HTTP_200_OK,
)
def borrado_logico(
    id: int = Path(..., gt=0),
    db: Session = Depends(get_session),
):
    desactivada = services.desactivar(db, id)
    if not desactivada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada"
        )
    return desactivada


# [Consigna TP6 - Rúbrica Backend]: DELETE /categorias/{id} - Eliminación de categoría con código 204 No Content
@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar_categoria(
    id: int = Path(..., gt=0),
    db: Session = Depends(get_session),
):
    eliminada = services.eliminar(db, id)
    if not eliminada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada"
        )
    return None

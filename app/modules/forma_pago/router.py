from typing import Annotated
from fastapi import APIRouter, Depends, status
from app.core.database import SessionDep
from app.core.deps import CurrentUser, require_role
from app.modules.auth.models import Usuario
from app.modules.forma_pago.schemas import FormaPagoCreate, FormaPagoUpdate, FormaPagoOut
from app.modules.forma_pago.service import FormaPagoService

router = APIRouter(prefix="/formas-pago", tags=["formas-pago"])

def get_forma_pago_service(session: SessionDep) -> FormaPagoService:
    return FormaPagoService(session)


@router.get("/", response_model=list[FormaPagoOut])
def listar(_user: CurrentUser, svc: FormaPagoService = Depends(get_forma_pago_service)) -> list[FormaPagoOut]:
    return svc.get_all()


@router.get("/{codigo}", response_model=FormaPagoOut)
def obtener(codigo: str, _user: CurrentUser, svc: FormaPagoService = Depends(get_forma_pago_service)) -> FormaPagoOut:
    return svc.get_by_codigo(codigo)


@router.post("/", response_model=FormaPagoOut, status_code=status.HTTP_201_CREATED)
def crear(_admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], data: FormaPagoCreate, svc: FormaPagoService = Depends(get_forma_pago_service)) -> FormaPagoOut:
    return svc.create(data)


@router.patch("/{codigo}", response_model=FormaPagoOut)
def actualizar(codigo: str, _admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))],
    data: FormaPagoUpdate, svc: FormaPagoService = Depends(get_forma_pago_service)) -> FormaPagoOut:
    return svc.update(codigo, data)


@router.delete("/{codigo}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(codigo: str, _admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], svc: FormaPagoService = Depends(get_forma_pago_service)) -> None:
    svc.delete(codigo)
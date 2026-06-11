from fastapi import APIRouter
from sqlmodel import select
from app.core.database import SessionDep
from app.core.deps import CurrentUser
from app.modules.forma_pago.models import FormaPago
from app.modules.forma_pago.schemas import FormaPagoOut
from app.modules.unidad_medida.models import UnidadMedida
from app.modules.unidad_medida.schemas import UnidadMedidaOut
from app.modules.roles.models import Rol
from app.modules.roles.schemas import RolOut


router = APIRouter(tags=["catalogos"])


@router.get("/formas-pago", response_model=list[FormaPagoOut])
def listar_formas_pago(_user: CurrentUser, session: SessionDep):
    formas = session.exec(select(FormaPago)).all()
    return [FormaPagoOut.model_validate(f) for f in formas]


@router.get("/unidades-medida", response_model=list[UnidadMedidaOut])
def listar_unidades_medida(_user: CurrentUser, session: SessionDep):
    unidades = session.exec(
        select(UnidadMedida).where(UnidadMedida.deleted_at.is_(None))
    ).all()
    return [UnidadMedidaOut.model_validate(u) for u in unidades]


@router.get("/roles", response_model=list[RolOut])
def listar_roles(_user: CurrentUser, session: SessionDep):
    roles = session.exec(select(Rol)).all()
    return [RolOut.model_validate(r) for r in roles]
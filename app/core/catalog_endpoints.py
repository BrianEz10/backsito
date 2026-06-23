from fastapi import APIRouter
from app.core.database import SessionDep
from app.core.deps import CurrentUser
from app.modules.forma_pago.schemas import FormaPagoOut
from app.modules.unidad_medida.schemas import UnidadMedidaOut
from app.modules.roles.schemas import RolOut
from app.modules.pedidos.repository import PedidoRepository
from app.modules.productos.repository import ProductoRepository
from app.modules.roles.repository import RolRepository

router = APIRouter(tags=["catalogos"])


@router.get("/formas-pago", response_model=list[FormaPagoOut])
def listar_formas_pago(_user: CurrentUser, session: SessionDep):
    formas = PedidoRepository(session).get_all_formas_pago()
    return [FormaPagoOut.model_validate(f) for f in formas]


@router.get("/unidades-medida", response_model=list[UnidadMedidaOut])
def listar_unidades_medida(_user: CurrentUser, session: SessionDep):
    unidades = ProductoRepository(session).get_all_unidades_medida()
    return [UnidadMedidaOut.model_validate(u) for u in unidades]


@router.get("/roles", response_model=list[RolOut])
def listar_roles(_user: CurrentUser, session: SessionDep):
    roles = RolRepository(session).get_all()
    return [RolOut.model_validate(r) for r in roles]
import logging
from typing import Annotated
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from app.core.config import settings
from app.core.database import SessionDep
from app.modules.usuarios.models import Usuario
from app.modules.pagos.schemas import CrearPagoRequest, ConfirmarPagoRequest, PagoCrearResponse, PagoEstadoResponse
from app.modules.pagos.service import PaymentService
from app.core.deps import CurrentUser, require_role


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/pagos", tags=["pagos"])


def get_payment_service(session: SessionDep) -> PaymentService:
    return PaymentService(session)


@router.post("/crear", response_model=PagoCrearResponse, status_code=status.HTTP_201_CREATED)
def create_preference(data: CrearPagoRequest, current_user: Annotated[Usuario, Depends(require_role(["CLIENT"]))], svc: PaymentService = Depends(get_payment_service)):
    return svc.crear_pago(data.pedido_id, current_user.id)


@router.post("/webhook")
async def webhook(request: Request, svc: PaymentService = Depends(get_payment_service)):
    try:
        query_params = dict(request.query_params)
        if request.headers.get("content-type", "").startswith("application/json"):
            data = await request.json()
        else:
            data = dict(await request.form())
        return svc.procesar_webhook(data, query_params=query_params)
    except Exception as e:
        logger.exception("Error en webhook MP")
        return {"status": "error", "reason": str(e)}


@router.post("/confirm", response_model=PagoEstadoResponse)
def confirm_payment(data: ConfirmarPagoRequest, svc: PaymentService = Depends(get_payment_service)):
    return svc.confirmar_pago(data.pedido_id, data.payment_id)


@router.get("/redirect/{pedido_id}/{status}")
async def redirect_after_pago(pedido_id: int, status: str, request: Request):

    frontend_url = settings.FRONTEND_URL
    qs = request.url.query
    url = f"{frontend_url}/orders/{pedido_id}/{status}"
    if qs:
        url += f"?{qs}"
    return RedirectResponse(url=url)


@router.get("/{pedido_id}")
def obtener_pago(pedido_id: int, current_user: CurrentUser, svc: PaymentService = Depends(get_payment_service)):
    roles = [rol.codigo for rol in current_user.roles]
    return svc.obtener_pago(pedido_id, current_user.id, roles)
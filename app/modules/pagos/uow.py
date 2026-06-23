from sqlmodel import Session
from app.core.uow import UnitOfWork
from app.modules.pagos.repository import PagoRepository
from app.modules.pedidos.repository import PedidoRepository


class PagoUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.pagos = PagoRepository(session)
        self.pedidos = PedidoRepository(session)
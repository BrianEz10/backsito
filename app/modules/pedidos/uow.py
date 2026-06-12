from sqlmodel import Session
from app.core.uow import UnitOfWork
from app.modules.pedidos.repository import PedidoRepository


class PedidoUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.pedidos = PedidoRepository(session)
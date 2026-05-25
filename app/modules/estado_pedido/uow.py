from sqlmodel import Session
from app.core.uow import UnitOfWork
from app.modules.estado_pedido.repository import EstadoPedidoRepository

class EstadoPedidoUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.estados = EstadoPedidoRepository(session)
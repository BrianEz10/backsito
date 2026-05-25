from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.estado_pedido.models import EstadoPedido

class EstadoPedidoRepository(BaseRepository[EstadoPedido]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, EstadoPedido)
        
    def get_by_codigo(self, codigo: str) -> EstadoPedido | None:
        return self.session.get(EstadoPedido, codigo)
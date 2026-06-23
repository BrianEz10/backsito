from sqlmodel import Session
from app.core.uow import UnitOfWork
from app.modules.pedidos.repository import PedidoRepository
from app.modules.productos.repository import ProductoRepository
from app.modules.direcciones.repository import DireccionRepository
from app.modules.ingredientes.repository import IngredienteRepository


class PedidoUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.pedidos = PedidoRepository(session)
        self.productos = ProductoRepository(session)
        self.direcciones = DireccionRepository(session)
        self.ingredientes = IngredienteRepository(session)
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.core.repository import BaseRepository
from app.modules.pedidos.models import Pedido


class PedidoRepository(BaseRepository[Pedido]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Pedido)


    def get_by_id_with_all(self, id: int) -> Pedido | None:
        return self.session.exec(
            select(Pedido)
            .where(Pedido.id == id, Pedido.deleted_at == None)
            .options(selectinload(Pedido.detalles))
            .options(selectinload(Pedido.historial))
        ).first()
    

    def get_by_usuario(self, usuario_id: int) -> list[Pedido]:
        return list(
            self.session.exec(
                select(Pedido)
                .where(Pedido.usuario_id == usuario_id, Pedido.deleted_at == None)
                .order_by(Pedido.created_at.desc())
            ).all()
        )
    
    
    def get_all_activos(self) -> list[Pedido]:
        return list(
            self.session.exec(
                select(Pedido).where(Pedido.deleted_at == None)
                .order_by(Pedido.created_at.desc())
            ).all()
        )
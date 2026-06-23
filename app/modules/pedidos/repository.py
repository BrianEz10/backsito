from sqlalchemy import func
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.core.repository import BaseRepository
from app.modules.forma_pago.models import FormaPago
from app.modules.pedidos.models import DetallePedido, HistorialEstadoPedido, Pedido


class PedidoRepository(BaseRepository[Pedido]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Pedido)

    
    def get_by_id(self, id: int) -> Pedido | None:
        return self.session.exec(
            select(Pedido)
            .where(Pedido.id == id, Pedido.deleted_at == None)
            .options(selectinload(Pedido.detalles))
            .options(selectinload(Pedido.historial))
        ).first()
    

    def lock_by_id(self, id: int) -> Pedido | None:
        return self.session.exec(
            select(Pedido).where(Pedido.id == id, Pedido.deleted_at == None)
            .with_for_update()
        ).first()
    
    #Para el "catalog_endpoints.py"
    def get_all_formas_pago(self) -> list[FormaPago]:
        return list(self.session.exec(select(FormaPago)).all())


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
    

    def get_forma_pago(self, codigo: str) -> FormaPago | None:
        return self.session.get(FormaPago, codigo)


    def get_historial_by_pedido(self, pedido_id: int) -> list[HistorialEstadoPedido]:
        return list(self.session.exec(
            select(HistorialEstadoPedido)
            .where(HistorialEstadoPedido.pedido_id == pedido_id)
            .order_by(HistorialEstadoPedido.created_at.asc())
        ).all())


    def find_all_filtered(self, usuario_id: int | None = None, offset: int = 0, limit: int = 20) -> list[Pedido]:
        stmt = select(Pedido).where(Pedido.deleted_at == None)
        if usuario_id is not None:
            stmt = stmt.where(Pedido.usuario_id == usuario_id)
        stmt = stmt.order_by(Pedido.created_at.desc()).offset(offset).limit(limit)
        return list(self.session.exec(stmt).all())


    def count_filtered(self, usuario_id: int | None = None) -> int:
        stmt = select(func.count()).select_from(Pedido).where(Pedido.deleted_at == None)
        if usuario_id is not None:
            stmt = stmt.where(Pedido.usuario_id == usuario_id)
        return self.session.exec(stmt).one()


    def add_detalle(self, detalle: DetallePedido) -> None:
        self.session.add(detalle)
        self.session.flush()


    def add_historial_entry(self, historial: HistorialEstadoPedido) -> None:
        self.session.add(historial)
        self.session.flush()
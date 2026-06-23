from sqlalchemy import func
from sqlmodel import Session, select
from app.modules.pedidos.models import Pedido, DetallePedido
from app.modules.productos.models import Producto
from app.modules.usuarios.models import Usuario
from app.modules.forma_pago.models import FormaPago


class AdminRepository:
    def __init__(self, session: Session) -> None:
        self.session = session


    def get_total_pedidos(self) -> int:
        return self.session.exec(
            select(func.count(Pedido.id)).where(Pedido.deleted_at == None)
        ).one()


    def get_ingresos(self) -> float:
        return float(self.session.exec(
            select(func.coalesce(func.sum(Pedido.total), 0))
            .where(Pedido.estado_codigo == "ENTREGADO", Pedido.deleted_at == None)
        ).one())


    def get_pedidos_por_estado(self) -> list[tuple[str, int]]:
        return list(self.session.exec(
            select(Pedido.estado_codigo, func.count(Pedido.id))
            .where(Pedido.deleted_at == None)
            .group_by(Pedido.estado_codigo)
        ).all())


    def get_productos_mas_vendidos(self) -> list[tuple[str, int]]:
        return list(self.session.exec(
            select(Producto.nombre, func.coalesce(func.sum(DetallePedido.cantidad), 0))
            .select_from(DetallePedido)
            .join(Producto, DetallePedido.producto_id == Producto.id)
            .group_by(DetallePedido.producto_id, Producto.nombre)
            .order_by(func.sum(DetallePedido.cantidad).desc())
            .limit(5)
        ).all())


    def get_pedidos_recientes(self) -> list[tuple]:
        return list(self.session.exec(
            select(Pedido.id, Usuario.email, Pedido.total, Pedido.estado_codigo, Pedido.created_at)
            .join(Usuario, Pedido.usuario_id == Usuario.id)
            .where(Pedido.deleted_at == None)
            .order_by(Pedido.created_at.desc())
            .limit(10)
        ).all())


    def get_total_por_forma_pago(self) -> list[tuple[str, float]]:
        return list(self.session.exec(
            select(FormaPago.codigo, func.coalesce(func.sum(Pedido.total), 0))
            .select_from(Pedido)
            .join(FormaPago, Pedido.forma_pago_codigo == FormaPago.codigo)
            .where(Pedido.estado_codigo == "ENTREGADO", Pedido.deleted_at == None)
            .group_by(FormaPago.codigo)
        ).all())
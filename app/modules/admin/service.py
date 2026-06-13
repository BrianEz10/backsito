from sqlmodel import Session, select
from sqlalchemy import func

from app.modules.pedidos.models import Pedido, DetallePedido
from app.modules.productos.models import Producto
from app.modules.usuarios.models import Usuario
from app.modules.admin.schemas import DashboardResponse, EstadoCount, ProductoVendido, PedidoReciente, TotalPorFormaPago
from app.modules.admin.uow import AdminUnitOfWork
from app.modules.forma_pago.models import FormaPago


class AdminService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_dashboard(self) -> DashboardResponse:
        with AdminUnitOfWork(self._session) as uow:
            total_pedidos = uow._session.exec(
                select(func.count(Pedido.id)).where(Pedido.deleted_at == None)
            ).one()


            ingresos = uow._session.exec(
                select(func.coalesce(func.sum(Pedido.total), 0))
                .where(Pedido.estado_codigo == "ENTREGADO", Pedido.deleted_at == None)
            ).one()
            ingresos_totales = float(ingresos)


            filas_estados = uow._session.exec(
                select(Pedido.estado_codigo, func.count(Pedido.id))
                .where(Pedido.deleted_at == None)
                .group_by(Pedido.estado_codigo)
            ).all()
            pedidos_por_estado = [EstadoCount(estado=e, cantidad=c) for e, c in filas_estados]


            filas_productos = uow._session.exec(
                select(Producto.nombre, func.coalesce(func.sum(DetallePedido.cantidad), 0))
                .select_from(DetallePedido)
                .join(Producto, DetallePedido.producto_id == Producto.id)
                .group_by(DetallePedido.producto_id, Producto.nombre)
                .order_by(func.sum(DetallePedido.cantidad).desc())
                .limit(5)
            ).all()
            productos_mas_vendidos = [ProductoVendido(nombre=n, total_vendido=int(c)) for n, c in filas_productos]


            filas_recientes = uow._session.exec(
                select(Pedido.id, Usuario.email, Pedido.total, Pedido.estado_codigo, Pedido.created_at)
                .join(Usuario, Pedido.usuario_id == Usuario.id)
                .where(Pedido.deleted_at == None)
                .order_by(Pedido.created_at.desc())
                .limit(10)
            ).all()
            pedidos_recientes = [
                PedidoReciente(id=pid, usuario_email=email, total=float(t), estado_codigo=est, created_at=ca)
                for pid, email, t, est, ca in filas_recientes
            ]
            
            
            filas_formas_pago = uow._session.exec(
                select(FormaPago.codigo, func.coalesce(func.sum(Pedido.total), 0))
                .select_from(Pedido)
                .join(FormaPago, Pedido.forma_pago_codigo == FormaPago.codigo)
                .where(Pedido.estado_codigo == "ENTREGADO", Pedido.deleted_at == None)
                .group_by(FormaPago.codigo)
            ).all()
            total_por_forma_pago = [TotalPorFormaPago(forma_pago=fp, total=float(t)) for fp, t in filas_formas_pago]


        return DashboardResponse(
            total_pedidos=total_pedidos,
            ingresos_totales=ingresos_totales,
            pedidos_por_estado=pedidos_por_estado,
            productos_mas_vendidos=productos_mas_vendidos,
            pedidos_recientes=pedidos_recientes,
            total_por_forma_pago=total_por_forma_pago
        )
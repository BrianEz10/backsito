from sqlmodel import Session
from app.modules.admin.schemas import DashboardResponse, EstadoCount, ProductoVendido, PedidoReciente, TotalPorFormaPago
from app.modules.admin.uow import AdminUnitOfWork


class AdminService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_dashboard(self) -> DashboardResponse:
        with AdminUnitOfWork(self._session) as uow:
            total_pedidos = uow.admin.get_total_pedidos()

            ingresos_totales = uow.admin.get_ingresos()

            filas_estados = uow.admin.get_pedidos_por_estado()
            pedidos_por_estado = [EstadoCount(estado=e, cantidad=c) for e, c in filas_estados]

            filas_productos = uow.admin.get_productos_mas_vendidos()
            productos_mas_vendidos = [ProductoVendido(nombre=n, total_vendido=int(c)) for n, c in filas_productos]

            filas_recientes = uow.admin.get_pedidos_recientes()
            pedidos_recientes = [
                PedidoReciente(id=pid, usuario_email=email, total=float(t), estado_codigo=est, created_at=ca)
                for pid, email, t, est, ca in filas_recientes
            ]
            
            filas_formas_pago = uow.admin.get_total_por_forma_pago()
            total_por_forma_pago = [TotalPorFormaPago(forma_pago=fp, total=float(t)) for fp, t in filas_formas_pago]


        return DashboardResponse(
            total_pedidos=total_pedidos,
            ingresos_totales=ingresos_totales,
            pedidos_por_estado=pedidos_por_estado,
            productos_mas_vendidos=productos_mas_vendidos,
            pedidos_recientes=pedidos_recientes,
            total_por_forma_pago=total_por_forma_pago
        )
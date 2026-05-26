from fastapi import HTTPException
from datetime import datetime, timezone
from sqlmodel import Session, select
from app.modules.pedidos.models import Pedido, DetallePedido, HistorialEstadoPedido
from app.modules.pedidos.schemas import PedidoCreate, PedidoOut, DetallePedidoOut, HistorialOut, AvanceEstadoRequest
from app.modules.pedidos.uow import PedidoUnitOfWork
from app.modules.productos.models import Producto
from app.modules.direcciones.models import DireccionEntrega
from app.modules.forma_pago.models import FormaPago


TRANSICIONES_VALIDAS = {
    "PENDIENTE":  ["CONFIRMADO", "CANCELADO"],
    "CONFIRMADO": ["EN_PREP", "PENDIENTE", "CANCELADO"],
    "EN_PREP":    ["EN_CAMINO", "CONFIRMADO", "CANCELADO"],
    "EN_CAMINO":  ["ENTREGADO", "EN_PREP", "CANCELADO"],
    "ENTREGADO":  [],
    "CANCELADO":  [],
}

ROLES_ADMIN_PEDIDOS = ["ADMIN", "PEDIDOS"]

COSTO_ENVIO = 50.00


class PedidoService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _get_or_404(self, uow: PedidoUnitOfWork, pedido_id: int) -> Pedido:
        pedido = uow.pedidos.get_by_id(pedido_id)
        if not pedido:
            raise HTTPException(404, "Pedido no encontrado")
        return pedido
    
    def _pedido_to_out(self, pedido: Pedido) -> PedidoOut:
        return PedidoOut(
            id=pedido.id,
            usuario_id=pedido.usuario_id,
            direccion_id=pedido.direccion_id,
            estado_codigo=pedido.estado_codigo,
            forma_pago_codigo=pedido.forma_pago_codigo,
            subtotal=pedido.subtotal,
            descuento=pedido.descuento,
            costo_envio=pedido.costo_envio,
            total=pedido.total,
            notas=pedido.notas,
            created_at=pedido.created_at,
            detalles=[DetallePedidoOut(
                pedido_id=d.pedido_id,
                producto_id=d.producto_id,
                cantidad=d.cantidad,
                nombre_snapshot=d.nombre_snapshot,
                precio_snapshot=d.precio_snapshot,
                subtotal_snap=d.subtotal_snap,
                personalizacion=d.personalizacion,
                created_at=d.created_at,
            ) for d in pedido.detalles],
            historial=[HistorialOut(
                pedido_id=h.pedido_id,
                estado_desde=h.estado_desde,
                estado_hacia=h.estado_hacia,
                usuario_id=h.usuario_id,
                motivo=h.motivo,
                created_at=h.created_at,
            ) for h in pedido.historial],
        )
    
    def create(self, data: PedidoCreate, usuario_id: int) -> PedidoOut:
        with PedidoUnitOfWork(self._session) as uow:
            subtotal = 0.0
            detalles = []
            for item in data.items:
                producto = uow.pedidos.session.get(Producto, item.producto_id)
                if not producto or producto.deleted_at is not None:
                    raise HTTPException(404, f"Producto {item.producto_id} no encontrado")
                if producto.stock_cantidad < item.cantidad:
                    raise HTTPException(400, f"Stock insuficiente para {producto.nombre}")
                producto.stock_cantidad -= item.cantidad
                precio_snap = producto.precio_base
                subtotal_item = precio_snap * item.cantidad
                subtotal += subtotal_item

                detalle = DetallePedido(
                    producto_id=producto.id,
                    cantidad=item.cantidad,
                    nombre_snapshot=producto.nombre,
                    precio_snapshot=precio_snap,
                    subtotal_snap=subtotal_item,
                    personalizacion=item.personalizacion,
                )
                detalles.append(detalle)

            fp = uow.pedidos.session.get(FormaPago, data.forma_pago_codigo)
            if not fp:
                raise HTTPException(400, f"Forma de pago '{data.forma_pago_codigo}' no existe")

            dir_entrega = uow.pedidos.session.get(DireccionEntrega, data.direccion_id)
            if not dir_entrega or dir_entrega.usuario_id != usuario_id:
                raise HTTPException(400, "Dirección de entrega no válida")

            total = subtotal + COSTO_ENVIO
            pedido = Pedido(
                usuario_id=usuario_id,
                direccion_id=data.direccion_id,
                estado_codigo="PENDIENTE",
                forma_pago_codigo=data.forma_pago_codigo,
                subtotal=subtotal,
                descuento=0.00,
                costo_envio=COSTO_ENVIO,
                total=total,
                notas=data.notas,
            )
            uow.pedidos.add(pedido)

            for d in detalles:
                d.pedido_id = pedido.id
                uow.pedidos.session.add(d)

            historial = HistorialEstadoPedido(
                pedido_id=pedido.id,
                estado_desde=None,
                estado_hacia="PENDIENTE",
                usuario_id=usuario_id,
                motivo=None,
            )
            uow.pedidos.session.add(historial)

            result = self._pedido_to_out(pedido)
        return result
    
    def get_all(self, usuario_id: int, roles: list[str]) -> list[PedidoOut]:
        with PedidoUnitOfWork(self._session) as uow:
            if any(r in ROLES_ADMIN_PEDIDOS for r in roles):
                pedidos = uow.pedidos.get_all_activos()
            else:
                pedidos = uow.pedidos.get_by_usuario(usuario_id)
            result = [self._pedido_to_out(p) for p in pedidos]
        return result

    def get_by_id(self, pedido_id: int, usuario_id: int, roles: list[str]) -> PedidoOut:
        with PedidoUnitOfWork(self._session) as uow:
            pedido = uow.pedidos.get_by_id(pedido_id)
            if not pedido:
                raise HTTPException(404, "Pedido no encontrado")
            is_admin = any(r in ROLES_ADMIN_PEDIDOS for r in roles)
            if not is_admin and pedido.usuario_id != usuario_id:
                raise HTTPException(404, "Pedido no encontrado")
            result = self._pedido_to_out(pedido)
        return result

    def avanzar_estado(self, pedido_id: int, data: AvanceEstadoRequest, usuario_id: int, roles: list[str]) -> PedidoOut:
        with PedidoUnitOfWork(self._session) as uow:
            pedido = self._get_or_404(uow, pedido_id)
            estado_actual = pedido.estado_codigo
            estado_destino = data.estado_hacia
            if estado_destino not in TRANSICIONES_VALIDAS.get(estado_actual, []):
                raise HTTPException(400, f"No se puede pasar de {estado_actual} a {estado_destino}")

            es_cliente = "CLIENT" in roles
            if es_cliente:
                if estado_destino != "CANCELADO":
                    raise HTTPException(403, "Como cliente solo puedes cancelar pedidos")
                if estado_actual not in ["PENDIENTE", "CONFIRMADO"]:
                    raise HTTPException(400, "Solo puedes cancelar pedidos pendientes o confirmados")

            if estado_destino == "CANCELADO" and not data.motivo:
                raise HTTPException(400, "Motivo obligatorio para cancelar un pedido")
            
            if estado_destino == "CANCELADO":
                for detalle in pedido.detalles:
                    producto = uow.pedidos.session.get(Producto, detalle.producto_id)
                    if producto:
                        producto.stock_cantidad += detalle.cantidad

            pedido.estado_codigo = estado_destino
            historial = HistorialEstadoPedido(
                pedido_id=pedido.id,
                estado_desde=estado_actual,
                estado_hacia=estado_destino,
                usuario_id=usuario_id,
                motivo=data.motivo,
            )
            uow.pedidos.session.add(historial)
            result = self._pedido_to_out(pedido)
        return result

    def delete(self, pedido_id: int) -> None:
        with PedidoUnitOfWork(self._session) as uow:
            pedido = self._get_or_404(uow, pedido_id)
            pedido.deleted_at = datetime.now(timezone.utc)
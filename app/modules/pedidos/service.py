from datetime import datetime, timezone
from sqlmodel import Session, select
from app.modules.pedidos.models import Pedido, DetallePedido, HistorialEstadoPedido
from app.modules.pedidos.schemas import PedidoCreate, PedidoOut, DetallePedidoOut, HistorialOut, AvanceEstadoRequest, PaginatedPedidos
from app.modules.pedidos.uow import PedidoUnitOfWork
from app.modules.productos.models import Producto
from app.modules.direcciones.models import DireccionEntrega
from app.modules.direcciones.schemas import DireccionOut
from app.modules.forma_pago.models import FormaPago
from app.modules.ingredientes.models import Ingrediente
from app.core.ws_manager import manager
from sqlalchemy import func
from app.core.errors import http_error


TRANSICIONES_VALIDAS = {
    "PENDIENTE":  ["CONFIRMADO", "CANCELADO"],
    "CONFIRMADO": ["EN_PREP", "CANCELADO"],
    "EN_PREP":    ["ENTREGADO", "CANCELADO"],
    "ENTREGADO":  [],
    "CANCELADO":  [],
}


ROLES_ADMIN_PEDIDOS = ["ADMIN", "PEDIDOS"]
METODOS_SIN_DIRECCION = ["RETIRO"]
COSTO_ENVIO = 50.00


EVENTOS_WS = {
    "CONFIRMADO": "PEDIDO_CONFIRMADO",
    "EN_PREP": "PEDIDO_EN_PREPARACION",
    "ENTREGADO": "PEDIDO_ENTREGADO",
    "CANCELADO": "PEDIDO_CANCELADO",
}


class PedidoService:
    def __init__(self, session: Session) -> None:
        self._session = session


    def _get_or_404(self, uow: PedidoUnitOfWork, pedido_id: int) -> Pedido:
        pedido = uow.pedidos.get_by_id(pedido_id)
        if not pedido:
            raise http_error(404, "Pedido no encontrado", "NOT_FOUND", "pedido_id")
        return pedido
    

    def _pedido_to_out(self, pedido: Pedido) -> PedidoOut:
        ing_ids = set()
        for d in pedido.detalles:
            if d.personalizacion:
                ing_ids.update(d.personalizacion)
        ing_map: dict[int, str] = {}
        if ing_ids:
            ingredients = self._session.exec(
                select(Ingrediente).where(Ingrediente.id.in_(ing_ids))
            ).all()
            for ing in ingredients:
                ing_map[ing.id] = ing.nombre
        direccion_out = None
        if pedido.direccion_id is not None:
            dir_entrega = self._session.get(DireccionEntrega, pedido.direccion_id)
            if dir_entrega:
                direccion_out = DireccionOut.model_validate(dir_entrega)

        return PedidoOut(
            id=pedido.id,
            usuario_id=pedido.usuario_id,
            direccion_id=pedido.direccion_id,
            direccion=direccion_out,
            estado_codigo=pedido.estado_codigo,
            forma_pago_codigo=pedido.forma_pago_codigo,
            metodo_envio=pedido.metodo_envio,
            subtotal=pedido.subtotal,
            descuento=pedido.descuento,
            costo_envio=pedido.costo_envio,
            total=pedido.total,
            nombre_para=pedido.nombre_para,
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
                personalizacion_nombres=[ing_map[i] for i in d.personalizacion if i in ing_map] if d.personalizacion else None,
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
    

    async def create(self, data: PedidoCreate, usuario_id: int, roles: list[str]) -> PedidoOut:
        with PedidoUnitOfWork(self._session) as uow:
            subtotal = 0.0
            detalles = []
            for item in data.items:
                producto = uow.pedidos.session.get(Producto, item.producto_id)
                if not producto or producto.deleted_at is not None:
                    raise http_error(404, f"Producto {item.producto_id} no encontrado", "NOT_FOUND", "producto_id")
                if producto.stock_cantidad < item.cantidad:
                    raise http_error(400, f"Stock insuficiente para {producto.nombre}", "STOCK_INSUFFICIENT", "producto_id")
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
                raise http_error(400, f"Forma de pago '{data.forma_pago_codigo}' no existe", "NOT_FOUND", "forma_pago_codigo")
            if any(r in ["CAJERO", "ADMIN", "PEDIDOS"] for r in roles) and data.direccion_id is None:
                data.metodo_envio = "RETIRO"
            if data.direccion_id is not None:
                dir_entrega = uow.pedidos.session.get(DireccionEntrega, data.direccion_id)
                if not dir_entrega or dir_entrega.usuario_id != usuario_id:
                    raise http_error(400, "Dirección de entrega no válida", "BAD_REQUEST", "direccion_id")
            elif data.metodo_envio not in METODOS_SIN_DIRECCION:
                raise http_error(400, "Dirección de entrega requerida", "BAD_REQUEST", "direccion_id")

            costo_envio = 0 if data.metodo_envio in METODOS_SIN_DIRECCION else COSTO_ENVIO
            total = subtotal + costo_envio
            pedido = Pedido(
                usuario_id=usuario_id,
                direccion_id=data.direccion_id,
                estado_codigo="PENDIENTE",
                forma_pago_codigo=data.forma_pago_codigo,
                metodo_envio=data.metodo_envio,
                nombre_para=data.nombre_para,
                subtotal=subtotal,
                descuento=0.00,
                costo_envio=costo_envio,
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

        evento = {
            "event": EVENTOS_WS.get("PENDIENTE", "PEDIDO_CREADO"),
            "pedido_id": pedido.id,
            "estado_nuevo": "PENDIENTE",
            "usuario_id": usuario_id,
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        }
        await manager.broadcast_pedido(pedido.id, evento, usuario_id)

        return result
    

    def get_all(self, usuario_id: int, roles: list[str], page: int = 1, size: int = 20) -> PaginatedPedidos:
        with PedidoUnitOfWork(self._session) as uow:
            stmt = select(Pedido).where(Pedido.deleted_at == None)
            if not any(r in ROLES_ADMIN_PEDIDOS for r in roles):
                stmt = stmt.where(Pedido.usuario_id == usuario_id)
            stmt = stmt.order_by(Pedido.created_at.desc())

            total = uow.pedidos.session.exec(
                select(func.count()).select_from(stmt.subquery())
            ).one()

            stmt = stmt.offset((page - 1) * size).limit(size)
            pedidos = uow.pedidos.session.exec(stmt).all()
            result = [self._pedido_to_out(p) for p in pedidos]
            pages = (total + size - 1) // size

        return PaginatedPedidos(items=result, total=total, page=page, size=size, pages=pages)


    def get_by_id(self, pedido_id: int, usuario_id: int, roles: list[str]) -> PedidoOut:
        with PedidoUnitOfWork(self._session) as uow:
            pedido = uow.pedidos.get_by_id(pedido_id)
            if not pedido:
                raise http_error(404, "Pedido no encontrado", "NOT_FOUND", "pedido_id")
            is_admin = any(r in ROLES_ADMIN_PEDIDOS for r in roles)
            if not is_admin and pedido.usuario_id != usuario_id:
                raise http_error(404, "Pedido no encontrado", "NOT_FOUND", "pedido_id")
            result = self._pedido_to_out(pedido)
        return result


    def get_historial(self, pedido_id: int, usuario_id: int, roles: list[str]) -> list[HistorialOut]:
        with PedidoUnitOfWork(self._session) as uow:
            pedido = self._get_or_404(uow, pedido_id)
            is_admin = any(r in ROLES_ADMIN_PEDIDOS for r in roles)
            if not is_admin and pedido.usuario_id != usuario_id:
                raise http_error(404, "Pedido no encontrado", "NOT_FOUND", "pedido_id")
            historial = uow.pedidos.session.exec(
                select(HistorialEstadoPedido)
                .where(HistorialEstadoPedido.pedido_id == pedido_id)
                .order_by(HistorialEstadoPedido.created_at.asc())
            ).all()
            result = [HistorialOut.model_validate(h) for h in historial]
        return result


    async def avanzar_estado(self, pedido_id: int, data: AvanceEstadoRequest, usuario_id: int, roles: list[str]) -> PedidoOut:
        with PedidoUnitOfWork(self._session) as uow:
            pedido = self._get_or_404(uow, pedido_id)
            estado_actual = pedido.estado_codigo
            estado_destino = data.estado_hacia

            if estado_destino not in TRANSICIONES_VALIDAS.get(estado_actual, []):
                raise http_error(400, f"No se puede pasar de {estado_actual} a {estado_destino}", "INVALID_STATE", "nuevo_estado")

            es_cliente = "CLIENT" in roles
            if es_cliente:
                if estado_destino != "CANCELADO":
                    raise http_error(403, "Como cliente solo puedes cancelar pedidos", "FORBIDDEN")
                if estado_actual not in ["PENDIENTE", "CONFIRMADO"]:
                    raise http_error(400, "Solo puedes cancelar pedidos pendientes o confirmados", "INVALID_STATE")

            if estado_destino == "CANCELADO" and not data.motivo:
                raise http_error(400, "Motivo obligatorio para cancelar un pedido", "MOTIVE_REQUIRED", "motivo")

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
            pedido_usuario_id = pedido.usuario_id
            result = self._pedido_to_out(pedido)


        evento = {
            "event": EVENTOS_WS.get(estado_destino, "estado_cambiado"),
            "pedido_id": pedido_id,
            "estado_anterior": estado_actual,
            "estado_nuevo": estado_destino,
            "usuario_id": usuario_id,
            "motivo": data.motivo,
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        }
        await manager.broadcast_pedido(pedido_id, evento, pedido_usuario_id)

        return result


    def delete(self, pedido_id: int) -> None:
        with PedidoUnitOfWork(self._session) as uow:
            pedido = self._get_or_404(uow, pedido_id)
            uow.pedidos.soft_delete(pedido)
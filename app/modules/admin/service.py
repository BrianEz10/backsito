from datetime import datetime, timezone
from sqlalchemy import func
from sqlmodel import Session, select
from app.modules.auth.models import Usuario
from app.modules.pedidos.models import DetallePedido, Pedido
from app.modules.productos.models import Producto
from app.modules.roles.associations import UsuarioRol
from app.modules.admin.schemas import AdminUserOut, AdminUserUpdate, AdminAsignarRolesRequest, DashboardResponse, EstadoCount, PedidoReciente, ProductoVendido
from app.modules.admin.uow import AdminUnitOfWork
from app.core.errors import http_error


class AdminService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _user_to_out(self, user: Usuario) -> AdminUserOut:
        roles = [rol.codigo for rol in user.roles]
        return AdminUserOut(
            id=user.id,
            email=user.email,
            nombre=user.nombre,
            apellido=user.apellido,
            celular=user.celular,
            roles=roles,
            created_at=user.created_at,
            deleted_at=user.deleted_at,
        )

    def listar(self, offset: int = 0, limit: int = 20, rol: str | None = None) -> list[AdminUserOut]:
        with AdminUnitOfWork(self._session) as uow:
            stmt = select(Usuario).where(Usuario.deleted_at == None)
            if rol:
                stmt = stmt.join(UsuarioRol, UsuarioRol.usuario_id == Usuario.id)
                stmt = stmt.where(UsuarioRol.rol_codigo == rol)
            stmt = stmt.offset(offset).limit(limit)
            usuarios = uow._session.exec(stmt).all()
            result = [self._user_to_out(u) for u in usuarios]
        return result

    def get_by_id(self, usuario_id: int) -> AdminUserOut:
        with AdminUnitOfWork(self._session) as uow:
            user = uow.usuarios.get_by_id(usuario_id)
            if not user or user.deleted_at is not None:
                raise http_error(404, "Usuario no encontrado", "NOT_FOUND", "usuario_id")
            result = self._user_to_out(user)
        return result

    def update(self, usuario_id: int, data: AdminUserUpdate) -> AdminUserOut:
        with AdminUnitOfWork(self._session) as uow:
            user = uow.usuarios.get_by_id(usuario_id)
            if not user or user.deleted_at is not None:
                raise http_error(404, "Usuario no encontrado", "NOT_FOUND", "usuario_id")
            patch = data.model_dump(exclude_unset=True)
            for field, value in patch.items():
                setattr(user, field, value)
            uow.usuarios.add(user)
            result = self._user_to_out(user)
        return result

    def asignar_roles(self, usuario_id: int, data: AdminAsignarRolesRequest) -> AdminUserOut:
        with AdminUnitOfWork(self._session) as uow:
            user = uow.usuarios.get_by_id(usuario_id)
            if not user or user.deleted_at is not None:
                raise http_error(404, "Usuario no encontrado", "NOT_FOUND", "usuario_id")
            old_links = uow._session.exec(
                select(UsuarioRol).where(UsuarioRol.usuario_id == usuario_id)
            ).all()
            for link in old_links:
                uow._session.delete(link)
            for rol_codigo in data.roles:
                rol = uow.roles.get_by_id(rol_codigo)
                if not rol:
                    raise http_error(400, f"Rol {rol_codigo} no existe", "NOT_FOUND", "roles")
                uow._session.add(UsuarioRol(usuario_id=usuario_id, rol_codigo=rol_codigo))
            uow._session.flush()
            result = self._user_to_out(user)
        return result

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

        return DashboardResponse(
            total_pedidos=total_pedidos,
            ingresos_totales=ingresos_totales,
            pedidos_por_estado=pedidos_por_estado,
            productos_mas_vendidos=productos_mas_vendidos,
            pedidos_recientes=pedidos_recientes,
        )

    def delete(self, usuario_id: int, current_user_id: int) -> None:
        if usuario_id == current_user_id:
            raise http_error(400, "No puedes eliminarte a ti mismo", "BAD_REQUEST")
        with AdminUnitOfWork(self._session) as uow:
            user = uow.usuarios.get_by_id(usuario_id)
            if not user or user.deleted_at is not None:
                raise http_error(404, "Usuario no encontrado", "NOT_FOUND", "usuario_id")
            user.deleted_at = datetime.now(timezone.utc)
from datetime import datetime, timezone
from sqlmodel import Session, select
from app.modules.auth.models import Usuario
from app.modules.roles.associations import UsuarioRol
from app.modules.admin.schemas import AdminUserOut, AdminUserUpdate, AdminAsignarRolesRequest
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
                raise HTTPException(404, "Usuario no encontrado")
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

    def delete(self, usuario_id: int, current_user_id: int) -> None:
        if usuario_id == current_user_id:
            raise http_error(400, "No puedes eliminarte a ti mismo", "BAD_REQUEST")
        with AdminUnitOfWork(self._session) as uow:
            user = uow.usuarios.get_by_id(usuario_id)
            if not user or user.deleted_at is not None:
                raise http_error(404, "Usuario no encontrado", "NOT_FOUND", "usuario_id")
            user.deleted_at = datetime.now(timezone.utc)
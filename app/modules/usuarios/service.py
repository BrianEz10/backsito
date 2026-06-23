from sqlmodel import Session
from app.modules.usuarios.models import Usuario
from app.modules.usuarios.schemas import PaginatedUsuarios, UsuarioOut, UsuarioUpdate, AsignarRolesRequest
from app.modules.usuarios.uow import UsuarioUnitOfWork
from app.core.errors import http_error


class UsuarioService:
    def __init__(self, session: Session) -> None:
        self._session = session


    def _user_to_out(self, user: Usuario) -> UsuarioOut:
        roles = [rol.codigo for rol in user.roles]
        return UsuarioOut(
            id=user.id,
            email=user.email,
            nombre=user.nombre,
            apellido=user.apellido,
            celular=user.celular,
            roles=roles,
            created_at=user.created_at,
            deleted_at=user.deleted_at,
        )


    def listar(self, page: int = 1, size: int = 20, rol: str | None = None) -> PaginatedUsuarios:
        with UsuarioUnitOfWork(self._session) as uow:
            total = uow.usuarios.count_filtered(rol)
            offset = (page - 1) * size
            usuarios = uow.usuarios.find_all_filtered(rol, offset, size)
            result = [self._user_to_out(u) for u in usuarios]
            pages = (total + size - 1) // size
        return PaginatedUsuarios(items=result, total=total, page=page, size=size, pages=pages)


    def get_by_id(self, usuario_id: int) -> UsuarioOut:
        with UsuarioUnitOfWork(self._session) as uow:
            user = uow.usuarios.get_by_id(usuario_id)
            if not user or user.deleted_at is not None:
                raise http_error(404, "Usuario no encontrado", "NOT_FOUND", "usuario_id")
            result = self._user_to_out(user)
        return result


    def update(self, usuario_id: int, data: UsuarioUpdate) -> UsuarioOut:
        with UsuarioUnitOfWork(self._session) as uow:
            user = uow.usuarios.get_by_id(usuario_id)
            if not user or user.deleted_at is not None:
                raise http_error(404, "Usuario no encontrado", "NOT_FOUND", "usuario_id")
            patch = data.model_dump(exclude_unset=True)
            for field, value in patch.items():
                setattr(user, field, value)
            uow.usuarios.add(user)
            result = self._user_to_out(user)
        return result


    def asignar_roles(self, usuario_id: int, data: AsignarRolesRequest) -> UsuarioOut:
        with UsuarioUnitOfWork(self._session) as uow:
            user = uow.usuarios.get_by_id(usuario_id)
            if not user or user.deleted_at is not None:
                raise http_error(404, "Usuario no encontrado", "NOT_FOUND", "usuario_id")
            old_links = uow.usuarios.get_roles_links(usuario_id)
            for link in old_links:
                uow.usuarios.delete_rol_link(link)
            for rol_codigo in data.roles:
                rol = uow.roles.get_by_id(rol_codigo)
                if not rol:
                    raise http_error(400, f"Rol {rol_codigo} no existe", "NOT_FOUND", "roles")
                uow.usuarios.add_rol_link(usuario_id, rol_codigo)
            result = self._user_to_out(user)
        return result


    def delete(self, usuario_id: int, current_user_id: int) -> None:
        if usuario_id == current_user_id:
            raise http_error(400, "No puedes eliminarte a ti mismo", "BAD_REQUEST")
        with UsuarioUnitOfWork(self._session) as uow:
            user = uow.usuarios.get_by_id(usuario_id)
            if not user or user.deleted_at is not None:
                raise http_error(404, "Usuario no encontrado", "NOT_FOUND", "usuario_id")
            uow.usuarios.soft_delete(user)
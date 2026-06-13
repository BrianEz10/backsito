from sqlalchemy import func
from sqlmodel import Session, select
from app.modules.usuarios.models import Usuario
from app.modules.roles.associations import UsuarioRol
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
            stmt = select(Usuario).where(Usuario.deleted_at == None)
            if rol:
                stmt = stmt.join(UsuarioRol, UsuarioRol.usuario_id == Usuario.id)
                stmt = stmt.where(UsuarioRol.rol_codigo == rol)

            total = uow._session.exec(
                select(func.count()).select_from(stmt.subquery())
            ).one()

            stmt = stmt.offset((page - 1) * size).limit(size)
            usuarios = uow._session.exec(stmt).all()
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
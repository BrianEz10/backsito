from sqlalchemy import func
from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.roles.associations import UsuarioRol
from app.modules.usuarios.models import Usuario


class UsuarioRepository(BaseRepository[Usuario]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Usuario)

        
    def get_by_email(self, email: str) -> Usuario | None:
        stmt = select(Usuario).where(
            Usuario.email == email, Usuario.deleted_at == None
        )
        return self.session.exec(stmt).first()
    
    
    def get_by_email_with_roles(self, email: str) -> Usuario | None:
        from sqlalchemy.orm import selectinload
        return self.session.exec(
            select(Usuario)
            .where(Usuario.email == email, Usuario.deleted_at == None)
            .options(selectinload(Usuario.roles))
        ).first()


    def find_all_filtered(self, rol: str | None = None, offset: int = 0, limit: int = 20) -> list[Usuario]:
        stmt = select(Usuario).where(Usuario.deleted_at == None)
        if rol:
            stmt = stmt.join(UsuarioRol, UsuarioRol.usuario_id == Usuario.id).where(UsuarioRol.rol_codigo == rol)
        stmt = stmt.offset(offset).limit(limit)
        return list(self.session.exec(stmt).all())


    def count_filtered(self, rol: str | None = None) -> int:
        stmt = select(func.count()).select_from(Usuario).where(Usuario.deleted_at == None)
        if rol:
            stmt = stmt.join(UsuarioRol, UsuarioRol.usuario_id == Usuario.id).where(UsuarioRol.rol_codigo == rol)
        return self.session.exec(stmt).one()


    def get_roles_links(self, usuario_id: int) -> list[UsuarioRol]:
        return list(self.session.exec(
            select(UsuarioRol).where(UsuarioRol.usuario_id == usuario_id)
        ).all())


    def delete_rol_link(self, link: UsuarioRol) -> None:
        self.session.delete(link)
        self.session.flush()


    def add_rol_link(self, usuario_id: int, rol_codigo: str) -> None:
        self.session.add(UsuarioRol(usuario_id=usuario_id, rol_codigo=rol_codigo))
        self.session.flush()
from sqlmodel import select
from app.core.repository import BaseRepository
from app.modules.direcciones.models import DireccionEntrega

class DireccionRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session, DireccionEntrega)

    def get_by_usuario(self, usuario_id: int) -> list[DireccionEntrega]:
        return list(self.session.exec(
            select(DireccionEntrega).where(
                DireccionEntrega.usuario_id == usuario_id,
                DireccionEntrega.deleted_at == None,
            )
        ).all())
    
    def get_principal(self, usuario_id: int) -> DireccionEntrega | None:
        return self.session.exec(
            select(DireccionEntrega).where(
                DireccionEntrega.usuario_id == usuario_id,
                DireccionEntrega.es_principal == True,
                DireccionEntrega.deleted_at == None,
            )
        ).first()
    
    def get_by_id(self, id: int) -> DireccionEntrega | None:
        return self.session.exec(
            select(DireccionEntrega).where(
                DireccionEntrega.id == id, DireccionEntrega.deleted_at == None
            )
        ).first()
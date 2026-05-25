from sqlmodel import Session
from app.core.repository import BaseRepository
from app.modules.forma_pago.models import FormaPago

class FormaPagoRepository(BaseRepository[FormaPago]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, FormaPago)
        
    def get_by_codigo(self, codigo: str) -> FormaPago | None:
        return self.session.get(FormaPago, codigo)
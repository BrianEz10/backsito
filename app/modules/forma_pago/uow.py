from sqlmodel import Session
from app.core.uow import UnitOfWork
from app.modules.forma_pago.repository import FormaPagoRepository

class FormaPagoUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.formas_pago = FormaPagoRepository(session)
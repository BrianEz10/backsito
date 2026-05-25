from fastapi import HTTPException
from sqlmodel import Session
from app.modules.forma_pago.models import FormaPago
from app.modules.forma_pago.schemas import FormaPagoCreate, FormaPagoUpdate, FormaPagoOut
from app.modules.forma_pago.uow import FormaPagoUnitOfWork

class FormaPagoService:
    def __init__(self, session: Session) -> None:
        self._session = session
    
    def _get_or_404(self, uow: FormaPagoUnitOfWork, codigo: str) -> FormaPago:
        fp = uow.formas_pago.get_by_codigo(codigo)
        if not fp:
            raise HTTPException(404, f"Forma de pago {codigo} no encontrada")
        return fp
    
    def get_all(self) -> list[FormaPagoOut]:
        with FormaPagoUnitOfWork(self._session) as uow:
            formas = uow.formas_pago.get_all()
            result = [FormaPagoOut.model_validate(f) for f in formas]
        return result
    
    def get_by_codigo(self, codigo: str) -> FormaPagoOut:
        with FormaPagoUnitOfWork(self._session) as uow:
            fp = self._get_or_404(uow, codigo)
            result = FormaPagoOut.model_validate(fp)
        return result
    
    def create(self, data: FormaPagoCreate) -> FormaPagoOut:
        with FormaPagoUnitOfWork(self._session) as uow:
            existing = uow.formas_pago.get_by_codigo(data.codigo)
            if existing:
                raise HTTPException(409, "Ya existe una forma de pago con ese codigo")
            fp = FormaPago.model_validate(data)
            uow.formas_pago.add(fp)
            result = FormaPagoOut.model_validate(fp)
        return result
    
    def update(self, codigo: str, data: FormaPagoUpdate) -> FormaPagoOut:
        with FormaPagoUnitOfWork(self._session) as uow:
            fp = self._get_or_404(uow, codigo)
            patch = data.model_dump(exclude_unset=True)
            for field, value in patch.items():
                setattr(fp, field, value)
            uow.formas_pago.add(fp)
            result = FormaPagoOut.model_validate(fp)
        return result
    
    def delete(self, codigo: str) -> None:
        with FormaPagoUnitOfWork(self._session) as uow:
            fp = self._get_or_404(uow, codigo)
            uow.formas_pago.delete(fp)
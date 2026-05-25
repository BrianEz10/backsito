from fastapi import HTTPException, status
from sqlmodel import Session
from app.modules.estado_pedido.models import EstadoPedido
from app.modules.estado_pedido.schemas import EstadoPedidoCreate, EstadoPedidoUpdate, EstadoPedidoOut
from app.modules.estado_pedido.uow import EstadoPedidoUnitOfWork

class EstadoPedidoService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _get_or_404(self, uow: EstadoPedidoUnitOfWork, codigo: str) -> EstadoPedido:
        estado = uow.estados.get_by_codigo(codigo)
        if not estado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Estado {codigo} no encontrado"
            )
        return estado
    
    def get_all(self) -> list[EstadoPedidoOut]:
        with EstadoPedidoUnitOfWork(self._session) as uow:
            estados = uow.estados.get_all()
            result = [EstadoPedidoOut.model_validate(e) for e in estados]
        return result
    
    def get_by_codigo(self, codigo: str) -> EstadoPedidoOut:
        with EstadoPedidoUnitOfWork(self._session) as uow:
            estado = self._get_or_404(uow, codigo)
            result = EstadoPedidoOut.model_validate(estado)
        return result
    
    def create(self, data: EstadoPedidoCreate) -> EstadoPedidoOut:
        with EstadoPedidoUnitOfWork(self._session) as uow:
            existing = uow.estados.get_by_codigo(data.codigo)
            if existing:
                raise HTTPException(409, "Ya existe un estado con ese codigo")
            estado = EstadoPedido.model_validate(data)
            uow.estados.add(estado)
            result = EstadoPedidoOut.model_validate(estado)
        return result
    
    def update(self, codigo: str, data: EstadoPedidoUpdate) -> EstadoPedidoOut:
        with EstadoPedidoUnitOfWork(self._session) as uow:
            estado = self._get_or_404(uow, codigo)
            patch = data.model_dump(exclude_unset=True)
            for field, value in patch.items():
                setattr(estado, field, value)
            uow.estados.add(estado)
            result = EstadoPedidoOut.model_validate(estado)
        return result
    
    def delete(self, codigo: str) -> None:
        with EstadoPedidoUnitOfWork(self._session) as uow:
            estado = self._get_or_404(uow, codigo)
            uow.estados.delete(estado)
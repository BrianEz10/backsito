from typing import TypeVar, Generic, Type, Sequence
from sqlmodel import Session, SQLModel, select
from sqlalchemy import func

ModelT = TypeVar("ModelT", bound=SQLModel)

class BaseRepository(Generic[ModelT]):
    def __init__(self, session: Session, model: Type[ModelT]) -> None:
        self.session = session
        self.model = model
    
    def get_by_id(self, record_id: int) -> ModelT | None:
        return self.session.get(self.model, record_id)
    
    def get_all(self, offset: int = 0, limit: int = 20) -> Sequence[ModelT]:
        return self.session.exec(
            select(self.model).offset(offset).limit(limit)
        ).all()
    
    def count(self) -> int:
        return self.session.exec(
            select(func.count()).select_from(self.model)
        ).one()

    def add(self, instance: ModelT) -> ModelT:
        self.session.add(instance)
        self.session.flush()
        self.session.refresh(instance)
        return instance
    
    #Faltan crear funciones, "soft-delete", "update"
    def delete(self, instance: ModelT) -> None:
        self.session.delete(instance)
        self.session.flush()
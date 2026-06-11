from typing import Annotated
from fastapi import APIRouter, Depends
from app.core.database import SessionDep
from app.core.deps import require_role
from app.modules.usuarios.models import Usuario
from app.modules.admin.schemas import DashboardResponse
from app.modules.admin.service import AdminService

router = APIRouter(prefix="/admin", tags=["admin"])


def get_admin_service(session: SessionDep) -> AdminService:
    return AdminService(session)


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(_admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], svc: AdminService = Depends(get_admin_service)) -> DashboardResponse:
    return svc.get_dashboard()
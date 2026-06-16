from typing import Annotated
from fastapi import Depends, Request
from sqlmodel import select
from sqlalchemy.orm import selectinload
from app.core.database import SessionDep
from app.modules.usuarios.models import Usuario
from app.core.security import decode_access_token
from app.core.errors import http_error

async def get_current_user(request: Request, session: SessionDep) -> Usuario:
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
    if not token:
        raise http_error(401, "No autenticado", "UNAUTHORIZED")
    payload = decode_access_token(token)

    if payload is None:
        raise http_error(401, "Token invalido", "UNAUTHORIZED")
    email: str = payload.get("sub")
    if email is None:
        raise http_error(401, "Token invalido", "UNAUTHORIZED")
    user = session.exec(
        select(Usuario)
        .where(Usuario.email == email, Usuario.deleted_at == None)
        .options(selectinload(Usuario.roles))
    ).first()
    if not user:
        raise http_error(401, "Usuario no encontrado", "UNAUTHORIZED")
    return user

CurrentUser = Annotated[Usuario, Depends(get_current_user)]

async def get_current_active_user(current_user: CurrentUser) -> Usuario:
    if current_user.deleted_at is not None:
        raise http_error(400, "Cuenta de usuario desactivada", "INACTIVE_ACCOUNT")
    return current_user

def require_role(allowed_roles: list[str]):
    async def role_checker(current_user: Annotated[Usuario, Depends(get_current_active_user)]) -> Usuario:
        user_roles = [rol.codigo for rol in current_user.roles]
        if not any(rol in allowed_roles for rol in user_roles):
            raise http_error(403, "Permisos insuficientes", "FORBIDDEN")
        return current_user
    return role_checker
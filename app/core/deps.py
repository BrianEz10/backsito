from typing import Annotated
from fastapi import Depends, HTTPException, status, Request
from sqlmodel import select
from sqlalchemy.orm import selectinload
from app.core.database import SessionDep
from app.modules.auth.models import Usuario
from app.core.security import decode_access_token

async def get_current_user(
        request: Request, session: SessionDep
) -> Usuario:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado"
        )
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido"
        )
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido"
        )
    user = session.exec(
        select(Usuario)
        .where(Usuario.email == email, Usuario.deleted_at == None)
        .options(selectinload(Usuario.roles))
    ).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado"
        )
    return user

CurrentUser = Annotated[Usuario, Depends(get_current_user)]

async def get_current_active_user(
    current_user: CurrentUser,
) -> Usuario:
    if current_user.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cuenta de usuario desactivada")
    return current_user

def require_role(allowed_roles: list[str]):
    async def role_checker(
            current_user: Annotated[Usuario, Depends(get_current_active_user)],
    ) -> Usuario:
        user_roles = [rol.codigo for rol in current_user.roles]
        if not any(rol in allowed_roles for rol in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes",
            )
        return current_user
    return role_checker
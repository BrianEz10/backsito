import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Response
from sqlmodel import Session
from app.modules.auth.models import Usuario
from app.modules.auth.schemas import UserCreate
from app.modules.auth.uow import AuthUnitOfWork
from app.modules.auth.refresh_models import RefreshToken
from app.modules.roles.associations import UsuarioRol
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings

class AuthService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._refresh_expire_days = 7

    def _utcnow(self) -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None) 
    
    def _hash_token(self, token_str: str) -> str:
        return hashlib.sha256(token_str.encode()).hexdigest()
    
    def _create_refresh_token(self, uow: AuthUnitOfWork, usuario_id: int) -> str:
        token_str = secrets.token_urlsafe(32)
        token_hash = self._hash_token(token_str)
        obj = RefreshToken(usuario_id=usuario_id, token_hash=token_hash, expires_at= self._utcnow()  + timedelta(days=self._refresh_expire_days))
        uow._session.add(obj)
        return token_str
    
    def _set_auth_cookies(self, response: Response, access_token: str, refresh_token: str) -> None:
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax",
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            max_age=self._refresh_expire_days * 24 * 60 * 60,
            samesite="lax",
        )
    
    def create_token(self, user: Usuario) -> str:
        roles = [rol.codigo for rol in user.roles]
        return create_access_token({"sub": user.email, "roles": roles})
    
    def register(self, data: UserCreate, response: Response) -> dict:
        with AuthUnitOfWork(self._session) as uow:
            existing = uow.usuarios.get_by_email(data.email)
            if existing:
                raise HTTPException(409, "Este email ya fue registrado")
            hashed = hash_password(data.password)
            user = Usuario(
                email=data.email,
                nombre=data.nombre,
                apellido=data.apellido,
                celular=data.celular,
                hashed_password=hashed,
            )
            uow.usuarios.add(user)
            link = UsuarioRol(usuario_id=user.id, rol_codigo="CLIENT")
            uow._session.add(link)
            refresh_token_str = self._create_refresh_token(uow, user.id)
            access_token = self.create_token(user)
        self._set_auth_cookies(response, access_token, refresh_token_str)
        return {"access_token": access_token, "token_type": "bearer"}
    
    def login(self, form_data, response: Response) -> dict:
        with AuthUnitOfWork(self._session) as uow:
            user = uow.usuarios.get_by_email(form_data.username)
            if not user or not verify_password(form_data.password, user.hashed_password):
                raise HTTPException(401, "Credenciales invalidas")
            refresh_token_str = self._create_refresh_token(uow, user.id)
            access_token = self.create_token(user)
        self._set_auth_cookies(response, access_token, refresh_token_str)
        return {"access_token": access_token, "token_type": "bearer"}
    
    def refresh(self, refresh_token_str: str, response: Response) -> dict:
        with AuthUnitOfWork(self._session) as uow:
            token_hash = self._hash_token(refresh_token_str)
            token = uow.refresh_tokens.get_by_token_hash(token_hash)
            now_utc = self._utcnow()
            if not token or token.expires_at < now_utc or token.revoked_at is not None:
                raise HTTPException(401, "Refresh token invalido o expirado")
            token.revoked_at = now_utc
            new_refresh_str = self._create_refresh_token(uow, token.usuario_id)
            user = uow.usuarios.get_by_id(token.usuario_id)
            access_token = self.create_token(user)
        self._set_auth_cookies(response, access_token, new_refresh_str)
        return {"access_token": access_token, "token_type": "bearer"}
    
    def logout(self, refresh_token_str: str, response: Response) -> dict:
        if refresh_token_str:
            with AuthUnitOfWork(self._session) as uow:
                token_hash = self._hash_token(refresh_token_str)
                token = uow.refresh_tokens.get_by_token_hash(token_hash)
                if token:
                    token.revoked_at = self._utcnow()
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return {"message": "Session cerrada"}
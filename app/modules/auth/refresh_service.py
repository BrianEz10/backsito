from datetime import datetime, timedelta, timezone
import secrets
import hashlib
from app.modules.auth.refresh_models import RefreshToken
from app.modules.auth.refresh_repository import RefreshTokenRepository

#RefreshTokenService existe pero está huérfano(pegarle un perma),  cambiar manga de giles.

class RefreshTokenService:
    def __init__(self, repo: RefreshTokenRepository):
        self.repo = repo
        self.REFRESH_EXPIRE_DAYS = 7

    def _hash_token(self, token_str: str) -> str:
        return hashlib.sha256(token_str.encode()).hexdigest()

    def create(self, usuario_id: int) -> str:
        token_str = secrets.token_urlsafe(32)
        token_hash = self._hash_token(token_str)
        obj = RefreshToken(
            usuario_id=usuario_id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(days=self.REFRESH_EXPIRE_DAYS)
        )
        self.repo.create(obj)
        return token_str

    def validate(self, token_str: str) -> RefreshToken | None:
        token_hash = self._hash_token(token_str)
        token = self.repo.get_by_token_hash(token_hash)
        if not token:
            return None
        if token.expires_at < datetime.now(timezone.utc):
            return None
        if token.revoked_at is not None:
            return None
        return token

    def revoke(self, token_str: str) -> None:
        token_hash = self._hash_token(token_str)
        token = self.repo.get_by_token_hash(token_hash)
        if token:
            token.revoked_at = datetime.now(timezone.utc)
            self.repo.update(token)
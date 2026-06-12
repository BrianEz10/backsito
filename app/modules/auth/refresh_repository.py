from sqlmodel import select
from app.core.repository import BaseRepository
from app.modules.auth.refresh_models import RefreshToken

class RefreshTokenRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session, RefreshToken)

    def get_by_token_hash(self, token_hash: str) -> RefreshToken | None:
        return self.session.exec(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.deleted_at == None
            )
        ).first()
from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from app.core.deps import CurrentUser
from app.core.database import SessionDep
from app.modules.auth.schemas import UserCreate, UserMeOut
from app.modules.auth.service import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])

def get_auth_service(session: SessionDep) -> AuthService:
    return AuthService(session)

@router.post("/register", status_code=201)
def register(data: UserCreate, response: Response, svc: AuthService = Depends(get_auth_service)) -> dict:
    return svc.register(data, response)


@router.post("/token")
def login(response: Response, form: OAuth2PasswordRequestForm = Depends(), svc: AuthService = Depends(get_auth_service)) -> dict:
    return svc.login(form, response)


@router.get("/me", response_model=UserMeOut)
def me(user: CurrentUser) -> UserMeOut:
    roles = [rol.codigo for rol in user.roles]
    return UserMeOut(
        id=user.id,
        email=user.email,
        nombre=user.nombre,
        apellido=user.apellido,
        celular=user.celular,
        roles=roles,
    )


@router.post("/logout")
def logout(response: Response, request: Request, svc: AuthService = Depends(get_auth_service)) -> dict:
    refresh_token_str = request.cookies.get("refresh_token", "")
    return svc.logout(refresh_token_str, response)


@router.post("/refresh")
def refresh(response: Response, request: Request, svc: AuthService = Depends(get_auth_service)) -> dict:
    refresh_token_str = request.cookies.get("refresh_token", "")
    return svc.refresh(refresh_token_str, response)
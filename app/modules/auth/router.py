from fastapi import APIRouter, Depends, Request, Response, status
from app.core.deps import CurrentUser
from app.core.database import SessionDep
from app.modules.auth.schemas import LoginRequest, RegisterRequest, UserResponse, TokenResponse
from app.modules.auth.service import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])

def get_auth_service(session: SessionDep) -> AuthService:
    return AuthService(session)

@router.post("/register", status_code=201, response_model=TokenResponse)
def register(data: RegisterRequest, response: Response, svc: AuthService = Depends(get_auth_service)) -> TokenResponse:
    return svc.register(data, response)


@router.post("/login", response_model=TokenResponse)
def login(response: Response, data: LoginRequest, svc: AuthService = Depends(get_auth_service)) -> TokenResponse:
    return svc.login(data, response)


@router.get("/me", response_model=UserResponse)
def me(user: CurrentUser) -> UserResponse:
    roles = [rol.codigo for rol in user.roles]
    return UserResponse(
        id=user.id,
        email=user.email,
        nombre=user.nombre,
        apellido=user.apellido,
        celular=user.celular,
        roles=roles,
        created_at=user.created_at
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response, request: Request, svc: AuthService = Depends(get_auth_service)) -> None:
    refresh_token_str = request.cookies.get("refresh_token", "")
    return svc.logout(refresh_token_str, response)


@router.post("/refresh", response_model=TokenResponse)
def refresh(response: Response, request: Request, svc: AuthService = Depends(get_auth_service)) -> TokenResponse:
    refresh_token_str = request.cookies.get("refresh_token", "")
    return svc.refresh(refresh_token_str, response)
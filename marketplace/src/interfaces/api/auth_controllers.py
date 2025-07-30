"""Authentication API controllers."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.application.services import AuthenticationService
from src.auth.infrastructure.sql_repositories import SQLSessionRepository, SQLTokenRepository
from src.shared.infrastructure.config import settings
from src.shared.infrastructure.database import get_db_session
from src.users.infrastructure.sql_repositories import SQLUserRepository

# Security scheme
security = HTTPBearer()

# Pydantic models for API
class LoginRequest(BaseModel):
    """Request model for user login."""
    email: str
    password: str

class TokenResponse(BaseModel):
    """Response model for authentication tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class RefreshTokenRequest(BaseModel):
    """Request model for token refresh."""
    refresh_token: str

class ChangePasswordRequest(BaseModel):
    """Request model for password change."""
    old_password: str
    new_password: str

class UserInfoResponse(BaseModel):
    """Response model for user information."""
    id: str
    email: str
    first_name: str
    last_name: str
    is_active: bool

# Dependency injection
def get_auth_service(session: AsyncSession = Depends(get_db_session)) -> AuthenticationService:
    """Get authentication service instance."""
    user_repo = SQLUserRepository(session)
    token_repo = SQLTokenRepository(session)
    session_repo = SQLSessionRepository(session)
    
    return AuthenticationService(
        user_repository=user_repo,
        token_repository=token_repo,
        session_repository=session_repo,
        secret_key=settings.secret_key,
        algorithm=settings.algorithm,
        access_token_expire_minutes=settings.access_token_expire_minutes,
    )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthenticationService = Depends(get_auth_service),
) -> Optional[dict]:
    """Get current authenticated user."""
    token = credentials.credentials
    user = await auth_service.get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Router
router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    request: LoginRequest,
    http_request: Request,
    auth_service: AuthenticationService = Depends(get_auth_service),
) -> TokenResponse:
    """Authenticate user and return token pair."""
    try:
        # Get client IP and user agent
        client_ip = http_request.client.host if http_request.client else "unknown"
        user_agent = http_request.headers.get("user-agent", "unknown")
        
        token_pair = await auth_service.login(
            email=request.email,
            password=request.password,
            ip_address=client_ip,
            user_agent=user_agent,
        )
        
        return TokenResponse(
            access_token=token_pair.access_token.value,
            refresh_token=token_pair.refresh_token.value,
            expires_in=settings.access_token_expire_minutes * 60,  # Convert to seconds
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AuthenticationService = Depends(get_auth_service),
) -> TokenResponse:
    """Refresh access token using refresh token."""
    try:
        token_pair = await auth_service.refresh_token(request.refresh_token)
        
        return TokenResponse(
            access_token=token_pair.access_token.value,
            refresh_token=token_pair.refresh_token.value,
            expires_in=settings.access_token_expire_minutes * 60,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user: dict = Depends(get_current_user),
    auth_service: AuthenticationService = Depends(get_auth_service),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Logout user by revoking current token."""
    try:
        success = await auth_service.logout(credentials.credentials)
        if success:
            return {"message": "Successfully logged out"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to logout",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.post("/logout-all", status_code=status.HTTP_200_OK)
async def logout_all_sessions(
    current_user: dict = Depends(get_current_user),
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    """Logout user from all sessions."""
    try:
        success = await auth_service.logout_all_sessions(current_user["id"])
        if success:
            return {"message": "Successfully logged out from all sessions"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to logout from all sessions",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    """Change user password."""
    try:
        success = await auth_service.change_password(
            user_id=current_user["id"],
            old_password=request.old_password,
            new_password=request.new_password,
        )
        if success:
            return {"message": "Password changed successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to change password",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.get("/me", response_model=UserInfoResponse, status_code=status.HTTP_200_OK)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
) -> UserInfoResponse:
    """Get current user information."""
    return UserInfoResponse(
        id=current_user["id"],
        email=current_user["email"],
        first_name=current_user["first_name"],
        last_name=current_user["last_name"],
        is_active=current_user["is_active"],
    )

@router.post("/validate", status_code=status.HTTP_200_OK)
async def validate_token(
    current_user: dict = Depends(get_current_user),
):
    """Validate current access token."""
    return {
        "valid": True,
        "user_id": current_user["id"],
        "email": current_user["email"],
    } 
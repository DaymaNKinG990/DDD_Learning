"""Authentication API controllers."""

# Python imports
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

# Local imports
from src.auth.application.services import AuthenticationService
from src.auth.infrastructure.sql_repositories import SQLSessionRepository, SQLTokenRepository
from src.shared.infrastructure.config import settings
from src.shared.infrastructure.database import get_db_session
from src.users.infrastructure.sql_repositories import SQLUserRepository


# Security scheme
security = HTTPBearer()


# Pydantic models for API
class LoginRequest(BaseModel):
    """
    Request model for user login.

    Attributes:
        email (str): The email address of the user.
        password (str): The password of the user.
    """

    email: str
    password: str


class TokenResponse(BaseModel):
    """
    Response model for authentication tokens.

    Attributes:
        access_token (str): The access token.
        refresh_token (str): The refresh token.
        token_type (str): The type of token.
        expires_in (int): The expiration time of the access token in seconds.
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """
    Request model for token refresh.

    Attributes:
        refresh_token (str): The refresh token.
    """

    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """
    Request model for password change.

    Attributes:
        old_password (str): The old password.
        new_password (str): The new password.
    """

    old_password: str
    new_password: str


class UserInfoResponse(BaseModel):
    """
    Response model for user information.

    Attributes:
        id (str): The user ID.
        email (str): The email address of the user.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        is_active (bool): Whether the user is active.
    """

    id: str
    email: str
    first_name: str
    last_name: str
    is_active: bool


# Dependency injection
def get_auth_service(session: AsyncSession = Depends(get_db_session)) -> AuthenticationService:
    """
    Get authentication service instance.

    Args:
        session (AsyncSession): The database session.

    Returns:
        AuthenticationService: The authentication service instance.
    """
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
    """
    Get current authenticated user.

    Args:
        credentials (HTTPAuthorizationCredentials): The authorization credentials.
        auth_service (AuthenticationService): The authentication service.

    Returns:
        Optional[dict]: The current authenticated user.
    """
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
    """
    Authenticate user and return token pair.

    Args:
        request (LoginRequest): The login request.
        http_request (Request): The HTTP request.
        auth_service (AuthenticationService): The authentication service.

    Returns:
        TokenResponse: The token response.
    """
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
    """
    Refresh access token using refresh token.

    Args:
        request (RefreshTokenRequest): The refresh token request.
        auth_service (AuthenticationService): The authentication service.

    Returns:
        TokenResponse: The token response.
    """
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
) -> dict[str, str]:
    """
    Logout user by revoking current token.

    Args:
        current_user (dict): The current user.
        auth_service (AuthenticationService): The authentication service.
        credentials (HTTPAuthorizationCredentials): The authorization credentials.

    Returns:
        dict[str, str]: The logout response.
    """
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
) -> dict[str, str]:
    """
    Logout user from all sessions.

    Args:
        current_user (dict): The current user.
        auth_service (AuthenticationService): The authentication service.

    Returns:
        dict[str, str]: The logout response.
    """
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
) -> dict[str, str]:
    """Change user password.

    Args:
        request (ChangePasswordRequest): The change password request.
        current_user (dict): The current user.
        auth_service (AuthenticationService): The authentication service.

    Returns:
        dict[str, str]: The change password response.
    """
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
    """Get current user information.

    Args:
        current_user (dict): The current user.

    Returns:
        UserInfoResponse: The current user information.
    """
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
) -> dict[str, bool | str]:
    """Validate current access token.

    Args:
        current_user (dict): The current user.

    Returns:
        dict[str, bool | str]: The validation response.
    """
    return {
        "valid": True,
        "user_id": current_user["id"],
        "email": current_user["email"],
    } 
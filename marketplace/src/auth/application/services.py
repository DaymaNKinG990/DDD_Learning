"""Authentication application services."""

import uuid
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.auth.domain.entities import TokenPair, UserSession
from src.auth.domain.events import (
    FailedLoginAttempt,
    PasswordChanged,
    UserLoggedIn,
    UserLoggedOut,
)
from src.auth.domain.repositories import SessionRepository, TokenRepository
from src.auth.domain.value_objects import (
    AccessToken,
    RefreshToken,
    TokenId,
    TokenType,
)
from src.shared.application.event_handlers import EventHandler
from src.shared.domain.events import DomainEvent
from src.shared.domain.exceptions import BusinessRuleViolationError, EntityNotFoundError
from src.users.domain.entities import User
from src.users.domain.repositories import UserRepository
from src.users.domain.value_objects import Email, UserId

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthenticationService:
    """Service for user authentication."""
    
    def __init__(
        self,
        user_repository: UserRepository,
        token_repository: TokenRepository,
        session_repository: SessionRepository,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
        event_handler: Optional[EventHandler] = None,
    ):
        self.user_repository = user_repository
        self.token_repository = token_repository
        self.session_repository = session_repository
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        self.event_handler = event_handler
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT refresh token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user with email and password."""
        user = await self.user_repository.get_by_email(Email(value=email))
        if not user:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        return user
    
    async def login(
        self,
        email: str,
        password: str,
        ip_address: str,
        user_agent: str,
    ) -> TokenPair:
        """Authenticate user and create token pair."""
        user = await self.authenticate_user(email, password)
        if not user:
            # Publish failed login event
            if self.event_handler:
                event = FailedLoginAttempt(
                    aggregate_id=email,
                    email=email,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    reason="Invalid credentials",
                    timestamp=datetime.utcnow(),
                )
                await self.event_handler.handle(event)
            
            raise BusinessRuleViolationError("Invalid email or password")
        
        # Create token pair
        access_token_data = {"sub": user.id.value, "type": "access"}
        refresh_token_data = {"sub": user.id.value, "type": "refresh"}
        
        access_token_value = self.create_access_token(access_token_data)
        refresh_token_value = self.create_refresh_token(refresh_token_data)
        
        access_token = AccessToken.create(access_token_value, self.access_token_expire_minutes)
        refresh_token = RefreshToken.create(refresh_token_value, self.refresh_token_expire_days)
        
        token_pair = TokenPair(
            id=TokenId(value=f"token_{uuid.uuid4().hex}"),
            user_id=user.id,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type=TokenType.ACCESS,
        )
        
        saved_token_pair = await self.token_repository.save(token_pair)
        
        # Create session
        session = UserSession(
            id=TokenId(value=f"session_{uuid.uuid4().hex}"),
            user_id=user.id,
            refresh_token=refresh_token,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        await self.session_repository.save(session)
        
        # Publish login event
        if self.event_handler:
            event = UserLoggedIn(
                aggregate_id=user.id.value,
                user_id=user.id.value,
                ip_address=ip_address,
                user_agent=user_agent,
                timestamp=datetime.utcnow(),
            )
            await self.event_handler.handle(event)
        
        return saved_token_pair
    
    async def refresh_token(self, refresh_token: str) -> TokenPair:
        """Refresh access token using refresh token."""
        # Verify refresh token
        payload = self.verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise BusinessRuleViolationError("Invalid refresh token")
        
        user_id = payload.get("sub")
        if not user_id:
            raise BusinessRuleViolationError("Invalid token payload")
        
        # Check if token exists in repository
        token_pair = await self.token_repository.get_by_refresh_token(refresh_token)
        if not token_pair or not token_pair.is_valid:
            raise BusinessRuleViolationError("Invalid or expired refresh token")
        
        # Create new access token
        access_token_data = {"sub": user_id, "type": "access"}
        new_access_token_value = self.create_access_token(access_token_data)
        new_access_token = AccessToken.create(new_access_token_value, self.access_token_expire_minutes)
        
        # Update token pair
        token_pair.access_token = new_access_token
        token_pair.updated_at = datetime.utcnow()
        
        return await self.token_repository.save(token_pair)
    
    async def logout(self, access_token: str) -> bool:
        """Logout user by revoking token."""
        token_pair = await self.token_repository.get_by_access_token(access_token)
        if not token_pair:
            return False
        
        # Revoke token
        token_pair.revoke()
        await self.token_repository.save(token_pair)
        
        # Deactivate session
        session = await self.session_repository.get_by_refresh_token(token_pair.refresh_token.value)
        if session:
            session.deactivate()
            await self.session_repository.save(session)
        
        # Publish logout event
        if self.event_handler:
            event = UserLoggedOut(
                aggregate_id=token_pair.user_id.value,
                user_id=token_pair.user_id.value,
                session_id=token_pair.id.value,
                timestamp=datetime.utcnow(),
            )
            await self.event_handler.handle(event)
        
        return True
    
    async def logout_all_sessions(self, user_id: str) -> bool:
        """Logout user from all sessions."""
        user = await self.user_repository.get_by_id(UserId(value=user_id))
        if not user:
            raise EntityNotFoundError(f"User with ID {user_id} not found")
        
        # Revoke all tokens
        await self.token_repository.revoke_all_user_tokens(user.id)
        
        # Deactivate all sessions
        await self.session_repository.deactivate_all_user_sessions(user.id)
        
        return True
    
    async def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Change user password."""
        user = await self.user_repository.get_by_id(UserId(value=user_id))
        if not user:
            raise EntityNotFoundError(f"User with ID {user_id} not found")
        
        # Verify old password
        if not self.verify_password(old_password, user.password_hash):
            raise BusinessRuleViolationError("Invalid old password")
        
        # Hash new password
        new_password_hash = self.get_password_hash(new_password)
        
        # Update user password
        user.password_hash = new_password_hash
        await self.user_repository.save(user)
        
        # Revoke all existing tokens
        await self.token_repository.revoke_all_user_tokens(user.id)
        await self.session_repository.deactivate_all_user_sessions(user.id)
        
        # Publish password changed event
        if self.event_handler:
            event = PasswordChanged(
                aggregate_id=user.id.value,
                user_id=user.id.value,
                timestamp=datetime.utcnow(),
            )
            await self.event_handler.handle(event)
        
        return True
    
    async def get_current_user(self, access_token: str) -> Optional[User]:
        """Get current user from access token."""
        payload = self.verify_token(access_token)
        if not payload or payload.get("type") != "access":
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        # Check if token is valid in repository
        token_pair = await self.token_repository.get_by_access_token(access_token)
        if not token_pair or not token_pair.is_valid:
            return None
        
        return await self.user_repository.get_by_id(UserId(value=user_id))
    
    async def cleanup_expired_tokens(self) -> int:
        """Clean up expired tokens and sessions."""
        expired_tokens = await self.token_repository.delete_expired_tokens()
        expired_sessions = await self.session_repository.delete_expired_sessions()
        return expired_tokens + expired_sessions 
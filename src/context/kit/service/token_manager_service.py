from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import timedelta
from typing import List, Optional, Any, Dict


@dataclass
class JwtPayload:
    iss: Optional[str] = None
    sub: Optional[str] = None
    aud: Optional[str] = None
    scp: List[str] = field(default_factory=list)
    custom_claims: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuthTokens:
    access_token: str
    refresh_token: str


class TokenManager(ABC):
    """
    TokenManager define el contrato para la gestión de tokens JWT (Access y Refresh).
    """

    @abstractmethod
    def sign(
        self,
        payload: JwtPayload,
        expires_in: timedelta,
        ctx: Optional[Any] = None,
    ) -> AuthTokens:
        pass

    def Sign(
        self,
        ctx: Optional[Any],
        payload: JwtPayload,
        expires_in: timedelta,
    ) -> AuthTokens:
        return self.sign(payload, expires_in, ctx)

    @abstractmethod
    def verify(self, token: str, ctx: Optional[Any] = None) -> JwtPayload:
        pass

    def Verify(self, ctx: Optional[Any], token: str) -> JwtPayload:
        return self.verify(token, ctx)

    @abstractmethod
    def verify_refresh_token(self, token: str, ctx: Optional[Any] = None) -> JwtPayload:
        pass

    def VerifyRefreshToken(self, ctx: Optional[Any], token: str) -> JwtPayload:
        return self.verify_refresh_token(token, ctx)


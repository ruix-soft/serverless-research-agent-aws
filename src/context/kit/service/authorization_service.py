from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Any
from context.kit.dtos.metadata import Metadata


@dataclass
class AuthorizationDecision:
    """
    AuthorizationDecision representa el resultado de una evaluación de permisos.
    """

    authorized: bool
    status: Optional[int] = None
    reason: Optional[str] = None


class AuthorizationService(ABC):
    """
    AuthorizationService define el contrato para verificar permisos.
    """

    @abstractmethod
    def authorize(
        self,
        payload: Any,
        action_type: str,
        metadata: Optional[Metadata] = None,
        ctx: Optional[Any] = None,
    ) -> AuthorizationDecision:
        """Determina si el payload tiene permiso para ejecutar la operación."""
        pass

    def Authorize(
        self,
        ctx: Optional[Any],
        payload: Any,
        action_type: str,
        metadata: Optional[Metadata] = None,
    ) -> AuthorizationDecision:
        """Alias para compatibilidad con Go (Authorize)."""
        return self.authorize(payload, action_type, metadata, ctx)


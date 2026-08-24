from abc import ABC, abstractmethod
from typing import Optional, Any


class SecretsService(ABC):
    """
    SecretsService define el contrato para acceder a secretos (AWS Secrets Manager, Vault, etc.).
    """

    @abstractmethod
    def get_secret_string(self, secret_id: str, ctx: Optional[Any] = None) -> str:
        pass

    def GetSecretString(self, ctx: Optional[Any], secret_id: str) -> str:
        return self.get_secret_string(secret_id, ctx)

    @abstractmethod
    def get_secret_binary(self, secret_id: str, ctx: Optional[Any] = None) -> bytes:
        pass

    def GetSecretBinary(self, ctx: Optional[Any], secret_id: str) -> bytes:
        return self.get_secret_binary(secret_id, ctx)


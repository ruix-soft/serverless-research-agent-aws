from abc import ABC, abstractmethod


class PasswordHasher(ABC):
    """
    PasswordHasher define el contrato para hashear y verificar contraseñas.
    """

    @abstractmethod
    def hash(self, plain_text: str) -> str:
        """Genera un hash seguro a partir de un texto plano."""
        pass

    def Hash(self, plain_text: str) -> str:
        """Alias para compatibilidad con Go (Hash)."""
        return self.hash(plain_text)

    @abstractmethod
    def compare(self, plain_text: str, hash_val: str) -> bool:
        """Verifica si una contraseña en texto plano coincide con el hash guardado."""
        pass

    def Compare(self, plain_text: str, hash_val: str) -> bool:
        """Alias para compatibilidad con Go (Compare)."""
        return self.compare(plain_text, hash_val)


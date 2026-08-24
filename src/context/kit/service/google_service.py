from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Any


@dataclass
class GoogleTokens:
    access_token: str
    refresh_token: str
    expires_in: int
    scope: str = ""
    token_type: str = "Bearer"


@dataclass
class GoogleUserInfo:
    email: str
    name: str


class GoogleOAuthService(ABC):
    """
    GoogleOAuthService abstrae el flujo de autorización OAuth 2.0 de Google.
    """

    @abstractmethod
    def auth_code_url(self, state: str) -> str:
        pass

    def AuthCodeURL(self, state: str) -> str:
        return self.auth_code_url(state)

    @abstractmethod
    def exchange(self, code: str, ctx: Optional[Any] = None) -> GoogleTokens:
        pass

    def Exchange(self, ctx: Optional[Any], code: str) -> GoogleTokens:
        return self.exchange(code, ctx)

    @abstractmethod
    def refresh(self, refresh_token: str, ctx: Optional[Any] = None) -> GoogleTokens:
        pass

    def Refresh(self, ctx: Optional[Any], refresh_token: str) -> GoogleTokens:
        return self.refresh(refresh_token, ctx)

    @abstractmethod
    def user_info(self, access_token: str, ctx: Optional[Any] = None) -> GoogleUserInfo:
        pass

    def UserInfo(self, ctx: Optional[Any], access_token: str) -> GoogleUserInfo:
        return self.user_info(access_token, ctx)


@dataclass
class CalendarEvent:
    summary: str
    description: str = ""
    location: str = ""
    start_rfc3339: str = ""
    end_rfc3339: str = ""
    time_zone: str = ""
    attendees: List[str] = field(default_factory=list)


class GoogleCalendarService(ABC):
    """
    GoogleCalendarService abstrae operaciones de eventos de calendario de Google.
    """

    @abstractmethod
    def create_event(
        self,
        access_token: str,
        calendar_id: str,
        event: CalendarEvent,
        ctx: Optional[Any] = None,
    ) -> str:
        pass

    def CreateEvent(
        self,
        ctx: Optional[Any],
        access_token: str,
        calendar_id: str,
        event: CalendarEvent,
    ) -> str:
        return self.create_event(access_token, calendar_id, event, ctx)

    @abstractmethod
    def update_event(
        self,
        access_token: str,
        calendar_id: str,
        event_id: str,
        event: CalendarEvent,
        ctx: Optional[Any] = None,
    ) -> None:
        pass

    def UpdateEvent(
        self,
        ctx: Optional[Any],
        access_token: str,
        calendar_id: str,
        event_id: str,
        event: CalendarEvent,
    ) -> None:
        self.update_event(access_token, calendar_id, event_id, event, ctx)

    @abstractmethod
    def delete_event(
        self,
        access_token: str,
        calendar_id: str,
        event_id: str,
        ctx: Optional[Any] = None,
    ) -> None:
        pass

    def DeleteEvent(
        self,
        ctx: Optional[Any],
        access_token: str,
        calendar_id: str,
        event_id: str,
    ) -> None:
        self.delete_event(access_token, calendar_id, event_id, ctx)


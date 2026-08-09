"""
HTTP client for the Smart Schedule API (agent talks to the API over HTTP
instead of importing the service/repository layer directly).
"""
import logging
from datetime import date, datetime, time
from typing import Optional

import httpx
from fastapi import HTTPException

from agent.config import (
    AGENT_API_BASE_URL,
    AGENT_API_USER,
    AGENT_API_PASSWORD,
    AGENT_COMPANY_NAME,
)

logger = logging.getLogger(__name__)


class ScheduleApiClient:
    """Client HTTP para a Smart Schedule API, com login/refresh automático de JWT."""

    def __init__(
        self,
        base_url: str = AGENT_API_BASE_URL,
        company_name: str = AGENT_COMPANY_NAME,
        user_name: str = AGENT_API_USER,
        password: str = AGENT_API_PASSWORD,
    ):
        self.company_name = company_name
        self.user_name = user_name
        self.password = password
        self.client = httpx.Client(timeout=30.0, base_url=base_url.rstrip("/"))
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None

    # ------------------------------------------------------------------
    # Autenticação
    # ------------------------------------------------------------------
    def _credentials_payload(self) -> dict:
        return {
            "company_name": self.company_name,
            "user_name": self.user_name,
            "password": self.password,
        }

    def _login(self) -> None:
        response = self.client.post("/auth/login", json=self._credentials_payload())
        if response.status_code == 401:
            # Primeira execução: usuário/empresa do agent ainda não existe.
            self._register()
            return
        response.raise_for_status()
        self._store_tokens(response.json())

    def _register(self) -> None:
        response = self.client.post("/auth/register", json=self._credentials_payload())
        response.raise_for_status()
        self._store_tokens(response.json())

    def _store_tokens(self, payload: dict) -> None:
        self._access_token = payload["access_token"]
        self._refresh_token = payload["refresh_token"]

    def _refresh(self) -> bool:
        if not self._refresh_token:
            return False
        response = self.client.post(
            "/auth/refresh", json={"refresh_token": self._refresh_token}
        )
        if response.status_code != 200:
            return False
        self._access_token = response.json()["access_token"]
        return True

    def _ensure_authenticated(self) -> None:
        if not self._access_token:
            self._login()

    # ------------------------------------------------------------------
    # Requisições autenticadas (com retry automático em caso de token expirado)
    # ------------------------------------------------------------------
    def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        self._ensure_authenticated()
        response = self.client.request(
            method, path, headers=self._auth_header(), **kwargs
        )

        if response.status_code == 401:
            if not self._refresh():
                self._login()
            response = self.client.request(
                method, path, headers=self._auth_header(), **kwargs
            )

        return response

    def _auth_header(self) -> dict:
        return {"Authorization": f"Bearer {self._access_token}"}

    @staticmethod
    def _raise_for_api_error(response: httpx.Response) -> None:
        if response.status_code >= 400:
            try:
                detail = response.json().get("detail", response.text)
            except ValueError:
                detail = response.text
            raise HTTPException(status_code=response.status_code, detail=detail)

    # ------------------------------------------------------------------
    # Endpoints de agendamento
    # ------------------------------------------------------------------
    def list_available_slots(
        self,
        start_date: Optional[str] = None,
        days_ahead: int = 7,
        limit: int = 8,
    ) -> list[dict]:
        params = {"days_ahead": days_ahead, "limit": limit}
        if start_date:
            params["start_date"] = start_date

        response = self._request("GET", "/schedule/available-slots", params=params)
        self._raise_for_api_error(response)

        return [
            {
                "date": datetime.strptime(item["date"], "%Y-%m-%d").date(),
                "time": time.fromisoformat(item["time"]),
            }
            for item in response.json()
        ]

    def create_schedule(self, customer_name: str, date_str: str, time_str: str) -> dict:
        response = self._request(
            "POST",
            "/schedule/",
            json={"customer_name": customer_name, "date": date_str, "time": time_str},
        )
        self._raise_for_api_error(response)

        payload = response.json()
        return {
            "customer_name": payload["customer"]["name"],
            "date": datetime.strptime(payload["date"], "%Y-%m-%d").date(),
            "time": time.fromisoformat(payload["time"]),
        }

    def close(self) -> None:
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

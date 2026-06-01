import json
import time
from typing import Any

from sqlalchemy.orm import Session

from backend.schema._input import ClientInput, ClientUpdateInput
from backend.services.sanaei import APIService
from backend.db import crud
from backend.utils.logger import logger


class AdminTaskService:
    def __init__(self, admin_username: str, db: Session):
        self.admin_username = admin_username
        self.db = db

        self.admin = crud.get_admin_by_username(
            db,
            username=admin_username
        )

        panel = crud.get_panel_by_name(
            db,
            name=self.admin.panel
        )

        self.api_service = APIService(
            url=panel.url,
            token=panel.token if panel.token else ""
        )

    async def get_all_users(self) -> Any:
        try:
            clients = await self.api_service.get_clients()

            online_clients = (
                await self.api_service.get_all_online_clients()
            )
            now = int(time.time() * 1000)

            result = []

            for client in clients:
                email = client.get("email")

                last_seen = online_clients.get(email, 0)

                client["isOnline"] = (
                last_seen > 0
                and now - last_seen < 120000
                )

                result.append(client)

            return result

        except Exception as e:
            logger.error(
                f"Error retrieving users for admin "
                f"{self.admin_username}: {str(e)}"
            )

            return []

    async def get_client_by_email(self, email: str):
        try:
            client = await self.api_service.get_client_by_email(email)
            return client

        except Exception as e:
            logger.error(
                f"Error retrieving client by email "
                f"{email}: {str(e)}"
            )
            return False

    async def add_client_to_panel(
        self,
        client: ClientInput
    ) -> bool:
        try:
            await self.api_service.add_client(
                list(map(int, self.admin.inbound_id.split(","))),
                self.admin.inbound_flow
                if self.admin.inbound_flow
                else None,
                client,
            )

            logger.info(
                f"Client {client.email} added "
                f"to panel by admin "
                f"{self.admin_username}"
            )

            return True

        except Exception as e:
            logger.error(
                f"Failed to add client "
                f"{client.email} by admin "
                f"{self.admin_username}: {str(e)}"
            )

            return False

    async def update_client_in_panel(
        self,
        uuid: str,
        client_data: ClientUpdateInput
    ) -> bool:
        try:
            await self.api_service.update_client(
                uuid,
                self.admin.inbound_flow
                if self.admin.inbound_flow
                else None,
                client_data
            )

            return True

        except Exception as e:
            logger.error(
                f"Failed to update client "
                f"{client_data.email} by admin "
                f"{self.admin_username}: {str(e)}"
            )

            return False

    async def reset_client_usage(
        self,
        email: str
    ) -> bool:
        try:
            await self.api_service.reset_client_usage(
                email
            )

            return True

        except Exception as e:
            logger.error(
                f"Failed to reset usage for client "
                f"{email} by admin "
                f"{self.admin_username}: {str(e)}"
            )

            return False

    async def delete_client_from_panel(
        self,
        uuid: str
    ) -> bool:
        try:
            email = await self.get_client_email_by_uuid(uuid)

            if not email:
                return False
            
            await self.api_service.delete_client(
                email
            )

            return True

        except Exception as e:
            logger.error(
                f"Failed to delete client "
                f"{uuid} by admin "
                f"{self.admin_username}: {str(e)}"
            )

            return False
    async def get_client_email_by_uuid(
        self,
        uuid: str
    ) -> str | None:
        try:
            clients = await self.get_all_users()

            for client in clients:
                if client.get("uuid") == uuid:
                    return client.get("email")

            return None

        except Exception as e:
            logger.error(
                f"Failed to get client email by uuid "
                f"{uuid}: {str(e)}"
            )

            return None
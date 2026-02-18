# built-in dependencies
from typing import Optional, Dict, Any, Tuple

# project dependencies
from deepface.commons.logger import Logger

from deepface.api.src.modules.auth.token_store import TokenStore

logger = Logger()


class AuthService:
    def __init__(self, token_store: TokenStore) -> None:
        self.token_store = token_store

    def extract_token(self, auth_header: Optional[str]) -> Optional[str]:
        if not auth_header:
            return None
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            return parts[1]
        return None

    def validate_and_get_name(self, headers: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        token = self.extract_token(headers.get("Authorization"))
        if not token:
            logger.debug("Invalid token")
            return False, None

        record = self.token_store.lookup(token)
        if not record:
            logger.debug("Invalid token")
            return False, None

        logger.debug(f"Authorized token for {record.name}")
        return True, record.name

    def validate(self, headers: Dict[str, Any]) -> bool:
        ok, _ = self.validate_and_get_name(headers)
        return ok

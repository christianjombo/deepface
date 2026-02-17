from typing import Optional, Dict, Any
import json
from deepface.commons.logger import Logger

logger = Logger()

class AuthService:
    def __init__(
        self,
        auth_token: Optional[str] = None,          # legacy: DEEPFACE_AUTH_TOKEN
        auth_tokens: Optional[str] = None,         # legacy: DEEPFACE_AUTH_TOKENS (csv)
        auth_tokens_json: Optional[str] = None     # NEW: DEEPFACE_AUTH_TOKENS_JSON (json map)
    ) -> None:
        """
        DEEPFACE_AUTH_TOKENS_JSON example:
          {"treasury-team":"tok1","support-team":"tok2"}

        Stored internally as token -> name for quick lookup.
        """
        self.token_to_name: Dict[str, str] = {}

        # 1) Preferred: JSON map name -> token
        if auth_tokens_json:
            try:
                obj = json.loads(auth_tokens_json)
                if not isinstance(obj, dict):
                    raise ValueError("DEEPFACE_AUTH_TOKENS_JSON must be a JSON object")
                for name, tok in obj.items():
                    if isinstance(name, str) and isinstance(tok, str) and tok.strip():
                        self.token_to_name[tok.strip()] = name.strip() or "unnamed"
            except Exception as e:
                logger.error(f"Invalid DEEPFACE_AUTH_TOKENS_JSON: {e}")

        # 2) CSV list => unnamed
        if auth_tokens:
            for t in auth_tokens.split(","):
                t = t.strip()
                if t:
                    self.token_to_name.setdefault(t, "unnamed")

        # 3) Single token => unnamed
        if auth_token and auth_token.strip():
            self.token_to_name.setdefault(auth_token.strip(), "unnamed")

        self.is_auth_enabled = len(self.token_to_name) > 0

    def extract_token(self, auth_header: Optional[str]) -> Optional[str]:
        if not auth_header:
            return None
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            return parts[1]
        return None

    def validate(self, headers: Dict[str, Any]) -> bool:
        ok, _ = self.validate_and_get_name(headers)
        return ok

    def validate_and_get_name(self, headers: Dict[str, Any]):
        if not self.is_auth_enabled:
            logger.debug("Authentication is disabled. Skipping token validation.")
            return True, None

        token = self.extract_token(headers.get("Authorization"))
        if not token:
            logger.debug("No authentication token provided. Validation failed.")
            return False, None

        name = self.token_to_name.get(token)
        if not name:
            logger.debug("Invalid authentication token provided. Validation failed.")
            return False, None

        return True, name

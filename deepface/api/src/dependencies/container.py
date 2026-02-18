# project dependencies
from deepface.api.src.modules.auth.service import AuthService
from deepface.api.src.modules.auth.token_store import TokenStore
from deepface.api.src.dependencies.variables import Variables


# pylint: disable=too-few-public-methods
class Container:
    def __init__(self, variables: Variables) -> None:
        self.variables = variables
        token_store = TokenStore(
            db_path=variables.token_db_path,
            ttl_seconds=1800,
        )
        self.auth_service = AuthService(token_store=token_store)
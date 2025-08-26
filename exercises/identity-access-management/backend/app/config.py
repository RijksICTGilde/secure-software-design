import secrets

from jose.constants import ALGORITHMS
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)

    DEBUG: bool = True

    OIDC_CLIENT_ID: str = "secret-backend"
    OIDC_CLIENT_SECRET: str = "fq77F06MOe8Gj0byhmGOc6svna5Juszy"
    OIDC_AUTHORIZATION_ENDPOINT: str = (
        "http://keycloak:8080/realms/master/protocol/openid-connect/auth"
    )
    OIDC_TOKEN_ENDPOINT: str = "http://keycloak:8080/realms/master/protocol/openid-connect/token"
    OIDC_JWKS_ENDPOINT: str = "http://keycloak:8080/realms/master/protocol/openid-connect/certs"
    OIDC_SCOPES: dict[str, str] = {"openid": "", "profile": "", "email": "", "organization": ""}
    OIDC_AUDIENCE: str = "account"
    OIDC_ISSUER: str = "http://localhost:8080/realms/master"
    OIDC_SIGNATURE_ALGORITM: str | list[str] = [ALGORITHMS.RS256, ALGORITHMS.HS256]

    CORS_ALLOW_ORIGINS: str | list[str] = "*"
    CORS_ALLOW_CREDENTIALS: bool = False
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]


settings = Settings()  # type: ignore[reportCallIssue]

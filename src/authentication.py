import aiohttp
from starlette.authentication import (
    AuthCredentials, AuthenticationBackend, AuthenticationError, SimpleUser
)


class UserAuth(SimpleUser):
    def __init__(self, **kwargs) -> None:
        self.__dict__.update(kwargs)


class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(self, conn):
        if "Authorization" not in conn.headers:
            url = conn.url.path
            if url.split("/")[-1] in ("docs", "openapi.json"):
                return
            raise AuthenticationError("No token received")
        auth = conn.headers["Authorization"]
        try:
            scheme, token = auth.split()
            if scheme.lower() != 'bearer':
                return
        except ValueError:
            return

        async with aiohttp.ClientSession() as session:
            async with session.post('http://localhost:7000/auth/userbytoken',
                                    json={"access": token}) as resp:
                if resp.status == 200:
                    user_data = await resp.json()
                else:
                    raise AuthenticationError("Invalid token")
        user = UserAuth(**user_data)
        return AuthCredentials(["authenticated"]), user

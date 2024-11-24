from decouple import config

from ai_dev3.infrastructure.DbApiService import DbApiService

from .types import User, UsersConnection


class UsersDb:
    def __init__(self):
        self.db = DbApiService(api_url=f"{config('CENTRALA_URL')}/apidb")

    async def get_all_users(self) -> list[User]:
        records = await self.db.query("select * from users")
        return [User(id=record["id"], name=record["username"]) for record in records]

    async def get_all_connections(self) -> list[UsersConnection]:
        records = await self.db.query("select * from connections")
        return [UsersConnection(user1_id=record["user1_id"], user2_id=record["user2_id"]) for record in records]

from pydantic import BaseModel


class User(BaseModel):
    id: str
    name: str


class UsersConnection(BaseModel):
    user1_id: str
    user2_id: str

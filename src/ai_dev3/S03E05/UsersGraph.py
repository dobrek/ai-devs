from neo4j import AsyncGraphDatabase, AsyncManagedTransaction, AsyncResult
from termcolor import colored

from .types import User, UsersConnection


class UsersGraphs:
    def __init__(self, uri: str, username: str, password: str) -> None:
        self.driver = AsyncGraphDatabase.driver(uri, auth=(username, password))

    async def init_with_data(self, users: list[User], connections: list[UsersConnection]):
        await self._veryfy_connection()
        async with self.driver.session() as session:
            await session.execute_write(self._clear_all)
            await session.execute_write(self._create_users, users)
            await session.execute_write(self._make_connections, connections)

    async def _veryfy_connection(self):
        await self.driver.verify_connectivity()

    async def _clear_all(self, tx: AsyncManagedTransaction):
        result = await tx.run("MATCH (u:User) DETACH DELETE u")
        summary = await result.consume()
        print(colored(f"Deleted nodes: {summary.counters.nodes_deleted}", "yellow"))
        print(colored(f"Deleted relationships: {summary.counters.relationships_deleted}", "yellow"))

    async def _create_users(self, tx: AsyncManagedTransaction, users: list[User]):
        result = await tx.run(
            """
            UNWIND $users AS user
            MERGE (u:User {id: user.id})
            SET u += user
            """,
            users=[user.model_dump() for user in users],
        )
        summary = await result.consume()
        print(colored(f"Users created: {summary.counters.nodes_created}", "cyan"))

    async def _make_connections(self, tx: AsyncManagedTransaction, connections: list[UsersConnection]):
        result = await tx.run(
            """
                UNWIND $connections AS connection
                MATCH (u_a:User {id: connection.a_id})
                MATCH (u_b:User {id: connection.b_id})
                MERGE (u_a)-[:KNOWS]->(u_b)
                """,
            connections=[{"a_id": connection.user1_id, "b_id": connection.user2_id} for connection in connections],
        )
        summary = await result.consume()
        print(colored(f"Relationships created: {summary.counters.relationships_created}", "cyan"))

    async def find_shortest_path(self, name_a, name_b) -> list[User] | None:
        query = """
            MATCH p = shortestPath((u_a:User {name: $name_a})-[:KNOWS*1..7]-(u_b:User {name: $name_b}))
            RETURN [n IN nodes(p) | {id: n.id, name: n.name}] AS path
            """
        record = await self.driver.execute_query(
            query, name_a=name_a, name_b=name_b, result_transformer_=AsyncResult.single
        )
        if record.get("path"):
            return [User(id=user["id"], name=user["name"]) for user in record["path"]]
        else:
            return None

    async def close(self):
        await self.driver.close()

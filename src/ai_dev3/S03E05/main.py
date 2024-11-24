import asyncio

from decouple import config
from termcolor import colored

from ai_dev3.utils.api_client import send_answer

from .UsersDb import UsersDb
from .UsersGraph import UsersGraphs


async def task():
    users_db = UsersDb()
    users_graph = UsersGraphs(uri=config("NEO4J_URI"), username=config("NEO4J_USER"), password=config("NEO4J_PASSWORD"))
    try:
        users = await users_db.get_all_users()
        connections = await users_db.get_all_connections()

        await users_graph.veryfy_connection()
        await users_graph.clear_all()
        await users_graph.populate(users, connections)
        path = await users_graph.find_shortest_path("Rafał", "Barbara")

        if path is None:
            print(colored("No path found", "red"))
        else:
            print("Path found", colored(path, "green"))
            send_answer(task="connections", answer=",".join([user.name for user in path]))

    except Exception as error:
        print(colored(error, "red"))
    finally:
        await users_graph.close()


def main():
    asyncio.run(task())


if __name__ == "__main__":
    main()

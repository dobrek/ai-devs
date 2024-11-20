import asyncio

from decouple import config
from openai import AsyncOpenAI
from qdrant_client import AsyncQdrantClient
from termcolor import colored

from ai_dev3.utils.api_client import send_answer
from ai_dev3.utils.open_ai import embeddings_function

from .load_reports import load_reports
from .VectorsService import VectorsService

task_name = "wektory"
zip_url = f"{config('CENTRALA_URL')}/dane/pliki_z_fabryki.zip"
zip_file_password = config("ZIP_FILE_PASSWORD")
collection_name = "SO3E02_wektory"


async def task():
    do_embeddings = embeddings_function(AsyncOpenAI(api_key=config("OPENAI_API_KEY")))
    vectors_service = VectorsService(AsyncQdrantClient(":memory:"), collection_name, do_embeddings)

    reports = await load_reports(zip_url, zip_file_password)
    await vectors_service.init_collection()
    await vectors_service.upsert_reports(reports)

    query = "W raporcie, z którego dnia znajduje się wzmianka o kradzieży prototypu broni?"
    results = await vectors_service.search_reports(query)

    first_report = results[0]
    print("Result", colored(first_report, "green"))
    send_answer(task=task_name, answer=first_report.date.isoformat())


def main():
    asyncio.run(task())


if __name__ == "__main__":
    main()

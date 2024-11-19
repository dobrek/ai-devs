import asyncio

from decouple import config
from termcolor import colored

from ai_dev3.utils.api_client import send_answer
from ai_dev3.utils.langfuse import init_langfuse

from .data import load_data
from .keywords import index_file

task_name = "dokumenty"
zip_url = f"{config('CENTRALA_URL')}/dane/pliki_z_fabryki.zip"


async def task():
    init_langfuse()
    data = await load_data(zip_url)
    reports = data.reports
    enhanced_reports = await asyncio.gather(*[index_file(report) for report in reports])
    [print(colored(report, "green")) for report in enhanced_reports]
    answer = {report.name: ",".join(report.keywords) for report in enhanced_reports}
    send_answer(answer, task_name)


def main():
    asyncio.run(task())


if __name__ == "__main__":
    main()

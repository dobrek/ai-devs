import asyncio
from collections.abc import Awaitable, Callable

from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.models import PointStruct
from termcolor import colored

from .types import ReportFile


class ReportFileWithEmbedding(ReportFile):
    embedding: list[float]


EmbeddingsFunction = Callable[[str], Awaitable[list[float]]]


class VectorsService:
    def __init__(self, client: AsyncQdrantClient, collection_name: str, do_embeddings: EmbeddingsFunction) -> None:
        self.client = client
        self.collection_name = collection_name
        self.do_embeddings = do_embeddings

    async def init_collection(self) -> None:
        if not await self.client.collection_exists(self.collection_name):
            print("Creating collection", colored(self.collection_name, "blue"))
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=3072, distance=Distance.COSINE),
            )

    async def _report_with_embedding(self, report: ReportFile) -> ReportFileWithEmbedding:
        embedding = await self.do_embeddings(report.text)
        return ReportFileWithEmbedding(**report.model_dump(), embedding=embedding)

    async def upsert_reports(self, reports: list[ReportFile]) -> None:
        print("Upserting reports")
        embedded_reports = await asyncio.gather(*[self._report_with_embedding(report) for report in reports])
        points = [
            PointStruct(id=str(report.id), vector=report.embedding, payload=report.model_dump(exclude=["embedding"]))
            for report in embedded_reports
        ]
        await self.client.upsert(collection_name=self.collection_name, points=points)

    async def search_reports(self, query: str, limit: int = 1) -> list[ReportFile]:
        query_vector = await self.do_embeddings(query)
        results = await self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
        )
        return [ReportFile(**result.payload) for result in results]

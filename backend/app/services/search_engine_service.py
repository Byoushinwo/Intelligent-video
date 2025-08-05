from elasticsearch import AsyncElasticsearch, BadRequestError
from elasticsearch.helpers import async_bulk
from app.core.config import settings

class SearchEngineService:
    def __init__(self):
        self.client = AsyncElasticsearch(
            hosts=settings.ELASTICSEARCH_HOSTS,
            request_timeout=30,
            max_retries=5,
            retry_on_timeout=True
        )
        self.index_name = "subtitles"
        self.index_mapping = {
            "properties": {
                "id": {"type": "integer"},
                "video_id": {"type": "integer"},
                "start_time": {"type": "float"},
                "text": {"type": "text", "analyzer": "standard"}
            }
        }

    # ---  绕过有问题的 exists() 检查
    async def create_index_if_not_exists(self):
        """
        直接尝试创建索引，如果已存在则捕获并忽略异常。
        这避免了调用有兼容性问题的 .indices.exists() 方法。
        """
        try:
            await self.client.indices.create(
                index=self.index_name,
                mappings=self.index_mapping
            )
            print(f"Created Elasticsearch index: '{self.index_name}' with mapping.")
        except BadRequestError as e:
            # 捕获因索引已存在而导致的 BadRequestError (code 400)
            if e.meta.status == 400 and e.body.get("error", {}).get("type") == "resource_already_exists_exception":
                # 这是预期的“错误”，说明索引已存在，我们什么都不用做
                print(f"Index '{self.index_name}' already exists.")
                pass
            else:
                # 如果是其他类型的 BadRequestError，则重新抛出异常
                print(f"An unexpected BadRequestError occurred: {e}")
                raise e
        except Exception as e:
            print(f"An unexpected error occurred during index creation: {e}")
            raise e

    # --- 使用 async_bulk 的正确 index_subtitles 方法 ---
    async def index_subtitles(self, subtitles: list[dict]):
        if not subtitles:
            return
        def generate_actions():
            for sub in subtitles:
                yield {
                    "_op_type": "index",
                    "_index": self.index_name,
                    "_id": sub["id"],
                    "_source": sub
                }
        try:
            success, failed = await async_bulk(self.client, generate_actions())
            print(f"Successfully indexed {success} subtitles. Failed items: {len(failed)}")
        except Exception as e:
            print(f"An error occurred during bulk indexing: {e}")

    async def search_subtitles_by_text(self, query_text: str, size: int = 10) -> list:
        response = await self.client.search(
            index=self.index_name,
            size=size,
            query={"match": {"text": {"query": query_text, "operator": "and"}}}
        )
        return [hit["_source"] for hit in response["hits"]["hits"]]

search_engine_service = SearchEngineService()
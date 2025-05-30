import time
import asyncio
from typing import List, Dict, Optional
from openai import OpenAI

class VectorStoreManager:
    def __init__(self, client: OpenAI):
        self.client = client

    def create_vector_store(self, name: str, file_ids: Optional[List[str]] = None) -> str:
        """Create a new vector store with optional initial files."""
        vector_store = self.client.vector_stores.create(
            name=name,
            file_ids=file_ids or []
        )
        return vector_store.id

    def add_files_to_store(self, vector_store_id: str, file_ids: List[str]) -> None:
        """Add multiple files to an existing vector store."""
        for file_id in file_ids:
            self.client.vector_stores.files.create(
                vector_store_id=vector_store_id,
                file_id=file_id
            )

    def wait_for_completion(self, vector_store_id: str, timeout: int = 300) -> bool:
        """Poll until all files are processed or timeout occurs."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            files = self.client.vector_stores.files.list(vector_store_id=vector_store_id)
            statuses = [file.status for file in files.data]
            if all(status == "completed" for status in statuses):
                return True
            elif any(status == "failed" for status in statuses):
                raise RuntimeError("File processing failed")
            elif any(status == "cancelled" for status in statuses):
                raise RuntimeError("File processing cancelled")
            # If any file is still in progress, wait and poll again
            time.sleep(5)
        raise TimeoutError("File processing timeout exceeded")

    async def wait_for_completion_async(self, vector_store_id: str, timeout: int = 300) -> bool:
        """Async version: poll until all files are processed or timeout occurs."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            files = self.client.vector_stores.files.list(vector_store_id=vector_store_id)
            statuses = [file.status for file in files.data]
            if all(status == "completed" for status in statuses):
                return True
            elif any(status == "failed" for status in statuses):
                raise RuntimeError("File processing failed")
            elif any(status == "cancelled" for status in statuses):
                raise RuntimeError("File processing cancelled")
            await asyncio.sleep(5)
        raise TimeoutError("File processing timeout exceeded")

    def cleanup_vector_store(self, vector_store_id: str) -> None:
        """Delete a vector store and all associated files."""
        self.client.vector_stores.delete(vector_store_id=vector_store_id)

"""
Search interface module for querying the vector store.
"""
from typing import List, Any, Dict, Optional
from vector_store import VectorStore
from openai import OpenAI

class SearchInterface:
    """Interface for searching files using vector embeddings."""
    def __init__(self, vector_store: VectorStore, client: OpenAI):
        self.vector_store = vector_store
        self.client = client

    def search(self, query: str, top_k: int = 5) -> List[Any]:
        """Search for files relevant to the query."""
        # Placeholder: convert query to embedding, then search
        # In production, use OpenAI or other embedding API
        query_embedding = self._embed_query(query)
        return self.vector_store.search(query_embedding, top_k=top_k)

    def semantic_search(self, vector_store_id: str, query: str, 
                       max_results: int = 10, filters: Optional[Dict] = None) -> Dict:
        """Perform direct semantic search against vector store"""
        search_params = {
            "vector_store_id": vector_store_id,
            "query": query,
            "max_num_results": max_results
        }
        if filters:
            search_params["attribute_filter"] = filters
        return self.client.vector_stores.search(**search_params)

    def assisted_search(self, vector_store_ids: List[str], query: str, 
                       model: str = "gpt-4o-mini") -> Dict:
        """Perform AI-assisted search with automatic response generation"""
        response = self.client.responses.create(
            model=model,
            input=query,
            tools=[{
                "type": "file_search",
                "vector_store_ids": vector_store_ids
            }],
            include=["file_search_call.results"]
        )
        return response

    def synthesize_response(self, search_results: Dict, original_query: str, 
                          model: str = "gpt-4o-mini") -> str:
        """Generate custom response from search results"""
        formatted_sources = self._format_search_results(search_results)
        completion = self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "developer",
                    "content": "Generate a comprehensive answer based on provided sources."
                },
                {
                    "role": "user", 
                    "content": f"Sources: {formatted_sources}\n\nQuery: {original_query}"
                }
            ]
        )
        return completion.choices[0].message.content

    def _format_search_results(self, search_results: Dict) -> str:
        """Format search results for prompt injection."""
        # This is a placeholder for formatting logic
        # In production, format citations and content as needed
        return str(search_results)

    def _embed_query(self, query: str) -> list:
        """Convert query string to embedding (stub)."""
        # Replace with actual embedding logic
        return []

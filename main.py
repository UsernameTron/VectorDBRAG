"""
Main entry point for the file search and retrieval system.
"""
from config import Config
from file_manager import FileUploader
from vector_store import VectorStore
from search_interface import SearchInterface
from openai import OpenAI


def main():
    try:
        Config.validate()
        Config.configure_logging()
        client = OpenAI(api_key=Config.OPENAI_API_KEY)
        uploader = FileUploader(client)
        vector_store = VectorStore(Config.EMBEDDING_MODEL)
        searcher = SearchInterface(vector_store, client)
        # Example usage (stub):
        # file_id = uploader.upload_file("example.pdf")
        # results = searcher.search("example query")
        print(f"System initialized in {Config.ENV} mode. Ready for file upload and search.")
    except Exception as e:
        import traceback
        print(f"Initialization failed: {e}\n{traceback.format_exc()}")

if __name__ == "__main__":
    main()

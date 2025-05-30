import os
import time
import pytest
from search_system import SearchSystem
from config import Config

@pytest.fixture(scope="module")
def config():
    # Create a test configuration
    config = Config("development")
    return config

@pytest.fixture(scope="module")
def search_system(config):
    return SearchSystem(config)

def test_end_to_end_workflow(search_system, tmp_path):
    # Create a small test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("Integration test content.")
    # Upload and create knowledge base
    kb_id = search_system.create_knowledge_base(
        name="integration-test-kb",
        file_paths=[str(test_file)],
        metadata={"test": True}
    )
    assert kb_id
    # Query the knowledge base (semantic)
    semantic_result = search_system.query_knowledge_base(kb_id, "test content", search_type="semantic")
    assert isinstance(semantic_result, dict)
    # Query the knowledge base (assisted)
    assisted_result = search_system.query_knowledge_base(kb_id, "test content", search_type="assisted")
    assert isinstance(assisted_result, dict)
    # Cleanup: Optionally delete the vector store (if supported by your API wrapper)
    # search_system.vector_store_manager.cleanup_vector_store(kb_id)
    # Add a short sleep to avoid API rate limits in rapid CI
    time.sleep(2)

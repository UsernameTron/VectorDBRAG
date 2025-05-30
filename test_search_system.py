import pytest
from unittest.mock import Mock, patch
from search_system import SearchSystem, FileProcessingError, VectorStoreError, SearchError

class TestSearchSystem:
    @pytest.fixture
    def mock_client(self):
        return Mock()

    @pytest.fixture
    def search_system(self, mock_client):
        with patch('search_system.OpenAI', return_value=mock_client):
            return SearchSystem("test_api_key")

    def test_file_upload_success(self, search_system, mock_client):
        mock_client.files.create.return_value.id = "file_123"
        with patch('os.path.exists', return_value=True), \
             patch('os.path.getsize', return_value=1024), \
             patch('builtins.open', mock_open(read_data=b'data')):
            file_id = search_system.file_uploader.upload_file("test.pdf")
            assert file_id == "file_123"
            mock_client.files.create.assert_called_once()

    def test_file_upload_failure(self, search_system, mock_client):
        mock_client.files.create.side_effect = Exception("Upload failed")
        with patch('os.path.exists', return_value=True), \
             patch('os.path.getsize', return_value=1024), \
             patch('builtins.open', mock_open(read_data=b'data')):
            with pytest.raises(FileProcessingError):
                search_system.file_uploader.upload_file("test.pdf")

    def test_create_knowledge_base_success(self, search_system, mock_client):
        mock_client.files.create.return_value.id = "file_123"
        mock_client.vector_stores.create.return_value.id = "vs_456"
        mock_client.vector_stores.files.list.return_value.data = [Mock(status="completed")]
        with patch('os.path.exists', return_value=True), \
             patch('os.path.getsize', return_value=1024), \
             patch('builtins.open', mock_open(read_data=b'data')):
            vs_id = search_system.create_knowledge_base("kb", ["test.pdf"])
            assert vs_id == "vs_456"

    def test_create_knowledge_base_file_upload_error(self, search_system, mock_client):
        mock_client.files.create.side_effect = Exception("Upload failed")
        with patch('os.path.exists', return_value=True), \
             patch('os.path.getsize', return_value=1024), \
             patch('builtins.open', mock_open(read_data=b'data')):
            with pytest.raises(FileProcessingError):
                search_system.create_knowledge_base("kb", ["test.pdf"])

    def test_query_knowledge_base_semantic(self, search_system, mock_client):
        mock_client.vector_stores.search.return_value = {"results": [1,2,3]}
        result = search_system.query_knowledge_base("vs_456", "query", search_type="semantic")
        assert result == {"results": [1,2,3]}

    def test_query_knowledge_base_assisted(self, search_system, mock_client):
        mock_client.responses.create.return_value = {"choices": ["result"]}
        result = search_system.query_knowledge_base("vs_456", "query", search_type="assisted")
        assert result == {"choices": ["result"]}

    def test_query_knowledge_base_invalid_type(self, search_system):
        with pytest.raises(ValueError):
            search_system.query_knowledge_base("vs_456", "query", search_type="invalid")

from unittest.mock import mock_open

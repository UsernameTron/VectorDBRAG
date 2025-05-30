"""
File management module for uploading and validating files.
Supports local and URL-based uploads with error handling and logging.
"""
import os
import logging
import requests
from typing import Optional, Dict
from openai import OpenAI
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import traceback

class FileUploader:
    def __init__(self, client: OpenAI):
        self.client = client
        self.supported_extensions = {'.pdf', '.docx', '.txt', '.md', '.html', '.json'}
        self.max_file_size_mb = 20
        self.logger = logging.getLogger("file_manager")
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler.setFormatter(formatter)
        if not self.logger.hasHandlers():
            self.logger.addHandler(handler)
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def upload_file(self, file_path: str, attributes: Optional[Dict] = None) -> str:
        """Upload a file from local path or URL and return file ID"""
        try:
            if self._is_url(file_path):
                return self._upload_from_url(file_path, attributes or {})
            else:
                return self._upload_from_local(file_path, attributes or {})
        except Exception as e:
            self.logger.error(f"Failed to upload file: {e}\n{traceback.format_exc()}")
            raise

    def _upload_from_local(self, file_path: str, attributes: Dict) -> str:
        """Handle local file upload with validation"""
        if not os.path.exists(file_path):
            self.logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in self.supported_extensions:
            self.logger.error(f"Unsupported file type: {file_ext}")
            raise ValueError(f"Unsupported file type: {file_ext}")
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if size_mb > self.max_file_size_mb:
            self.logger.error(f"File size {size_mb:.2f}MB exceeds limit of {self.max_file_size_mb}MB")
            raise ValueError(f"File size {size_mb:.2f}MB exceeds limit of {self.max_file_size_mb}MB")
        try:
            with open(file_path, "rb") as file_content:
                result = self.client.files.create(
                    file=file_content,
                    purpose="assistants"
                )
            self.logger.info(f"File uploaded successfully: {file_path} (ID: {result.id})")
            return result.id
        except Exception as e:
            self.logger.error(f"OpenAI upload failed: {e}\n{traceback.format_exc()}")
            raise

    def _upload_from_url(self, url: str, attributes: Dict) -> str:
        """Download and upload file from remote URL with validation and retry"""
        try:
            local_filename = url.split("/")[-1]
            file_ext = os.path.splitext(local_filename)[1].lower()
            if file_ext not in self.supported_extensions:
                self.logger.error(f"Unsupported file type: {file_ext}")
                raise ValueError(f"Unsupported file type: {file_ext}")
            resp = self.session.get(url, timeout=30)
            resp.raise_for_status()
            size_mb = len(resp.content) / (1024 * 1024)
            if size_mb > self.max_file_size_mb:
                self.logger.error(f"Downloaded file size {size_mb:.2f}MB exceeds limit of {self.max_file_size_mb}MB")
                raise ValueError(f"Downloaded file size {size_mb:.2f}MB exceeds limit of {self.max_file_size_mb}MB")
            with open(local_filename, "wb") as f:
                f.write(resp.content)
            file_id = self._upload_from_local(local_filename, attributes)
            os.remove(local_filename)
            return file_id
        except requests.RequestException as e:
            self.logger.error(f"Network error during file download: {e}\n{traceback.format_exc()}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to upload file from URL: {e}\n{traceback.format_exc()}")
            raise

    def _is_url(self, path: str) -> bool:
        return path.startswith("http://") or path.startswith("https://")

from abc import ABC, abstractmethod
from typing import BinaryIO, Optional

class StorageService(ABC):
    @abstractmethod
    async def upload_file(self, file: BinaryIO, file_name: str, folder: Optional[str] = None) -> str:
        """Uploads a file and returns the storage URL."""
        pass

    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """Deletes a file from storage."""
        pass

    @abstractmethod
    async def get_public_url(self, file_path: str) -> str:
        """Generates a public URL for a file."""
        pass

    @abstractmethod
    async def file_exists(self, file_path: str) -> bool:
        """Checks if a file exists in storage."""
        pass

# In base.py, define an abstract adapter class with the same methods for all sources, such as fetch(), parse(), and normalize().

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseAdapter(ABC):
    @abstractmethod
    def extract_data(self) -> list[Any]:
        """Fetch raw data from the source."""
        pass

    @abstractmethod
    def transform_data(self, raw_data: List[Any]) -> List[Dict[str, Any]]:
        """Standardize the raw data into a dictionary."""
        pass

    @abstractmethod
    def load_data(self, transformed_data: List[Dict[str, Any]]) -> None:
        """Sink the data."""
        pass

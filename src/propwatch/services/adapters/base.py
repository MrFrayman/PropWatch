# In base.py, define an abstract adapter class with the same methods for all sources, such as fetch(), parse(), and normalize().

from abc import ABC, abstractmethod

class BaseAdapter(ABC):
    @abstractmethod
    def fetch(self):
        """Fetch raw data from the source."""
        pass

    @abstractmethod
    def parse(self, raw_data):
        """Parse the raw data into a structured format."""
        pass

    @abstractmethod
    def normalize(self, parsed_data):
        """Normalize the parsed data into a consistent format for the app."""
        pass
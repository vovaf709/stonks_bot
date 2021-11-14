from abc import ABC, abstractmethod
from typing import Dict


class ExternalApi(ABC):
    @abstractmethod
    def process_response(self, data: Dict):
        pass

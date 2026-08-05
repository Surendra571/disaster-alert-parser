from abc import ABC, abstractmethod
from typing import List
from src.models import NormalizedAlert
from src.utils.lookups import ReferenceLookups

class BaseParser(ABC):
    def __init__(self, lookups: ReferenceLookups):
        self.lookups = lookups

    @abstractmethod
    def parse(self, raw_content: str) -> List[NormalizedAlert]:
        pass
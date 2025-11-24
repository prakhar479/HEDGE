from abc import ABC, abstractmethod
from typing import List

class Mutator(ABC):
    @abstractmethod
    def mutate(self, code_str: str) -> List[str]:
        """
        Generates a list of mutated code strings from the input code.
        """
        pass

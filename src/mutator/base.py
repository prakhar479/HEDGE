from abc import ABC, abstractmethod
from typing import List, Tuple

class Mutator(ABC):
    @abstractmethod
    def mutate(self, code_str: str) -> List[Tuple[str, str]]:
        """
        Generates a list of (mutated_code, mutation_strategy_name) tuples.
        """
        pass

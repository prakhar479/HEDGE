from abc import ABC, abstractmethod
from typing import List, Tuple

# Forward declaration to avoid circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.core.ir_manager import CodeIR

class Mutator(ABC):
    @abstractmethod
    def mutate(self, code_ir: 'CodeIR') -> List[Tuple['CodeIR', str]]:
        """
        Generates a list of (mutated_code_ir, mutation_strategy_name) tuples.
        """
        pass

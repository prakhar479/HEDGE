# HEDGE Mutators

Mutators are the core transformation engines in HEDGE. They accept a `Module` (IR root) and return a list of potentially optimized variants.

## 1. Structural Mutators (`src/application/mutators/structural.py`)

These mutators operate directly on the IR tree. They are fast, deterministic, and focus on syntactic-level transformations that don't change the algorithm but might improve local performance or readability.

### Strategies
-   **Reorder Statements**: Identifies independent adjacent statements and swaps them.
    -   *Logic*: Safe if neither statement uses variables defined by the other (checked via `MutationContext` dependency analysis).
-   **Swap Operands**: Swaps operands for commutative binary operations (e.g., `a + b` → `b + a`).
    -   *Logic*: Applied to `+`, `*`, `==`, `!=`, `and`, `or`.
-   **Augmented Assignment**: Converts `x = x + y` to `x += y`.
    -   *Logic*: Checks binary operations where the target appears in the expression.
-   **Range Optimization**: conversion of `range(0, n)` to `range(n)`.

### Context Awareness
If enabled (default), `StructuralMutator` builds a lightweight symbol table and dependency graph (`MutationContext`) to ensure transformations like statement reordering do not violate data dependencies.

## 2. Semantic Mutators (`src/application/mutators/semantic.py`)

These mutators leverage Large Language Models (LLMs) to perform high-level refactoring and algorithmic changes.

### Workflow
1.  **Code Generation**: Convert current IR to Python source code.
2.  **Prompting**: Send code to LLM with specific optimization instructions.
3.  **Parsing**: Parse the LLM response back into HEDGE IR.
4.  **Self-Repair**: If parsing fails (syntax error), the system feeds the error back to the LLM to request a fix (up to 3 retries).

### Strategies
-   **Idiomatic Refactoring**: Rewrites code to use Pythonic patterns (list comprehensions, generators).
-   **Library Optimization**: Replaces manual loops/logic with standard library functions (`itertools`, `collections`).
-   **Algorithmic Optimization**: Attempts to improve Big-O complexity (e.g., O(n²) → O(n)).

## 3. Advanced Mutators (`src/application/mutators/advanced.py`)

Compiler-style optimizations implemented on the IR.

### Strategies
-   **Constant Folding**: Evaluates constant expressions at compile-time (e.g., `2 + 3` → `5`).
-   **Dead Code Elimination**: Removes code that does not affect the program output (e.g., code after a `return` statement, or assignments to unused variables).

## Extending Mutators

To create a new mutator, implement the `Mutator` interface:

```python
from src.domain.interfaces import Mutator
from src.domain.ir import schema
from typing import List, Tuple

class MyCustomMutator(Mutator):
    def mutate(self, ir: schema.Module) -> List[Tuple[schema.Module, str]]:
        new_ir = copy.deepcopy(ir)
        # ... perform transformations ...
        return [(new_ir, "MyCustomStrategy")]
```

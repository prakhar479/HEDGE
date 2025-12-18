"""
Syntactic Layer Mutators - Code Patterns and Idiom Improvements

These mutators focus on:
- Python idiom optimization
- Code pattern improvements
- Syntactic sugar utilization
- Readability and maintainability enhancements
"""
import copy
import logging
from typing import List, Optional, Set
from src.application.mutators.base import LayeredMutator, MutationLayer, MutationResult, safe_deepcopy_ir, create_mutation_result
from src.application.mutators.semantic_base import LLMMutatorBase
from src.domain.ir import schema
from src.domain.ir.utils import NodeTransformer

logger = logging.getLogger(__name__)


class PythonicIdiomOptimizer(LayeredMutator):
    """
    Optimizes code to use Pythonic idioms and patterns.
    
    Focuses on converting verbose or non-Pythonic code into
    idiomatic Python that is both more readable and efficient.
    """
    
    def __init__(self, enabled_strategies: Optional[Set[str]] = None):
        super().__init__(MutationLayer.SYNTACTIC, enabled_strategies)
    
    def get_available_strategies(self) -> List[str]:
        return [
            "Idiom_ComprehensionOptimization",
            "Idiom_BuiltinUtilization",
            "Idiom_IteratorOptimization",
            "Idiom_ContextManagerUsage"
        ]
    
    def _apply_mutations(self, ir: schema.Module) -> List[MutationResult]:
        """Apply Pythonic idiom optimization mutations."""
        results = []
        
        # Strategy 1: List/Dict/Set Comprehensions
        if self._is_strategy_enabled("Idiom_ComprehensionOptimization"):
            variant = self._optimize_comprehensions(ir)
            if variant:
                results.append(create_mutation_result(
                    ir=variant,
                    strategy_name="Idiom_ComprehensionOptimization",
                    layer=MutationLayer.SYNTACTIC,
                    confidence=0.9,
                    description="Converted loops to comprehensions for better performance and readability"
                ))
        
        # Strategy 2: Built-in Function Utilization
        if self._is_strategy_enabled("Idiom_BuiltinUtilization"):
            variant = self._utilize_builtins(ir)
            if variant:
                results.append(create_mutation_result(
                    ir=variant,
                    strategy_name="Idiom_BuiltinUtilization",
                    layer=MutationLayer.SYNTACTIC,
                    confidence=0.85,
                    description="Replaced manual implementations with efficient built-in functions"
                ))
        
        # Strategy 3: Iterator and Generator Optimization
        if self._is_strategy_enabled("Idiom_IteratorOptimization"):
            variant = self._optimize_iterators(ir)
            if variant:
                results.append(create_mutation_result(
                    ir=variant,
                    strategy_name="Idiom_IteratorOptimization",
                    layer=MutationLayer.SYNTACTIC,
                    confidence=0.8,
                    description="Optimized iteration patterns using generators and iterators"
                ))
        
        # Strategy 4: Context Manager Usage
        if self._is_strategy_enabled("Idiom_ContextManagerUsage"):
            variant = self._optimize_context_managers(ir)
            if variant:
                results.append(create_mutation_result(
                    ir=variant,
                    strategy_name="Idiom_ContextManagerUsage",
                    layer=MutationLayer.SYNTACTIC,
                    confidence=0.75,
                    description="Improved resource management using context managers"
                ))
        
        return results
    
    def _optimize_comprehensions(self, ir: schema.Module) -> Optional[schema.Module]:
        """Convert loops to comprehensions where appropriate."""
        new_ir = safe_deepcopy_ir(ir)
        transformer = ComprehensionOptimizer()
        transformer.visit(new_ir)
        return new_ir if transformer.changed else None
    
    def _utilize_builtins(self, ir: schema.Module) -> Optional[schema.Module]:
        """Replace manual implementations with built-in functions."""
        new_ir = safe_deepcopy_ir(ir)
        transformer = BuiltinUtilizer()
        transformer.visit(new_ir)
        return new_ir if transformer.changed else None
    
    def _optimize_iterators(self, ir: schema.Module) -> Optional[schema.Module]:
        """Optimize iteration patterns using generators and iterators."""
        new_ir = safe_deepcopy_ir(ir)
        transformer = IteratorOptimizer()
        transformer.visit(new_ir)
        return new_ir if transformer.changed else None
    
    def _optimize_context_managers(self, ir: schema.Module) -> Optional[schema.Module]:
        """Improve resource management using context managers."""
        new_ir = safe_deepcopy_ir(ir)
        transformer = ContextManagerOptimizer()
        transformer.visit(new_ir)
        return new_ir if transformer.changed else None


class CodePatternOptimizer(LayeredMutator, LLMMutatorBase):
    """
    Optimizes common code patterns using LLM-based analysis.
    
    Identifies and improves common coding patterns that can be
    made more efficient or readable through syntactic changes.
    """
    
    def __init__(self, llm_client, enabled_strategies: Optional[Set[str]] = None):
        LayeredMutator.__init__(self, MutationLayer.SYNTACTIC, enabled_strategies)
        LLMMutatorBase.__init__(self, llm_client)
    
    def get_available_strategies(self) -> List[str]:
        return [
            "Pattern_LoopOptimization",
            "Pattern_ConditionalSimplification",
            "Pattern_FunctionComposition",
            "Pattern_ErrorHandling"
        ]
    
    def _apply_mutations(self, ir: schema.Module) -> List[MutationResult]:
        """Apply code pattern optimization mutations."""
        results = []
        code = self.codegen.generate(ir)
        allowed_imports = self._get_imports(ir)
        
        # Strategy 1: Loop Pattern Optimization
        if self._is_strategy_enabled("Pattern_LoopOptimization"):
            variant = self._optimize_loop_patterns(code, allowed_imports)
            if variant:
                results.append(create_mutation_result(
                    ir=variant,
                    strategy_name="Pattern_LoopOptimization",
                    layer=MutationLayer.SYNTACTIC,
                    confidence=0.8,
                    description="Optimized loop patterns for better performance and readability"
                ))
        
        # Strategy 2: Conditional Simplification
        if self._is_strategy_enabled("Pattern_ConditionalSimplification"):
            variant = self._simplify_conditionals(code, allowed_imports)
            if variant:
                results.append(create_mutation_result(
                    ir=variant,
                    strategy_name="Pattern_ConditionalSimplification",
                    layer=MutationLayer.SYNTACTIC,
                    confidence=0.85,
                    description="Simplified conditional logic and boolean expressions"
                ))
        
        # Strategy 3: Function Composition
        if self._is_strategy_enabled("Pattern_FunctionComposition"):
            variant = self._optimize_function_composition(code, allowed_imports)
            if variant:
                results.append(create_mutation_result(
                    ir=variant,
                    strategy_name="Pattern_FunctionComposition",
                    layer=MutationLayer.SYNTACTIC,
                    confidence=0.7,
                    description="Improved function composition and call patterns"
                ))
        
        # Strategy 4: Error Handling Patterns
        if self._is_strategy_enabled("Pattern_ErrorHandling"):
            variant = self._optimize_error_handling(code, allowed_imports)
            if variant:
                results.append(create_mutation_result(
                    ir=variant,
                    strategy_name="Pattern_ErrorHandling",
                    layer=MutationLayer.SYNTACTIC,
                    confidence=0.75,
                    description="Improved error handling patterns and exception management"
                ))
        
        return results
    
    def _optimize_loop_patterns(self, code: str, allowed_imports: Set[str]) -> Optional[schema.Module]:
        """Optimize loop patterns for better performance."""
        prompt = f"""You are an expert in Python loop optimization and iteration patterns.

Optimize the loop patterns in this code for better performance and readability:

LOOP OPTIMIZATIONS:
- Convert manual index loops to enumerate() where appropriate
- Use zip() for parallel iteration instead of manual indexing
- Replace range(len()) patterns with direct iteration
- Convert nested loops to itertools.product where beneficial
- Use any()/all() instead of manual boolean accumulation
- Apply list comprehensions for simple transformations
- Use generator expressions for memory efficiency

PERFORMANCE PATTERNS:
- Minimize repeated attribute lookups in loops
- Use local variable caching for frequently accessed items
- Apply early termination with break/continue where possible
- Optimize loop invariant code motion

Available imports: {allowed_imports}

Code:
{code}

Return ONLY the loop-optimized code.
"""
        return self._mutate_with_prompt(code, prompt, allowed_imports)
    
    def _simplify_conditionals(self, code: str, allowed_imports: Set[str]) -> Optional[schema.Module]:
        """Simplify conditional logic and boolean expressions."""
        prompt = f"""You are an expert in boolean logic simplification and conditional optimization.

Simplify the conditional logic in this code:

CONDITIONAL OPTIMIZATIONS:
- Apply De Morgan's laws to simplify boolean expressions
- Use truthiness testing instead of explicit comparisons (if x: vs if x != None:)
- Combine multiple conditions using logical operators
- Use conditional expressions (ternary operator) for simple cases
- Apply early returns to reduce nesting depth
- Eliminate redundant conditions and impossible branches

BOOLEAN SIMPLIFICATIONS:
- not (a and b) -> (not a) or (not b)
- not (a or b) -> (not a) and (not b)
- if x == True: -> if x:
- if x == False: -> if not x:
- if len(x) > 0: -> if x:

Available imports: {allowed_imports}

Code:
{code}

Return ONLY the conditionally simplified code.
"""
        return self._mutate_with_prompt(code, prompt, allowed_imports)
    
    def _optimize_function_composition(self, code: str, allowed_imports: Set[str]) -> Optional[schema.Module]:
        """Optimize function composition and call patterns."""
        prompt = f"""You are an expert in function composition and call optimization.

Optimize function composition and calling patterns in this code:

FUNCTION OPTIMIZATIONS:
- Combine multiple function calls where possible
- Use functools.partial for partial application
- Apply function composition to reduce intermediate variables
- Optimize recursive calls with tail recursion where applicable
- Use lambda functions for simple transformations
- Apply map(), filter(), reduce() for functional patterns

CALL PATTERN OPTIMIZATIONS:
- Minimize function call overhead in hot paths
- Use method chaining where appropriate
- Optimize argument passing and unpacking
- Apply decorator patterns for cross-cutting concerns

Available imports: {allowed_imports}

Code:
{code}

Return ONLY the function-optimized code.
"""
        return self._mutate_with_prompt(code, prompt, allowed_imports)
    
    def _optimize_error_handling(self, code: str, allowed_imports: Set[str]) -> Optional[schema.Module]:
        """Optimize error handling patterns."""
        prompt = f"""You are an expert in Python error handling and exception management.

Optimize error handling patterns in this code:

ERROR HANDLING OPTIMIZATIONS:
- Use EAFP (Easier to Ask for Forgiveness than Permission) patterns
- Replace explicit checks with try/except where appropriate
- Use specific exception types instead of broad catches
- Apply context managers for resource cleanup
- Optimize exception handling performance
- Use else clauses in try/except blocks effectively

PATTERN IMPROVEMENTS:
- if key in dict: dict[key] -> try: dict[key] except KeyError:
- if hasattr(obj, 'attr'): obj.attr -> try: obj.attr except AttributeError:
- Proper exception chaining and context preservation
- Use finally blocks for cleanup when needed

Available imports: {allowed_imports}

Code:
{code}

Return ONLY the error-handling optimized code.
"""
        return self._mutate_with_prompt(code, prompt, allowed_imports)


# Transformer implementations for syntactic optimizations
class ComprehensionOptimizer(NodeTransformer):
    """Converts loops to comprehensions where appropriate."""
    
    def __init__(self):
        self.changed = False
    
    def visit_For(self, node: schema.For) -> schema.Statement:
        node = self.generic_visit(node)
        
        # Look for simple append patterns that can become list comprehensions
        if (len(node.body.statements) == 1 and
            isinstance(node.body.statements[0], schema.ExprStmt) and
            isinstance(node.body.statements[0].value, schema.Call)):
            
            call = node.body.statements[0].value
            if (isinstance(call.func, schema.Attribute) and 
                call.func.attr == 'append' and len(call.args) == 1):
                
                # This is a simple append pattern - could be converted to comprehension
                # For now, we'll mark it as a potential optimization
                pass
        
        return node


class BuiltinUtilizer(NodeTransformer):
    """Replaces manual implementations with built-in functions."""
    
    def __init__(self):
        self.changed = False
    
    def visit_For(self, node: schema.For) -> schema.Statement:
        node = self.generic_visit(node)
        
        # Look for manual sum implementations
        if (len(node.body.statements) == 1 and
            isinstance(node.body.statements[0], schema.AugAssign) and
            node.body.statements[0].op == '+'):
            
            # This might be a manual sum - could use built-in sum()
            pass
        
        return node


class IteratorOptimizer(NodeTransformer):
    """Optimizes iteration patterns."""
    
    def __init__(self):
        self.changed = False
    
    def visit_For(self, node: schema.For) -> schema.Statement:
        node = self.generic_visit(node)
        
        # Look for range(len()) patterns
        if (isinstance(node.iter, schema.Call) and
            isinstance(node.iter.func, schema.Name) and
            node.iter.func.id == 'range' and
            len(node.iter.args) == 1 and
            isinstance(node.iter.args[0], schema.Call) and
            isinstance(node.iter.args[0].func, schema.Name) and
            node.iter.args[0].func.id == 'len'):
            
            # This is range(len(something)) - could be optimized to enumerate
            pass
        
        return node


class ContextManagerOptimizer(NodeTransformer):
    """Optimizes resource management using context managers."""
    
    def __init__(self):
        self.changed = False
    
    def visit_Try(self, node: schema.Try) -> schema.Statement:
        node = self.generic_visit(node)
        
        # Look for resource management patterns that could use context managers
        # This would require more sophisticated analysis
        
        return node
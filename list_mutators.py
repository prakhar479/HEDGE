#!/usr/bin/env python3
"""
Simple script to list all available mutators and their strategies.
This helps users understand what optimization layers and strategies are available.
"""

def list_mutators():
    """List all available mutators organized by layer."""
    
    layers = {
        "🧠 Semantic Layer (Highest Level)": {
            "description": "Algorithm intent and high-level logic optimization (requires LLM)",
            "mutators": {
                "AlgorithmicIntentMutator": [
                    "ComplexityReduction - Reduces Big-O complexity through better algorithms",
                    "PatternRecognition - Recognizes and optimizes common algorithmic patterns",
                    "ArchitecturalImprovement - Improves program architecture and design patterns"
                ],
                "ProgramIntentMutator": [
                    "LogicSimplification - Simplifies complex logic while preserving functionality",
                    "FlowOptimization - Optimizes control flow and execution paths",
                    "PurposeAlignment - Aligns implementation with intended purpose"
                ]
            }
        },
        "📊 Algorithmic Layer": {
            "description": "Data structure and complexity improvements",
            "mutators": {
                "DataStructureOptimizer": [
                    "MembershipOptimization - List → Set conversion for O(1) membership testing",
                    "AccessPatternOptimization - Optimizes data access patterns for cache locality",
                    "InsertionOptimization - List → deque for frequent insertions/deletions",
                    "SearchOptimization - Optimizes search operations using efficient algorithms"
                ],
                "ComplexityReducer": [
                    "NestedLoopReduction - Converts nested loops to more efficient patterns",
                    "SortingOptimization - Optimizes sorting operations for better complexity",
                    "DuplicateWorkElimination - Eliminates redundant computations",
                    "MathematicalOptimization - Applies mathematical optimizations"
                ]
            }
        },
        "🐍 Syntactic Layer": {
            "description": "Code patterns and Python idiom improvements",
            "mutators": {
                "PythonicIdiomOptimizer": [
                    "ComprehensionOptimization - Converts loops to comprehensions",
                    "BuiltinUtilization - Replaces manual implementations with built-ins",
                    "IteratorOptimization - Optimizes iteration patterns using generators",
                    "ContextManagerUsage - Improves resource management"
                ],
                "CodePatternOptimizer": [
                    "LoopOptimization - Optimizes loop patterns for better performance",
                    "ConditionalSimplification - Simplifies boolean expressions and conditions",
                    "FunctionComposition - Optimizes function composition and call patterns",
                    "ErrorHandling - Improves error handling patterns"
                ]
            }
        },
        "⚡ Micro Layer (Lowest Level)": {
            "description": "Low-level performance optimizations",
            "mutators": {
                "ConstantOptimizer": [
                    "Folding - Evaluates constant expressions at compile time",
                    "Propagation - Propagates constant values through assignments",
                    "BooleanSimplification - Simplifies boolean expressions with constants",
                    "ArithmeticSimplification - Simplifies arithmetic with identity operations"
                ],
                "DeadCodeEliminator": [
                    "UnreachableElimination - Removes code after returns/breaks",
                    "UnusedVariableElimination - Removes assignments to unused variables",
                    "PureExpressionElimination - Removes pure expressions with no side effects",
                    "EmptyBlockElimination - Removes empty code blocks"
                ],
                "LoopMicroOptimizer": [
                    "SmallUnrolling - Unrolls small loops for better performance",
                    "StrengthReduction - Replaces expensive operations in loops",
                    "InvariantMotion - Moves loop-invariant code outside loops",
                    "BoundsOptimization - Optimizes loop bounds and iteration patterns"
                ]
            }
        }
    }
    
    print("HEDGE - Hierarchical Mutation Layers")
    print("=" * 50)
    print()
    
    for layer_name, layer_info in layers.items():
        print(f"{layer_name}")
        print(f"Purpose: {layer_info['description']}")
        print()
        
        for mutator_name, strategies in layer_info['mutators'].items():
            print(f"  {mutator_name}:")
            for strategy in strategies:
                print(f"    • {strategy}")
            print()
        
        print("-" * 50)
        print()
    
    print("Usage Examples:")
    print("  # Micro-optimizations only")
    print("  python hedge.py optimize code.py tests.py --level micro")
    print()
    print("  # Standard layered optimization")
    print("  python hedge.py optimize code.py tests.py --level standard")
    print()
    print("  # Advanced with semantic layer (requires LLM)")
    print("  export GEMINI_API_KEY='your-key'")
    print("  python hedge.py optimize code.py tests.py --level advanced")
    print()
    print("  # Custom layer selection")
    print("  python hedge.py optimize code.py tests.py --layers algorithmic,micro")
    print()
    print("  # Exclude specific mutators")
    print("  python hedge.py optimize code.py tests.py --exclude-mutators 'ConstantOptimizer,DeadCodeEliminator'")

if __name__ == "__main__":
    list_mutators()
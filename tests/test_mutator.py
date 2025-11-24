from src.mutator.simple import SimpleMutator

def test_mutator_bubble_sort():
    mutator = SimpleMutator()
    code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
"""
    variants = mutator.mutate(code)
    assert len(variants) > 0
    assert "sorted(arr)" in variants[0]

def test_mutator_fib():
    mutator = SimpleMutator()
    code = """
def fib_recursive(n):
    if n <= 1: return n
    return fib_recursive(n-1) + fib_recursive(n-2)
"""
    variants = mutator.mutate(code)
    assert len(variants) > 0
    # Check for iterative logic
    assert "range(2, n + 1)" in variants[0]

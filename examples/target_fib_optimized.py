import functools
@functools.lru_cache(maxsize=None)
def fib_recursive(n):
    'Recursive Fibonacci - inefficient O(2^n)'
    if (n <= 1):
        return n
    return (fib_recursive((n - 2)) + fib_recursive((n - 1)))
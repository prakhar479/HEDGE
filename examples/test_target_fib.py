def test():
    # Test correctness
    assert candidate.fib_recursive(0) == 0
    assert candidate.fib_recursive(1) == 1
    assert candidate.fib_recursive(5) == 5
    assert candidate.fib_recursive(10) == 55
    
    # Larger test for energy measurement
    # Recursive fib is very slow, so we use a moderate value
    result = candidate.fib_recursive(25)
    assert result == 75025

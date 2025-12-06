"""
Test suite for EvoEval/63
Auto-generated from EvoEval benchmark
"""

from target import customFibFib


def test_customFibFib():
    """Test all cases for customFibFib."""

    test_cases = [
        (5, [-1, 0, 1], 1000),  # Test case 1
        (8, [0, 1, 2], 5),  # Test case 2
        (1, [1, 1, 2], 1000),  # Test case 3
        (10, [0, 0, 1], 100000),  # Test case 4
        (20, [-1, 2, 3], 1000000),  # Test case 5
        (15, [1, 1, 1], 50000),  # Test case 6
        (25, [3, 5, 8], 300000),  # Test case 7
        (30, [-1, -2, -3], 100000),  # Test case 8
        (7, [2, 1, 3], 500000),  # Test case 9
        (12, [0, -1, -2], 200000),  # Test case 10
        (18, [2, 0, 2], 10000),  # Test case 11
        (0, [1, 2, 3], 1000),  # Test case 12
        (22, [-3, -5, -8], 500000),  # Test case 13
        (17, [1, 0, -1], 250000),  # Test case 14
        (13, [0, 0, 0], 1000),  # Test case 15
        (6, [1, 2, 3], 1000),  # Test case 16
        (10, [0, 1, 2], 500),  # Test case 17
        (0, [1, 2, 3], 1000),  # Test case 18
        (15, [2, 5, 7], 10000),  # Test case 19
        (20, [-1, 1, 2], 100000),  # Test case 20
        (3, [1, 1, 2], 10),  # Test case 21
        (12, [3, 4, 5], 1000),  # Test case 22
        (7, [0, 0, 1], 100),  # Test case 23
        (4, [2, 3, 5], 50),  # Test case 24
        (9, [1, -1, 1], 1000),  # Test case 25
        (0, [0, 0, 0], 1000),  # Test case 26
        (1, [1, 1, 1], 1),  # Test case 27
        (2, [-1, -1, -1], 1),  # Test case 28
        (50, [1, 1, 2], 10000),  # Test case 29
        (3, [5, 5, 5], 10),  # Test case 30
        (4, [-5, -5, -5], 5),  # Test case 31
        (100, [0, 0, 0], 1000),  # Test case 32
        (1000, [1, 2, 3], 100000),  # Test case 33
        (5000, [1, 1, 1], 1000000),  # Test case 34
        (10, [10, 10, 10], 100),  # Test case 35
        (0, [100, 200, 300], 1000),  # Test case 36
        (1, [1000, 2000, 3000], 5000),  # Test case 37
        (2, [10000, 20000, 30000], 100000),  # Test case 38
        (50, [0, 1, 2], 1000000000),  # Test case 39
        (20, [-5, 10, -15], 1000),  # Test case 40
        (30, [1, 2, 3], 500),  # Test case 41
        (0, [100, 200, 300], 1000),  # Test case 42
        (10, [100, 200, 300], 100000),  # Test case 43
        (15, [1, 1, 1], 100),  # Test case 44
        (25, [3, 2, 1], 50000),  # Test case 45
        (35, [-1, -2, -3], 1000),  # Test case 46
        (45, [10, 20, 30], 500000),  # Test case 47
        (55, [5, -5, 10], 10000000),  # Test case 48
        (20, [1, 2, 3], 100000),  # Test case 49
        (30, [-2, 0, 2], 1000000),  # Test case 50
        (15, [0, 0, 0], 0),  # Test case 51
        (25, [-1, -1, -1], 10),  # Test case 52
        (35, [5, 5, 5], 500),  # Test case 53
        (45, [-10, 0, 10], 10000),  # Test case 54
        (100, [1, 1, 1], 100000000),  # Test case 55
        (50, [0, 1, 1], 50000),  # Test case 56
        (75, [1, 2, 3], 10000000),  # Test case 57
        (40, [-1, -2, -3], 1000),  # Test case 58
    ]

    for i, test_input in enumerate(test_cases):
        try:
            # Handle single vs multiple arguments
            if isinstance(test_input, tuple):
                result = customFibFib(*test_input)
            else:
                result = customFibFib(test_input)
            # Test passed if no exception
        except Exception as e:
            print(f"Test case {i+1} failed: {e}")
            raise


if __name__ == "__main__":
    test_customFibFib()
    print(f"All tests passed for customFibFib!")

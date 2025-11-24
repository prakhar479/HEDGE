import random

def test():
    # Test case 1: Simple list
    assert candidate.bubble_sort([3, 1, 2]) == [1, 2, 3]
    
    # Test case 2: Reverse sorted
    assert candidate.bubble_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]
    
    # Test case 3: Random list (larger for energy measurement)
    random.seed(42)
    large_list = [random.randint(0, 1000) for _ in range(1000)]
    sorted_list = sorted(large_list)
    assert candidate.bubble_sort(large_list) == sorted_list

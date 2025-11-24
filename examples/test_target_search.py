def test():
    # Test basic cases
    assert candidate.search_list([1, 2, 3, 4, 5], 3) == 2
    assert candidate.search_list([1, 2, 3, 4, 5], 1) == 0
    assert candidate.search_list([1, 2, 3, 4, 5], 5) == 4
    assert candidate.search_list([1, 2, 3, 4, 5], 10) == -1
    
    # Larger test for energy measurement
    large_list = list(range(10000))
    # Worst case: search for last element
    assert candidate.search_list(large_list, 9999) == 9999
    # Not found case
    assert candidate.search_list(large_list, 20000) == -1

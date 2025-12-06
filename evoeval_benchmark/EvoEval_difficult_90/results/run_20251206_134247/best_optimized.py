def next_smallest_and_largest(lst):
    if (len(lst) < 2):
        return (None, None)
    unique_nums = sorted(list(set(lst)))
    if (len(unique_nums) < 2):
        return (None, None)
    return (unique_nums[1], unique_nums[-2])
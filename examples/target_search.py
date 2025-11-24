def search_list(items, target):
    """Linear search - O(n)"""
    for i in range(len(items)):
        if items[i] == target:
            return i
    return -1


def process_data(numbers):
    """
    A complex function demonstrating various inefficiencies:
    1. Bubble Sort (O(n^2)) -> Should be sorted() (O(n log n))
    2. Manual Filter/Map -> Should be List Comprehension
    3. Manual Sum -> Should be sum()
    4. Power operation -> Should be multiplication (Strength Reduction)
    5. Dead Code -> Should be removed
    """
    # 1. Inefficient Sorting (Bubble Sort)
    n = len(numbers)
    sorted_nums = list(numbers) # Copy
    for i in range(n):
        for j in range(0, n-i-1):
            if sorted_nums[j] > sorted_nums[j+1]:
                sorted_nums[j], sorted_nums[j+1] = sorted_nums[j+1], sorted_nums[j]
    
    # 2. Manual Filtering & Transformation
    # Filter even numbers and multiply by 3
    processed = []
    for x in sorted_nums:
        if x % 2 == 0:
            processed.append(x * 3)
            
    # 3. Manual Summation
    total = 0
    for x in processed:
        total += x
        
    # 4. Expensive Operation (Strength Reduction: x ** 2)
    variance_term = 0
    mean = total / (len(processed) if len(processed) > 0 else 1)
    
    # 5. Loop with invariant (if I put one there) 
    # But let's stick to strength reduction
    for x in processed:
        diff = x - mean
        variance_term += diff ** 2
        
    # 6. Dead Code
    if False:
        print("Debug info")
        return -1
        
    return total, int(variance_term)

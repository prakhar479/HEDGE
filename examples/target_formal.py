def target_function(n):
    # Constant Folding
    x = 24 * 60 * 60
    
    # Dead Code Elimination
    if False:
        print("This should be removed")
        
    # Strength Reduction
    y = n ** 2
    
    # Loop Unrolling
    res = 0
    for i in range(3):
        res += i
        
    return x + y + res

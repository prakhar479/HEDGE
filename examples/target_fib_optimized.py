def _multiply_matrices_fib(A, B):
    a, b = A[0][0], A[0][1]
    c, d = A[1][0], A[1][1]

    e, f = B[0][0], B[0][1]
    g, h = B[1][0], B[1][1]

    return [
        [a*e + b*g, a*f + b*h],
        [c*e + d*g, c*f + d*h]
    ]

def _matrix_pow_fib(M, power):
    result = [[1, 0], [0, 1]]
    base = M

    while power > 0:
        if power % 2 == 1:
            result = _multiply_matrices_fib(result, base)
        base = _multiply_matrices_fib(base, base)
        power //= 2
    return result

def fib_recursive(n):
    """
    Optimized Fibonacci calculation using matrix exponentiation (O(log n) time, O(1) space).
    This method provides significantly faster execution for large values of n compared to
    the iterative O(n) approach.
    """
    if n <= 1:
        return n
    
    transformation_matrix = [[1, 1], [1, 0]]
    
    res_matrix = _matrix_pow_fib(transformation_matrix, n)
    return res_matrix[1][0]
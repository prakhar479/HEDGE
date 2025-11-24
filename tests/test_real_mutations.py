import ast
import astor
from src.mutator.simple import SimpleMutator

def test_loop_unrolling():
    code = """
x = 0
for i in range(3):
    x = x + 1
"""
    mutator = SimpleMutator()
    variants = mutator.mutate(code)
    
    # Check if any variant has unrolled loop (no for loop, just repeated statements)
    unrolled_found = False
    for v in variants:
        if "for i in range" not in v and "x = x + 1" in v:
            # Should appear 3 times
            if v.count("x = x + 1") == 3:
                unrolled_found = True
                break
    
    assert unrolled_found, "Loop unrolling failed"

def test_list_comp():
    code = """
res = []
for x in items:
    res.append(x * 2)
"""
    mutator = SimpleMutator()
    variants = mutator.mutate(code)
    
    # Check for list comprehension
    list_comp_found = False
    for v in variants:
        if "res.extend([x * 2 for x in items])" in v or "res.extend([(x * 2) for x in items])" in v:
            list_comp_found = True
            break
            
    assert list_comp_found, "List comprehension transformation failed"

def test_aug_assign():
    code = """
x = x + 1
"""
    mutator = SimpleMutator()
    variants = mutator.mutate(code)
    
    aug_assign_found = False
    for v in variants:
        if "x += 1" in v:
            aug_assign_found = True
            break
            
    assert aug_assign_found, "AugAssign transformation failed"

if __name__ == "__main__":
    test_loop_unrolling()
    test_list_comp()
    test_aug_assign()
    print("All mutation tests passed!")

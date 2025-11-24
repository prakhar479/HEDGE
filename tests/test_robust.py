from src.mutator.robust import RobustMutator

def test_robust_mutator_range():
    mutator = RobustMutator()
    code = """
for i in range(0, 10):
    pass
"""
    variants = mutator.mutate(code)
    # Should contain range(10)
    assert any("range(10)" in v for v in variants)

def test_robust_mutator_aug_assign():
    mutator = RobustMutator()
    code = """
x = 1
x = x + 1
"""
    variants = mutator.mutate(code)
    # Should contain x += 1
    assert any("x += 1" in v for v in variants)

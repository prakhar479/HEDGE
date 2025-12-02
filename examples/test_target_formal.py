def test():
    from examples.target_formal import target_function
    assert target_function(10) == 86400 + 100 + 3

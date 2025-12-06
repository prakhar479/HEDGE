def correct_bracketing_advanced(brackets):
    stack = []
    bracket_map = {'(': ')', '[': ']', '{': '}'}
    for bracket in brackets:
        if (bracket in bracket_map):
            stack.append(bracket)
        else:
            if ((not stack) or (bracket_map.get(stack.pop()) != bracket)):
                return False
    return (not stack)
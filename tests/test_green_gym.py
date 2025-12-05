import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.green_gym.runner import CodeRunner

def test_runner_success():
    runner = CodeRunner()
    code = """
def add(a, b):
    return a + b
"""
    test_code = """
def test():
    assert candidate.add(1, 2) == 3
"""
    success, metrics, output = runner.run(code, test_code)
    assert success
    assert "duration_seconds" in metrics
    # Energy might be 0 if codecarbon fails or is too fast, but key should exist
    assert "energy_joules" in metrics 

def test_runner_failure():
    runner = CodeRunner()
    code = """
def add(a, b):
    return a - b # Bug
"""
    test_code = """
def test():
    assert candidate.add(1, 2) == 3
"""
    success, metrics, output = runner.run(code, test_code)
    assert not success

def test_runner_timeout():
    runner = CodeRunner(timeout_seconds=1)
    code = """
import time
def loop():
    while True:
        time.sleep(0.1)
"""
    test_code = """
def test():
    candidate.loop()
"""
    success, metrics, output = runner.run(code, test_code)
    assert not success
    assert metrics.get("timeout") is True

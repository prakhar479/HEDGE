
import pytest
import sys
import os

# Ensure current directory is in path so we can import the target
sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from target_complex import process_data

def test_process_data_small():
    data = [5, 2, 9, 1, 5, 6]
    # Sorted: 1, 2, 5, 5, 6, 9
    # Evens: 2, 6
    # Processed (x*3): 6, 18
    # Total: 24
    # Mean: 12
    # Variance term: (6-12)^2 + (18-12)^2 = 36 + 36 = 72
    
    total, var = process_data(data)
    assert total == 24
    assert var == 72

def test_process_data_empty():
    total, var = process_data([])
    assert total == 0
    assert var == 0

def test_process_data_large():
    # Only odds
    data = [2*i+1 for i in range(10000)]
    total, var = process_data(data)
    assert total == 0
    assert var == 0

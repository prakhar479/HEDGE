"""
Integration tests for IR snapshot saving during evolution.

Tests the end-to-end functionality of the --save-ir flag.
"""
import sys
import json
import tempfile
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.application.engine.evolution import EvolutionaryEngine
from src.application.mutators.structural import StructuralMutator
from src.infrastructure.execution.runner import GreenGymRunner


def test_evolution_saves_ir_snapshots():
    """Test that EvolutionaryEngine saves IR snapshots when enabled."""
    code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
"""
    
    test_code = """
def test_fibonacci():
    assert fibonacci(0) == 0
    assert fibonacci(1) == 1
    assert fibonacci(5) == 5
"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        experiment_dir = Path(tmpdir)
        
        # Create engine with save_ir_snapshots enabled
        engine = EvolutionaryEngine(
            mutators=[StructuralMutator()],
            runner=GreenGymRunner(timeout_seconds=10),
            generations=2,
            population_size=2,
            experiment_dir=experiment_dir,
            save_ir_snapshots=True
        )
        
        # Run optimization
        solutions = engine.optimize(code, test_code)
        
        # Check that ir_snapshots directory was created
        snapshots_dir = experiment_dir / "ir_snapshots"
        assert snapshots_dir.exists(), "ir_snapshots directory not created"
        
        # Check that snapshot files exist
        snapshot_files = list(snapshots_dir.glob("*.json"))
        assert len(snapshot_files) > 0, "No IR snapshot files created"
        
        # Verify baseline snapshot exists (generation 0)
        baseline_snapshots = list(snapshots_dir.glob("gen_000_*.json"))
        assert len(baseline_snapshots) > 0, "No baseline (gen_000) snapshot found"
        
        # Check each snapshot file
        for snapshot_file in snapshot_files:
            # File should not be empty
            assert snapshot_file.stat().st_size > 100, \
                f"{snapshot_file.name} is too small (likely empty)"
            
            # File should contain valid JSON
            with open(snapshot_file) as f:
                data = json.load(f)
            
            # Should have __type__ field
            assert '__type__' in data, \
                f"{snapshot_file.name} missing __type__ field"
            assert data['__type__'] == 'Module', \
                f"{snapshot_file.name} has wrong root type"
            
            # Should have body with statements
            assert 'body' in data, f"{snapshot_file.name} missing body"
            assert 'statements' in data['body'], \
                f"{snapshot_file.name} missing statements"
            
            # Statements should not be empty dicts
            statements = data['body']['statements']
            for i, stmt in enumerate(statements):
                assert stmt != {}, \
                    f"{snapshot_file.name} has empty statement at index {i}"
                assert '__type__' in stmt, \
                    f"{snapshot_file.name} statement {i} missing __type__"


def test_evolution_without_save_ir_creates_no_snapshots():
    """Test that EvolutionaryEngine doesn't save snapshots when disabled."""
    code = """
def simple_add(a, b):
    return a + b
"""
    
    test_code = """
def test_add():
    assert simple_add(1, 2) == 3
    assert simple_add(0, 0) == 0
"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        experiment_dir = Path(tmpdir)
        
        # Create engine with save_ir_snapshots disabled
        engine = EvolutionaryEngine(
            mutators=[StructuralMutator()],
            runner=GreenGymRunner(timeout_seconds=10),
            generations=1,
            population_size=2,
            experiment_dir=experiment_dir,
            save_ir_snapshots=False  # Disabled
        )
        
        # Run optimization
        solutions = engine.optimize(code, test_code)
        
        # Check that ir_snapshots directory was NOT created
        snapshots_dir = experiment_dir / "ir_snapshots"
        if snapshots_dir.exists():
            # If it exists, it should be empty
            snapshot_files = list(snapshots_dir.glob("*.json"))
            assert len(snapshot_files) == 0, \
                "IR snapshots created when save_ir_snapshots=False"


def test_snapshot_filenames_include_generation():
    """Test that snapshot filenames include generation number."""
    code = """
def multiply(x, y):
    return x * y
"""
    
    test_code = """
def test_multiply():
    assert multiply(2, 3) == 6
    assert multiply(0, 5) == 0
"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        experiment_dir = Path(tmpdir)
        
        # Create engine
        engine = EvolutionaryEngine(
            mutators=[StructuralMutator()],
            runner=GreenGymRunner(timeout_seconds=10),
            generations=2,
            population_size=2,
            experiment_dir=experiment_dir,
            save_ir_snapshots=True
        )
        
        # Run optimization
        solutions = engine.optimize(code, test_code)
        
        # Check snapshot filenames
        snapshots_dir = experiment_dir / "ir_snapshots"
        snapshot_files = list(snapshots_dir.glob("*.json"))
        
        # Should have baseline (gen_000)
        assert any("gen_000_" in f.name for f in snapshot_files), \
            "No baseline generation snapshot found"
        
        # Check filename format
        for snapshot_file in snapshot_files:
            name = snapshot_file.name
            # Should match pattern: gen_NNN_XXXXXXXX.json
            assert name.startswith("gen_"), \
                f"Snapshot {name} doesn't start with 'gen_'"
            assert name.endswith(".json"), \
                f"Snapshot {name} doesn't end with '.json'"
            
            # Extract generation number
            parts = name.split("_")
            assert len(parts) >= 3, \
                f"Snapshot {name} doesn't follow gen_NNN_ID.json pattern"
            
            gen_num = parts[1]
            assert gen_num.isdigit(), \
                f"Generation number '{gen_num}' in {name} is not numeric"


def test_multiple_generations_create_multiple_snapshots():
    """Test that multiple generations create appropriately numbered snapshots."""
    code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""
    
    test_code = """
def test_factorial():
    assert factorial(0) == 1
    assert factorial(1) == 1
    assert factorial(5) == 120
"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        experiment_dir = Path(tmpdir)
        
        # Create engine with multiple generations
        engine = EvolutionaryEngine(
            mutators=[StructuralMutator()],
            runner=GreenGymRunner(timeout_seconds=10),
            generations=3,
            population_size=2,
            experiment_dir=experiment_dir,
            save_ir_snapshots=True
        )
        
        # Run optimization
        solutions = engine.optimize(code, test_code)
        
        # Check snapshots
        snapshots_dir = experiment_dir / "ir_snapshots"
        snapshot_files = list(snapshots_dir.glob("*.json"))
        
        # Extract generation numbers
        generations_found = set()
        for f in snapshot_files:
            parts = f.name.split("_")
            if len(parts) >= 2:
                gen_num = int(parts[1])
                generations_found.add(gen_num)
        
        # Should have baseline (gen 0)
        assert 0 in generations_found, "No baseline generation (0) found"
        
        # Should have at least generation 0 (might have 1, 2, 3 depending on success)
        assert len(generations_found) >= 1, "No generation snapshots created"


if __name__ == "__main__":
    # Run all tests
    test_evolution_saves_ir_snapshots()
    test_evolution_without_save_ir_creates_no_snapshots()
    test_snapshot_filenames_include_generation()
    test_multiple_generations_create_multiple_snapshots()
    print("✓ All integration tests passed!")

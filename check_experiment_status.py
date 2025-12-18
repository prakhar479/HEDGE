#!/usr/bin/env python3
"""
Quick status checker for running experiments.
"""
import sys
import json
from pathlib import Path
from datetime import datetime

def check_status():
    """Check status of all experiments."""
    
    # Find the most recent comprehensive experiment directory
    experiments_dir = Path("experiments")
    comprehensive_dirs = sorted([d for d in experiments_dir.glob("comprehensive_*") if d.is_dir()])
    
    if not comprehensive_dirs:
        print("No comprehensive experiments found!")
        return
    
    latest_dir = comprehensive_dirs[-1]
    print(f"\n{'='*80}")
    print(f"EXPERIMENT STATUS: {latest_dir.name}")
    print(f"{'='*80}\n")
    
    # Check for suite summary
    summary_file = latest_dir / "suite_summary.json"
    if summary_file.exists():
        with open(summary_file, 'r') as f:
            summary = json.load(f)
        
        print("✓ EXPERIMENTS COMPLETE!")
        print(f"\nTotal Experiments: {summary['total_experiments']}")
        print(f"Successful: {summary['successful']}")
        print(f"Failed: {summary['failed']}")
        print(f"Total Duration: {summary['total_duration']:.2f}s ({summary['total_duration']/60:.2f} minutes)")
        
        print("\nIndividual Results:")
        for result in summary['results']:
            status = "✓" if result['success'] else "✗"
            print(f"  {status} {result['name']}: {result['duration']:.2f}s")
        
        print(f"\n{'='*80}")
        print("Next Steps:")
        print(f"  1. Run: python aggregate_results.py {latest_dir}")
        print(f"  2. View: {latest_dir}/aggregated/comprehensive_report.html")
        print(f"{'='*80}\n")
        return
    
    # Check individual experiment directories
    exp_dirs = sorted([d for d in latest_dir.iterdir() if d.is_dir()])
    
    completed = []
    running = []
    pending = []
    
    for exp_dir in exp_dirs:
        config_file = exp_dir / "config.json"
        results_file = exp_dir / "pareto_results.json"
        
        if results_file.exists():
            completed.append(exp_dir.name)
        elif config_file.exists():
            running.append(exp_dir.name)
        else:
            pending.append(exp_dir.name)
    
    print(f"Completed: {len(completed)}")
    for name in completed:
        print(f"  ✓ {name}")
    
    print(f"\nRunning: {len(running)}")
    for name in running:
        print(f"  ⟳ {name}")
    
    print(f"\nPending: {len(pending)}")
    for name in pending:
        print(f"  ○ {name}")
    
    total = len(completed) + len(running) + len(pending)
    if total > 0:
        progress = (len(completed) / total) * 100
        print(f"\nProgress: {progress:.1f}% ({len(completed)}/{total})")
    
    # Show latest experiment details
    if completed:
        latest_exp = latest_dir / completed[-1]
        results_file = latest_exp / "pareto_results.json"
        
        if results_file.exists():
            with open(results_file, 'r') as f:
                results = json.load(f)
            
            print(f"\nLatest Completed: {completed[-1]}")
            print(f"  Solutions Found: {len(results)}")
            
            if results:
                baseline_energy = results[0]['metrics'].get('energy_joules', 0)
                best_energy = min(r['metrics'].get('energy_joules', float('inf')) for r in results)
                
                if baseline_energy > 0:
                    improvement = ((baseline_energy - best_energy) / baseline_energy) * 100
                    print(f"  Energy Improvement: {improvement:.2f}%")
                    print(f"  Baseline: {baseline_energy:.4f} J")
                    print(f"  Best: {best_energy:.4f} J")
    
    print(f"\n{'='*80}")
    print("Monitoring:")
    print(f"  Run this script again to check progress")
    print(f"  Or check: {latest_dir}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    try:
        check_status()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

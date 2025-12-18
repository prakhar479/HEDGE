#!/usr/bin/env python3
"""
Aggregate and visualize results from comprehensive experiments.
"""
import json
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend

def load_experiment_results(exp_dir):
    """Load results from a single experiment."""
    results_file = exp_dir / "pareto_results.json"
    stats_file = exp_dir / "statistics.json"
    config_file = exp_dir / "config.json"
    
    if not results_file.exists():
        return None
    
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    stats = {}
    if stats_file.exists():
        with open(stats_file, 'r') as f:
            stats = json.load(f)
    
    config = {}
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
    
    return {
        "results": results,
        "stats": stats,
        "config": config,
        "name": exp_dir.name
    }

def create_comparison_charts(all_experiments, output_dir):
    """Create comparison charts across all experiments."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Energy Improvement Comparison
    fig, ax = plt.subplots(figsize=(14, 8))
    
    exp_names = []
    improvements = []
    
    for exp in all_experiments:
        if not exp['results']:
            continue
        
        results = exp['results']
        if len(results) < 2:
            continue
        
        # Calculate improvement (baseline vs best)
        baseline_energy = results[0]['metrics'].get('energy_joules', 0)
        best_energy = min(r['metrics'].get('energy_joules', float('inf')) for r in results)
        
        if baseline_energy > 0:
            improvement = ((baseline_energy - best_energy) / baseline_energy) * 100
            exp_names.append(exp['name'])
            improvements.append(improvement)
    
    colors = ['green' if i > 0 else 'red' for i in improvements]
    bars = ax.barh(exp_names, improvements, color=colors, alpha=0.7)
    ax.set_xlabel('Energy Improvement (%)', fontsize=12)
    ax.set_title('Energy Improvement Across All Experiments', fontsize=14, fontweight='bold')
    ax.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
    ax.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, improvements)):
        ax.text(float(val) + 1, i, f'{val:.1f}%', va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'energy_improvements.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Success Rate Comparison
    fig, ax = plt.subplots(figsize=(14, 8))
    
    exp_names = []
    success_rates = []
    
    for exp in all_experiments:
        if exp['stats']:
            exp_names.append(exp['name'])
            rate = exp['stats'].get('success_rate', 0)
            # Handle both numeric and string values
            if isinstance(rate, str):
                rate = float(rate.rstrip('%'))
            success_rates.append(float(rate))
    
    bars = ax.barh(exp_names, success_rates, color='steelblue', alpha=0.7)
    ax.set_xlabel('Success Rate (%)', fontsize=12)
    ax.set_title('Mutation Success Rate Across Experiments', fontsize=14, fontweight='bold')
    ax.set_xlim(0, 100)
    ax.grid(axis='x', alpha=0.3)
    
    for i, (bar, val) in enumerate(zip(bars, success_rates)):
        ax.text(val + 1, i, f'{val:.1f}%', va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'success_rates.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Pareto Front Size Comparison
    fig, ax = plt.subplots(figsize=(14, 8))
    
    exp_names = []
    pareto_sizes = []
    
    for exp in all_experiments:
        if exp['results']:
            exp_names.append(exp['name'])
            pareto_sizes.append(len(exp['results']))
    
    bars = ax.barh(exp_names, pareto_sizes, color='coral', alpha=0.7)
    ax.set_xlabel('Number of Pareto-Optimal Solutions', fontsize=12)
    ax.set_title('Pareto Front Size Across Experiments', fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    
    for i, (bar, val) in enumerate(zip(bars, pareto_sizes)):
        ax.text(float(val) + 0.5, i, str(val), va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'pareto_sizes.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4. Energy vs Time Scatter (all experiments combined)
    fig, ax = plt.subplots(figsize=(12, 8))
    
    for exp in all_experiments:
        if not exp['results']:
            continue
        
        energies = [r['metrics'].get('energy_joules', 0) for r in exp['results']]
        times = [r['metrics'].get('duration_seconds', 0) for r in exp['results']]
        
        ax.scatter(times, energies, alpha=0.6, s=100, label=exp['name'])
    
    ax.set_xlabel('Execution Time (seconds)', fontsize=12)
    ax.set_ylabel('Energy Consumption (Joules)', fontsize=12)
    ax.set_title('Energy vs Time - All Experiments', fontsize=14, fontweight='bold')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'energy_vs_time_all.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Generated 4 comparison charts in {output_dir}")

def generate_html_report(all_experiments, output_dir, suite_dir):
    """Generate comprehensive HTML report."""
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>HEDGE Comprehensive Experiment Report</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }
        h1 {
            color: #667eea;
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            font-size: 1.2em;
            margin-bottom: 40px;
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }
        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
        }
        .chart {
            margin: 30px 0;
            text-align: center;
        }
        .chart img {
            max-width: 100%;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .experiment-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin-top: 40px;
        }
        .experiment-card {
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            background: #f9f9f9;
        }
        .experiment-card h3 {
            color: #667eea;
            margin-top: 0;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #e0e0e0;
        }
        .metric:last-child {
            border-bottom: none;
        }
        .metric-label {
            font-weight: 600;
            color: #555;
        }
        .metric-value {
            color: #667eea;
            font-weight: bold;
        }
        .improvement-positive {
            color: #10b981;
        }
        .improvement-negative {
            color: #ef4444;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 HEDGE Comprehensive Experiment Report</h1>
        <div class="subtitle">Exhaustive Code Optimization Analysis</div>
"""
    
    # Calculate summary statistics
    total_experiments = len(all_experiments)
    total_solutions = sum(len(exp['results']) for exp in all_experiments if exp['results'])
    
    avg_improvement = 0
    improvement_count = 0
    for exp in all_experiments:
        if exp['results'] and len(exp['results']) >= 2:
            baseline = exp['results'][0]['metrics'].get('energy_joules', 0)
            best = min(r['metrics'].get('energy_joules', float('inf')) for r in exp['results'])
            if baseline > 0:
                avg_improvement += ((baseline - best) / baseline) * 100
                improvement_count += 1
    
    if improvement_count > 0:
        avg_improvement /= improvement_count
    
    html += f"""
        <div class="summary">
            <div class="stat-card">
                <div class="stat-label">Total Experiments</div>
                <div class="stat-value">{total_experiments}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Pareto Solutions</div>
                <div class="stat-value">{total_solutions}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Energy Improvement</div>
                <div class="stat-value">{avg_improvement:.1f}%</div>
            </div>
        </div>
        
        <h2>📊 Comparison Charts</h2>
        
        <div class="chart">
            <h3>Energy Improvement Across Experiments</h3>
            <img src="energy_improvements.png" alt="Energy Improvements">
        </div>
        
        <div class="chart">
            <h3>Mutation Success Rates</h3>
            <img src="success_rates.png" alt="Success Rates">
        </div>
        
        <div class="chart">
            <h3>Pareto Front Sizes</h3>
            <img src="pareto_sizes.png" alt="Pareto Sizes">
        </div>
        
        <div class="chart">
            <h3>Energy vs Time - All Experiments</h3>
            <img src="energy_vs_time_all.png" alt="Energy vs Time">
        </div>
        
        <h2>📋 Individual Experiment Details</h2>
        <div class="experiment-grid">
"""
    
    # Add individual experiment cards
    for exp in all_experiments:
        if not exp['results']:
            continue
        
        results = exp['results']
        config = exp['config']
        stats = exp['stats']
        
        # Calculate metrics
        baseline_energy = results[0]['metrics'].get('energy_joules', 0)
        best_energy = min(r['metrics'].get('energy_joules', float('inf')) for r in results)
        improvement = 0
        if baseline_energy > 0:
            improvement = ((baseline_energy - best_energy) / baseline_energy) * 100
        
        improvement_class = 'improvement-positive' if improvement > 0 else 'improvement-negative'
        
        # Handle success_rate which might be string or numeric
        success_rate = stats.get('success_rate', 0)
        if isinstance(success_rate, str):
            success_rate = float(success_rate.rstrip('%'))
        else:
            success_rate = float(success_rate)
        
        html += f"""
            <div class="experiment-card">
                <h3>{exp['name']}</h3>
                <div class="metric">
                    <span class="metric-label">Optimization Level:</span>
                    <span class="metric-value">{config.get('level', 'N/A')}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Generations:</span>
                    <span class="metric-value">{config.get('generations', 'N/A')}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Pareto Solutions:</span>
                    <span class="metric-value">{len(results)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Energy Improvement:</span>
                    <span class="metric-value {improvement_class}">{improvement:.2f}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Success Rate:</span>
                    <span class="metric-value">{success_rate:.1f}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Best Energy:</span>
                    <span class="metric-value">{best_energy:.4f} J</span>
                </div>
            </div>
"""
    
    html += """
        </div>
    </div>
</body>
</html>
"""
    
    report_path = output_dir / 'comprehensive_report.html'
    with open(report_path, 'w') as f:
        f.write(html)
    
    print(f"✓ Generated HTML report: {report_path}")
    return report_path

def main():
    if len(sys.argv) < 2:
        print("Usage: python aggregate_results.py <comprehensive_experiment_dir>")
        return 1
    
    suite_dir = Path(sys.argv[1])
    if not suite_dir.exists():
        print(f"Error: Directory not found: {suite_dir}")
        return 1
    
    print(f"\nAggregating results from: {suite_dir}\n")
    
    # Load all experiment results
    all_experiments = []
    for exp_dir in sorted(suite_dir.iterdir()):
        if exp_dir.is_dir() and exp_dir.name != 'aggregated':
            print(f"Loading: {exp_dir.name}")
            exp_data = load_experiment_results(exp_dir)
            if exp_data:
                all_experiments.append(exp_data)
    
    if not all_experiments:
        print("No experiment results found!")
        return 1
    
    print(f"\nLoaded {len(all_experiments)} experiments\n")
    
    # Create aggregated output directory
    output_dir = suite_dir / 'aggregated'
    output_dir.mkdir(exist_ok=True)
    
    # Generate comparison charts
    print("Generating comparison charts...")
    create_comparison_charts(all_experiments, output_dir)
    
    # Generate HTML report
    print("Generating HTML report...")
    report_path = generate_html_report(all_experiments, output_dir, suite_dir)
    
    print(f"\n{'='*80}")
    print("AGGREGATION COMPLETE")
    print(f"{'='*80}")
    print(f"\nView comprehensive report:")
    print(f"  file://{report_path.absolute()}")
    print(f"\nAll visualizations saved to: {output_dir}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
from typing import List, Dict, Any
import numpy as np
from pathlib import Path

class ExperimentVisualizer:
    def __init__(self, experiment_dir: str):
        self.experiment_dir = experiment_dir
        self.viz_dir = os.path.join(experiment_dir, "visualizations")
        os.makedirs(self.viz_dir, exist_ok=True)
        
        # Set style
        sns.set_theme(style="whitegrid")
        plt.rcParams['figure.figsize'] = (10, 6)
        
    def load_evolution_data(self) -> List[Dict]:
        """Load evolution.jsonl data."""
        jsonl_path = os.path.join(self.experiment_dir, "evolution.jsonl")
        data = []
        if os.path.exists(jsonl_path):
            with open(jsonl_path, 'r') as f:
                for line in f:
                    data.append(json.loads(line))
        return data
    
    def load_pareto_results(self) -> List[Dict]:
        """Load pareto_results.json data."""
        json_path = os.path.join(self.experiment_dir, "pareto_results.json")
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                return json.load(f)
        return []
    
    def plot_pareto_frontier(self, pareto_data: List[Dict]):
        """Plot Pareto frontier: Energy vs Time."""
        if not pareto_data:
            return
            
        energies = [sol['metrics'].get('energy_joules', 0) for sol in pareto_data]
        times = [sol['metrics'].get('duration_seconds', 0) for sol in pareto_data]
        mutations = [sol['mutation'] for sol in pareto_data]
        
        plt.figure(figsize=(10, 6))
        scatter = plt.scatter(times, energies, c=range(len(pareto_data)), 
                            cmap='viridis', s=100, alpha=0.6, edgecolors='black')
        
        for i, (t, e, m) in enumerate(zip(times, energies, mutations)):
            plt.annotate(m, (t, e), xytext=(5, 5), textcoords='offset points', 
                        fontsize=8, alpha=0.7)
        
        plt.xlabel('Execution Time (seconds)', fontsize=12)
        plt.ylabel('Energy Consumption (Joules)', fontsize=12)
        plt.title('Pareto Frontier: Energy vs Time Trade-off', fontsize=14, fontweight='bold')
        plt.colorbar(scatter, label='Solution Index')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(self.viz_dir, 'pareto_frontier.png'), dpi=300)
        plt.close()
    
    def plot_convergence(self, evolution_data: List[Dict]):
        """Plot convergence: Best energy/time over generations."""
        if not evolution_data:
            return
            
        generations = []
        best_energies = []
        best_times = []
        
        current_best_energy = float('inf')
        current_best_time = float('inf')
        
        for entry in evolution_data:
            if entry.get('success', False):
                gen = entry.get('generation', 0)
                energy = entry['metrics'].get('energy_joules', float('inf'))
                time = entry['metrics'].get('duration_seconds', float('inf'))
                
                if energy < current_best_energy:
                    current_best_energy = energy
                if time < current_best_time:
                    current_best_time = time
                    
                generations.append(gen)
                best_energies.append(current_best_energy)
                best_times.append(current_best_time)
        
        if not generations:
            return
            
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        ax1.plot(generations, best_energies, marker='o', linewidth=2, markersize=6, color='green')
        ax1.set_xlabel('Generation', fontsize=11)
        ax1.set_ylabel('Best Energy (Joules)', fontsize=11, color='green')
        ax1.set_title('Convergence: Best Energy Over Generations', fontsize=13, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='y', labelcolor='green')
        
        ax2.plot(generations, best_times, marker='s', linewidth=2, markersize=6, color='blue')
        ax2.set_xlabel('Generation', fontsize=11)
        ax2.set_ylabel('Best Time (seconds)', fontsize=11, color='blue')
        ax2.set_title('Convergence: Best Time Over Generations', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='y', labelcolor='blue')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.viz_dir, 'convergence.png'), dpi=300)
        plt.close()
    
    def plot_mutation_distribution(self, evolution_data: List[Dict]):
        """Plot mutation strategy distribution and success rates."""
        if not evolution_data:
            return
            
        mutation_counts = {}
        mutation_successes = {}
        
        for entry in evolution_data:
            mut_type = entry.get('mutation_type', 'Unknown')
            success = entry.get('success', False)
            
            mutation_counts[mut_type] = mutation_counts.get(mut_type, 0) + 1
            if success:
                mutation_successes[mut_type] = mutation_successes.get(mut_type, 0) + 1
        
        mutations = list(mutation_counts.keys())
        counts = [mutation_counts[m] for m in mutations]
        successes = [mutation_successes.get(m, 0) for m in mutations]
        success_rates = [100 * s / c if c > 0 else 0 for s, c in zip(successes, counts)]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Mutation attempts
        ax1.bar(range(len(mutations)), counts, color='skyblue', edgecolor='black')
        ax1.set_xlabel('Mutation Strategy', fontsize=11)
        ax1.set_ylabel('Number of Attempts', fontsize=11)
        ax1.set_title('Mutation Strategy Distribution', fontsize=13, fontweight='bold')
        ax1.set_xticks(range(len(mutations)))
        ax1.set_xticklabels(mutations, rotation=45, ha='right')
        ax1.grid(axis='y', alpha=0.3)
        
        # Success rates
        colors = ['green' if sr > 50 else 'orange' if sr > 0 else 'red' for sr in success_rates]
        ax2.bar(range(len(mutations)), success_rates, color=colors, edgecolor='black')
        ax2.set_xlabel('Mutation Strategy', fontsize=11)
        ax2.set_ylabel('Success Rate (%)', fontsize=11)
        ax2.set_title('Mutation Success Rates', fontsize=13, fontweight='bold')
        ax2.set_xticks(range(len(mutations)))
        ax2.set_xticklabels(mutations, rotation=45, ha='right')
        ax2.grid(axis='y', alpha=0.3)
        ax2.set_ylim(0, 100)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.viz_dir, 'mutation_distribution.png'), dpi=300)
        plt.close()
    
    def plot_metrics_timeline(self, evolution_data: List[Dict]):
        """Plot all metrics over time."""
        if not evolution_data:
            return
            
        successful = [e for e in evolution_data if e.get('success', False)]
        if not successful:
            return
            
        generations = [e.get('generation', 0) for e in successful]
        energies = [e['metrics'].get('energy_joules', 0) for e in successful]
        times = [e['metrics'].get('duration_seconds', 0) for e in successful]
        
        fig, ax = plt.subplots(figsize=(14, 7))
        
        ax.scatter(generations, energies, label='Energy (Joules)', alpha=0.6, s=50, color='green')
        ax.scatter(generations, times, label='Time (seconds)', alpha=0.6, s=50, color='blue')
        
        ax.set_xlabel('Generation', fontsize=12)
        ax.set_ylabel('Metrics Value', fontsize=12)
        ax.set_title('All Metrics Timeline', fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(self.viz_dir, 'metrics_timeline.png'), dpi=300)
        plt.close()
    
    def plot_code_complexity_evolution(self, evolution_data: List[Dict]):
        """Plot code length evolution over generations."""
        if not evolution_data:
            return
            
        successful = [e for e in evolution_data if e.get('success', False) and 'code' in e]
        if not successful:
            return
            
        generations = [e.get('generation', 0) for e in successful]
        code_lengths = [len(e.get('code', '')) for e in successful]
        
        plt.figure(figsize=(12, 6))
        plt.scatter(generations, code_lengths, alpha=0.6, s=50, color='purple', edgecolors='black')
        plt.plot(generations, code_lengths, alpha=0.3, linewidth=1, color='purple')
        
        plt.xlabel('Generation', fontsize=12)
        plt.ylabel('Code Length (characters)', fontsize=12)
        plt.title('Code Complexity Evolution', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(self.viz_dir, 'code_complexity.png'), dpi=300)
        plt.close()
    
    def generate_summary_report(self, evolution_data: List[Dict], pareto_data: List[Dict]):
        """Generate a text summary report."""
        report_path = os.path.join(self.viz_dir, 'summary_report.txt')
        
        total_evaluations = len(evolution_data)
        successful_evals = len([e for e in evolution_data if e.get('success', False)])
        
        mutation_types = {}
        for e in evolution_data:
            mut = e.get('mutation_type', 'Unknown')
            mutation_types[mut] = mutation_types.get(mut, 0) + 1
        
        with open(report_path, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("HEDGE EXPERIMENT SUMMARY REPORT\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Total Evaluations: {total_evaluations}\n")
            f.write(f"Successful Evaluations: {successful_evals}\n")
            f.write(f"Success Rate: {100 * successful_evals / total_evaluations:.2f}%\n\n")
            
            f.write(f"Pareto-Optimal Solutions: {len(pareto_data)}\n\n")
            
            f.write("Mutation Strategy Usage:\n")
            for mut, count in sorted(mutation_types.items(), key=lambda x: x[1], reverse=True):
                f.write(f"  {mut}: {count}\n")
            
            if pareto_data:
                f.write("\n" + "=" * 60 + "\n")
                f.write("PARETO-OPTIMAL SOLUTIONS\n")
                f.write("=" * 60 + "\n")
                for i, sol in enumerate(pareto_data, 1):
                    f.write(f"\nSolution {i}:\n")
                    f.write(f"  Strategy: {sol['mutation']}\n")
                    f.write(f"  Energy: {sol['metrics'].get('energy_joules', 0):.4f} J\n")
                    f.write(f"  Time: {sol['metrics'].get('duration_seconds', 0):.4f} s\n")
                    f.write(f"  Code Length: {len(sol.get('code', ''))} chars\n")
    
    def generate_all_visualizations(self):
        """Generate all visualizations."""
        print(f"📊 Generating visualizations in {self.viz_dir}...")
        
        evolution_data = self.load_evolution_data()
        pareto_data = self.load_pareto_results()
        
        self.plot_pareto_frontier(pareto_data)
        print("  ✓ Pareto frontier plot")
        
        self.plot_convergence(evolution_data)
        print("  ✓ Convergence plots")
        
        self.plot_mutation_distribution(evolution_data)
        print("  ✓ Mutation distribution plots")
        
        self.plot_metrics_timeline(evolution_data)
        print("  ✓ Metrics timeline")
        
        self.plot_code_complexity_evolution(evolution_data)
        print("  ✓ Code complexity evolution")
        
        self.generate_summary_report(evolution_data, pareto_data)
        print("  ✓ Summary report")
        
        print(f"\n✅ All visualizations saved to: {self.viz_dir}")

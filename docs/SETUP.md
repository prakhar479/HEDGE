# HEDGE Setup Guide

This guide will help you get HEDGE up and running with the layered mutation system and LLM integration.

## Quick Start

### 1. Installation

```bash
# Clone the repository (if not already done)
git clone https://github.com/prakhar479/HEDGE.git
cd HEDGE

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Optional: Enhanced UI and visualizations
pip install rich matplotlib
```

### 2. API Key Configuration

HEDGE supports two LLM providers: **OpenAI** and **Google Gemini**.

#### Option A: Using OpenAI (GPT-4)

1. Get your API key from [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` and add your key:
   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

#### Option B: Using Google Gemini

1. Get your API key from [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
2. Create a `.env` file and add:
   ```
   GEMINI_API_KEY=your-actual-key-here
   ```

#### Option C: Demo Mode (No API Key)

If you don't provide any API key, HEDGE will use `MockLLMClient` which demonstrates the system with hardcoded transformations.

### 3. Running Examples

#### Example 1: Micro-Level Optimizations (No LLM Required)
```bash
python hedge.py optimize examples/target.py examples/test_target.py --level micro --generations 5
```

Expected outcome: Constant folding, dead code elimination, and basic micro-optimizations.

#### Example 2: Standard Layered Optimization
```bash
python hedge.py optimize examples/target.py examples/test_target.py --level standard --generations 5
```

Expected outcome: HEDGE will apply micro + syntactic + algorithmic optimizations, including O(n²) bubble sort → O(n log n) Timsort.

#### Example 3: Advanced Semantic Optimization (Requires LLM)
```bash
export GEMINI_API_KEY="your-api-key"
python hedge.py optimize examples/target_fib.py examples/test_target_fib.py --level advanced --generations 5
```

Expected outcome: HEDGE will optimize O(2ⁿ) recursive Fibonacci to O(n) iterative through semantic understanding.

#### Example 4: Custom Layer Selection
```bash
python hedge.py optimize examples/target_search.py examples/test_target_search.py --layers algorithmic,micro --generations 5
```

Expected outcome: Only algorithmic and micro-level optimizations applied.

#### Example 5: Legacy Mode
```bash
python hedge.py optimize examples/target.py examples/test_target.py --legacy-mode --level advanced --generations 5
```

Expected outcome: Uses the original mutator system for comparison.

## Understanding the Output

HEDGE will show you:

1. **Baseline Metrics**: Energy and time for original code
2. **Layer Statistics**: Mutations applied per layer (Semantic, Algorithmic, Syntactic, Micro)
3. **Generation Progress**: Evolution progress with layer-specific improvements
4. **Pareto Front**: Trade-offs between energy consumption and execution time
5. **Final Results**: Best solutions with layer contribution analysis

### Output Directories

```
experiments/run_TIMESTAMP/
├── config.json                    # Experiment configuration
├── pareto_results.json           # All Pareto-optimal solutions
├── statistics.json               # Layer and mutation statistics
├── visualizations/               # Charts and HTML report (if --visualize)
└── <target>_optimized.py        # Best solution (lowest energy)
```

## Advanced Usage

### Layer-Specific Optimization
```bash
# Only semantic and algorithmic layers
python hedge.py optimize your_code.py your_tests.py --layers semantic,algorithmic --generations 10

# Exclude specific mutators
python hedge.py optimize your_code.py your_tests.py --exclude-mutators "ConstantOptimizer,DeadCodeEliminator"

# Aggressive optimization with all layers
python hedge.py optimize your_code.py your_tests.py --level aggressive --generations 15 --visualize
```

### Monitoring Energy Consumption

HEDGE uses `codecarbon` to measure energy. For best results:
- Run on Linux or WSL
- Ensure you have hardware energy monitoring (Intel RAPL or similar)
- If energy monitoring isn't available, HEDGE will fall back to execution time

### Layer Performance Analysis
```bash
# Generate detailed visualizations
python hedge.py optimize your_code.py your_tests.py --level standard --visualize --verbose

# View layer contribution in HTML report
open experiments/run_TIMESTAMP/visualizations/report.html
```

## Troubleshooting

### "No module named 'src'"
Make sure you're running from the project root directory.

### "OPENAI_API_KEY not found"
Check that your `.env` file is in the project root and properly formatted.

### LLM produces invalid code
- The system will automatically skip invalid variants
- Try adjusting the temperature in `src/core/llm_client.py`
- Check the experiment logs to see what code was generated

### Energy monitoring not working
This is normal on some systems. HEDGE will fall back to execution time as the optimization metric.

## What's Next?

- Explore the `src/` directory to understand the architecture
- Read `docs/ARCHITECTURE.md` for implementation details
- Check the experiment logs to see how mutations performed
- Try optimizing your own code!

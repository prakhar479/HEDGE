# HEDGE Setup Guide

This guide will help you get HEDGE up and running with real LLM integration.

## Quick Start

### 1. Installation

```bash
# Clone the repository (if not already done)
git clone https://github.com/prakhar479/HEDGE.git
cd HEDGE

# Create and activate virtual environment
python3 -m venv .env
source .env/bin/activate  # On Windows: .env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
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

#### Example 1: Bubble Sort Optimization
```bash
python hedge.py optimize examples/target.py examples/test_target.py --generations 5
```

Expected outcome: HEDGE will optimize the O(n²) bubble sort to use Python's built-in `sorted()` (Timsort, O(n log n)).

#### Example 2: Fibonacci Optimization
```bash
python hedge.py optimize examples/target_fib.py examples/test_target_fib.py --generations 5
```

Expected outcome: HEDGE will optimize the O(2ⁿ) recursive Fibonacci to an O(n) iterative or memoized version.

#### Example 3: Search Optimization
```bash
python hedge.py optimize examples/target_search.py examples/test_target_search.py --generations 5
```

Expected outcome: HEDGE may suggest optimizations like using `enumerate()` or Python's built-in `list.index()`.

## Understanding the Output

HEDGE will show you:

1. **Baseline Metrics**: Energy and time for original code
2. **Generation Progress**: Each mutation attempt with its type (L1/L2)
3. **Improvements Found**: When a better variant is discovered
4. **Final Results**: Best code and comparative metrics

### Output Directories

- `experiments/<timestamp>/`: Contains detailed logs in JSONL format
- `examples/target_optimized.py`: Optimized version of your target code

## Advanced Usage

### Customizing Generations
```bash
python hedge.py optimize your_code.py your_tests.py --generations 10
```

### Monitoring Energy Consumption

HEDGE uses `codecarbon` to measure energy. For best results:
- Run on Linux or WSL
- Ensure you have hardware energy monitoring (Intel RAPL or similar)
- If energy monitoring isn't available, HEDGE will fall back to execution time

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

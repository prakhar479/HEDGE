#!/bin/bash
# Quick script to view HEDGE experiment results

echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                           ║"
echo "║              HEDGE EXPERIMENT RESULTS VIEWER                              ║"
echo "║                                                                           ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""

# Find the most recent comprehensive experiment
LATEST_DIR=$(ls -td experiments/comprehensive_* 2>/dev/null | head -1)

if [ -z "$LATEST_DIR" ]; then
    echo "❌ No comprehensive experiments found!"
    echo ""
    echo "Run: python run_comprehensive_experiments.py"
    exit 1
fi

echo "📁 Latest Experiment: $LATEST_DIR"
echo ""

# Check if aggregated report exists
REPORT="$LATEST_DIR/aggregated/comprehensive_report.html"

if [ -f "$REPORT" ]; then
    echo "✓ Aggregated report found!"
    echo ""
    echo "Opening comprehensive report in browser..."
    
    # Try different commands based on OS
    if command -v xdg-open &> /dev/null; then
        xdg-open "$REPORT"
    elif command -v open &> /dev/null; then
        open "$REPORT"
    elif command -v start &> /dev/null; then
        start "$REPORT"
    else
        echo ""
        echo "⚠️  Could not auto-open browser. Please manually open:"
        echo "   file://$(pwd)/$REPORT"
    fi
    
    echo ""
    echo "📊 Available visualizations:"
    echo "   • Energy improvements across experiments"
    echo "   • Mutation success rates"
    echo "   • Pareto front sizes"
    echo "   • Energy vs Time scatter plots"
    echo ""
    echo "📂 Individual experiment results:"
    ls -1 "$LATEST_DIR" | grep -v "aggregated\|suite_summary.json" | while read exp; do
        if [ -d "$LATEST_DIR/$exp" ]; then
            echo "   • $exp"
        fi
    done
    
else
    echo "⚠️  Aggregated report not found. Generating now..."
    echo ""
    python aggregate_results.py "$LATEST_DIR"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ Report generated successfully!"
        echo ""
        echo "Opening report..."
        
        if command -v xdg-open &> /dev/null; then
            xdg-open "$REPORT"
        elif command -v open &> /dev/null; then
            open "$REPORT"
        else
            echo "Please open: file://$(pwd)/$REPORT"
        fi
    else
        echo "❌ Failed to generate report. Check errors above."
        exit 1
    fi
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "📖 For more details, see:"
echo "   • EXPERIMENT_RESULTS_SUMMARY.md - Complete results summary"
echo "   • EXPERIMENT_GUIDE.md - Experiment setup guide"
echo ""
echo "🔍 To check experiment status:"
echo "   python check_experiment_status.py"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"

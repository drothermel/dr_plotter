# Phase 2 Agent Prompt: Faceted Plotting Example

## Your Mission
Create a working example that demonstrates faceted plotting using current dr_plotter capabilities. This example will produce a 2-row × N-column grid visualization and identify all friction points for Phase 3 library enhancements.

## Context
Phase 1 analysis shows perfect data structure for faceted plotting:
- 1,913 metrics available 
- 25 data recipes available
- 14 model sizes available (4M, 6M, 8M, 10M, 14M, 16M, 20M, 60M, 90M, 150M, 300M, 530M, 750M, 1B)
- 100% data density across all combinations
- Training steps range 0-69,369

## Target Visualization Specification

Create example at `examples/06_faceted_training_curves.py` with this exact specification:

**Grid Layout**: 2 rows × 4 columns
- **Row 1**: `pile_valppl` metric (perplexity, lower is better)
- **Row 2**: `mmlu_avg_correct_prob` metric (accuracy, higher is better)  
- **Columns**: These 4 data recipes in order: ["C4", "Dolma1.7", "FineWeb-Edu", "DCLM-Baseline"]

**Within Each Subplot**:
- **X-axis**: Training steps
- **Y-axis**: Metric value
- **Lines**: One line per model size, showing all 14 model sizes
- **Line styling**: Color/style differentiated by model size in logical order (4M → 1B)

## Required Script Structure

Create `examples/06_faceted_training_curves.py` with these functions:

```python
def load_and_prepare_data() -> pd.DataFrame:
    # Load data and do basic filtering/preparation
    
def create_model_size_ordering() -> List[str]:
    # Return model sizes in logical numeric order (4M, 6M, ..., 1B)
    
def subset_data_for_plotting(df: pd.DataFrame) -> pd.DataFrame:
    # Filter to target metrics and data recipes
    
def create_faceted_grid() -> tuple[plt.Figure, Any]:  # or appropriate return type
    # Create the 2x4 subplot grid using dr_plotter
    
def plot_training_curves(df: pd.DataFrame) -> None:
    # Main plotting logic - produce the complete visualization
    
def main() -> None:
    # Orchestrate all functions
```

## Code Requirements

**CRITICAL - Follow Project Standards**:
1. **No comments or docstrings anywhere** - code must be self-documenting  
2. **Comprehensive type hints** on ALL functions (parameters and return values)
3. **All imports at the very top** of the file
4. **Use assertions for validation**: `assert condition, "message"` instead of exceptions
5. **Remove any existing comments** when editing files

**Import Requirements**:
```python
from typing import Any, Dict, List, Tuple
import pandas as pd
import matplotlib.pyplot as plt
from dr_plotter import [import what you need from existing dr_plotter]
# Add other imports as needed
```

## Data Preparation Requirements

1. **Model Size Ordering**: Convert alphabetic sorting (10M, 14M, 150M...) to numeric (4M, 6M, 8M, 10M, 14M, 16M, 20M, 60M, 90M, 150M, 300M, 530M, 750M, 1B)

2. **Data Filtering**: 
   - Target metrics: `pile_valppl`, `mmlu_avg_correct_prob`
   - Target recipes: ["C4", "Dolma1.7", "FineWeb-Edu", "DCLM-Baseline"]  
   - Handle null values appropriately

3. **Data Structure**: Organize data for efficient plotting across the grid

## Current dr_plotter Investigation Required

**BEFORE implementing plotting logic**:
1. **Explore existing dr_plotter classes** - understand BasePlotter, StyleApplicator, legend system
2. **Identify current subplot capabilities** - how to create 2×4 grids
3. **Understand styling system** - how to map model sizes to colors/styles consistently
4. **Check legend management** - how to create unified legend across subplots

**Research these files**:
- Look at existing examples in `examples/` for patterns
- Examine `src/dr_plotter/` structure for subplot and styling capabilities
- Check how existing plotters handle multiple series within subplots

## Documentation Requirements

In your implementation, create clear evidence of:

1. **Configuration complexity** - How much setup is needed?
2. **Repetitive patterns** - What code gets repeated across subplots?
3. **Styling friction** - How hard is consistent styling across subplots?
4. **Legend management** - How complex is unified legend handling?
5. **Data preparation friction** - What data manipulation is needed?

## Success Criteria

**Functional Requirements**:
- ✅ Produces publication-ready 2×4 grid visualization  
- ✅ Correct metrics in correct rows (pile_valppl top, mmlu_avg_correct_prob bottom)
- ✅ Data recipes in correct column order
- ✅ All 14 model sizes plotted as different lines in each subplot
- ✅ Consistent styling across all subplots
- ✅ Clear, readable legend
- ✅ Proper axis labels and formatting

**Strategic Requirements**:
- ✅ Clear identification of repetitive code patterns
- ✅ Documentation of configuration complexity  
- ✅ List of friction points that should be abstracted
- ✅ Working foundation for Phase 3 enhancements

## Testing
Before submitting:
1. Run the script - ensure it produces the visualization
2. Verify all 8 subplots are correctly configured
3. Check that model size ordering is logical (4M → 1B)
4. Confirm legend is clear and consistent
5. Validate no errors or warnings

## Output Format
When complete, provide:
1. **Working script** that produces target visualization
2. **List of friction points** discovered during implementation  
3. **Configuration complexity assessment** - how much setup was required?
4. **Recommendations** for what should be abstracted in Phase 3

This example will serve as the foundation for designing Phase 3 library enhancements.
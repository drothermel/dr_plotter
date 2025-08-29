# Phase 2 Friction Analysis: Faceted Plotting Implementation

## Overview

Phase 2 successfully created `examples/06_faceted_training_curves.py` that produces a publication-ready 2×4 grid visualization demonstrating current dr_plotter capabilities and identifying friction points for Phase 3 library enhancements.

## Target Visualization Achieved ✅

- **Grid Layout**: 2 rows × 4 columns
- **Row 1**: `pile-valppl` (perplexity, lower is better)  
- **Row 2**: `mmlu_average_correct_prob` (accuracy, higher is better)
- **Columns**: C4, Dolma1.7, FineWeb-Edu, DCLM-Baseline
- **Lines**: All 14 model sizes (4M → 1B) with consistent styling across subplots

## Friction Points Discovered

### Configuration Complexity 🔴 **HIGH PRIORITY**

1. **Manual subplot iteration** 
   - Must loop through each (row, col) position individually
   - No built-in faceting abstraction for row_by/col_by operations
   - Current approach: 8 separate fm.plot() calls with manual coordinate management

2. **Repetitive axis labeling**
   - Each subplot requires manual xlabel/ylabel configuration  
   - Conditional logic needed to avoid duplicate labels
   - No automatic label inference from metric names or faceting dimensions

3. **Legend management complexity** ~~RESOLVED~~
   - ✅ **SOLUTION FOUND**: `legend_strategy="figure_below"` creates unified legend across all subplots
   - ✅ **Updated implementation** uses single shared legend with proper spacing
   - ~~Each subplot creates its own legend independently~~ **FIXED**

4. **Manual grid/formatting per subplot**
   - Each subplot needs individual grid, tick formatting
   - Scientific notation, styling applied subplot-by-subplot
   - No theme propagation across faceted layouts

### Repetitive Code Patterns 🟡 **MEDIUM PRIORITY**

1. **Nested loops for grid setup**
   - Same fm.plot() call structure repeated 8 times
   - Only coordinates change between iterations
   - Pattern suggests need for higher-level abstraction

2. **Duplicate styling configuration**
   - linewidth, alpha, grid settings repeated per subplot
   - No centralized styling that propagates across facets
   - Theme consistency requires manual maintenance

3. **Manual data filtering per subplot**
   - Same subset logic needed for each subplot position
   - Data preparation repeated rather than abstracted
   - No built-in data routing for faceted layouts

4. **Axis configuration repetition**
   - xlabel/ylabel logic repeated with conditional branching
   - Manual handling of shared vs. individual axis labels
   - Edge case logic for first column, bottom row positioning

### Data Preparation Friction 🟡 **MEDIUM PRIORITY**

1. **Model size ordering complexity**
   - Manual conversion from alphabetic ("10M", "1B") to numeric ordering required
   - No built-in parameter size parsing utilities
   - Custom categorical ordering logic needed

2. **Multi-metric handling**
   - Separate data filtering and subplot assignment for each metric
   - No streamlined multi-y-column faceted plotting
   - Manual metric-to-row mapping required

3. **Missing data handling**
   - Manual dropna() calls scattered throughout the process
   - No centralized missing data strategy for faceted plots
   - Inconsistent handling across different subplots

### Styling Consistency Challenges 🟡 **MEDIUM PRIORITY**

1. **No automatic color coordination**
   - Each subplot handles hue mapping independently  
   - Color palette consistency requires manual verification
   - No guarantee of consistent model size → color mapping

2. **Legend coordination complexity** ~~RESOLVED~~
   - ✅ **SOLUTION FOUND**: `legend_strategy="figure_below"` provides built-in unified legend
   - ✅ **Available options**: "figure_below", "split", "per_axes", "none" 
   - ~~Manual positioning and styling coordination required~~ **BUILT-IN SUPPORT**

3. **Manual formatting application**
   - Scientific notation, grid styling applied per subplot
   - No automatic format inference based on data ranges
   - Theme settings don't propagate to faceted layouts

## Current Implementation Statistics

- **Lines of Code**: ~70 lines for faceted plotting configuration
- **Manual Repetition**: 8 identical fm.plot() calls with only coordinates varying  
- **Configuration Complexity**: ~~15+ separate styling/formatting decisions~~ → **5+ decisions after discovering existing features**
- **Data Preparation**: 3 separate filtering/transformation steps required

## Implementation Quality Achieved ✅

- ✅ **Unified Legend**: Single shared legend across all 8 subplots
- ✅ **Shared Y-Axes**: Same scale within rows for easy comparison
- ✅ **Professional Spacing**: Proper margins and legend positioning
- ✅ **Clean Axis Labels**: Only where needed (bottom row, left column)
- ✅ **Consistent Styling**: Color mapping preserved across all subplots
- ✅ **Optimal Data Usage**: Per-metric NaN filtering recovers 29% more data points (1,396 vs 1,081 rows)

## Recommendations for Phase 3 Abstractions

### High Priority Abstractions 🔴

1. **FacetGrid Class**
   - Automate subplot creation with `row_by="metric"` and `col_by="data_recipe"` parameters
   - Handle data routing automatically to appropriate subplot positions
   - Target: Reduce 8 fm.plot() calls to 1 faceted plot call

2. **Automatic Axis Labeling**
   - Smart defaults based on metric names and faceting dimensions
   - Shared axis labels for rows/columns with proper positioning
   - Eliminate conditional xlabel/ylabel logic

### ~~Medium~~ → **High Priority** (Multiple Systems Already Solved ✅)

3. **~~Unified Legend System~~** ✅ **AVAILABLE NOW**
   - ✅ `legend_strategy="figure_below"` provides single legend across all subplots
   - ✅ Multiple positioning options: "figure_below", "split", "per_axes", "none"
   - ✅ Built-in legend coordination with proper spacing controls

4. **~~Shared Axis System~~** ✅ **AVAILABLE NOW**
   - ✅ `sharey="row"` parameter passes through to matplotlib's plt.subplots()
   - ✅ Automatic y-axis sharing within rows (same scale for same metrics)
   - ✅ Reduces visual comparison friction across data recipes

5. **~~Subplot Spacing Controls~~** ✅ **AVAILABLE NOW**
   - ✅ `plot_margin_bottom`, `legend_y_offset` for legend positioning
   - ✅ `layout_pad` for general subplot spacing
   - ✅ Proper accommodation for figure-level legends

### Medium Priority Enhancements 🟡

1. **Model Size Ordering Utilities**
   - Built-in numeric parameter sorting ("4M" → "1B" ordering)
   - Automatic detection and parsing of size suffixes (K, M, B)
   - Custom ordering support for non-standard parameter formats

2. **Multi-Metric Plotting Helpers**
   - Streamlined handling of multiple y-columns across facets
   - Automatic metric-to-row assignment
   - Built-in missing data handling strategies

3. **Consistent Styling Propagation**
   - Theme settings that automatically apply across all subplots
   - Centralized styling configuration for faceted layouts
   - Automatic format inference (scientific notation, grid styles)

### Target Phase 3 API

```python
# Current Phase 2 approach: ~70 lines
with FigureManager(rows=2, cols=4) as fm:
    for col_idx, recipe in enumerate(target_recipes):
        for row_idx, metric in enumerate(metrics):
            # Manual subplot configuration...
            
# Proposed Phase 3 approach: ~10 lines  
fm.facet_plot(
    "line",
    data=df,
    x="step", 
    y=["pile-valppl", "mmlu_average_correct_prob"],
    row_by="metric",
    col_by="data", 
    hue_by="params",
    col_order=["C4", "Dolma1.7", "FineWeb-Edu", "DCLM-Baseline"]
)
```

## Success Criteria Achieved ✅

### Functional Requirements
- ✅ Publication-ready 2×4 grid visualization produced
- ✅ Correct metrics in correct rows (pile_valppl top, mmlu_average_correct_prob bottom)
- ✅ Data recipes in specified column order
- ✅ All 14 model sizes plotted as different lines in each subplot
- ✅ Consistent styling across all subplots
- ✅ Clear, readable output with proper axis labels and formatting

### Strategic Requirements  
- ✅ Clear identification of 15+ friction points requiring abstraction
- ✅ Documented configuration complexity assessment
- ✅ Quantified repetitive code patterns (8x identical subplot calls)
- ✅ Working foundation established for Phase 3 enhancement design

## Advanced Controls Implementation ✅ **NEW**

### Successfully Implemented Features

Following Phase 2 completion, we added comprehensive filtering, ordering, and axis control capabilities to both examples:

1. **Model Size Filtering & Ordering**
   ```bash
   --model-sizes 150M 300M 1B  # Select and order model sizes  
   ```
   - ✅ Custom ordering preserves user-specified sequence
   - ✅ Automatic categorical conversion maintains consistent line styling
   - ✅ Dynamic legend sizing based on filtered model count

2. **Data Recipe Filtering & Ordering**
   ```bash
   --recipes C4 Dolma1.7  # Select and order data recipes
   ```
   - ✅ Ordering controls subplot column arrangement
   - ✅ Dynamic grid width adjustment (3.5 * num_recipes)
   - ✅ Automatic figure sizing based on recipe count

3. **Axis Scaling Controls**
   ```bash
   --x-log --y-log  # Independent axis log scaling
   ```
   - ✅ Per-axis logarithmic scaling support
   - ✅ Automatic scientific notation for linear axes
   - ✅ Theme integration stores scaling preferences

4. **Axis Range Limiting**
   ```bash
   --xlim 5000 50000 --ylim 0.1 10  # Custom axis ranges
   ```
   - ✅ Independent X and Y axis range control
   - ✅ Applied uniformly across all subplots in faceted grid
   - ✅ Works with both linear and logarithmic scaling

### Implementation Quality Assessment

**Ease of Addition**: ⭐⭐⭐⭐ (4/5)
- Adding filtering was straightforward using pandas categorical ordering
- dr_plotter's parameter passing worked seamlessly for axis limits
- Grid resizing integrated naturally with FigureManager
- Both regular and themed versions updated without major refactoring

**User Experience**: ⭐⭐⭐⭐⭐ (5/5)
- Intuitive command-line interface matching common plotting tools
- Order specification directly translates to visual arrangement
- Sensible defaults allow incremental customization
- Immediate feedback on data filtering results

### Friction Points Discovered During Advanced Controls

#### Low Priority Issues 🟢

1. **Pandas FutureWarning Noise**
   - Multiple `observed=False` deprecation warnings during categorical grouping
   - Originates from dr_plotter's base plotting layer
   - Does not affect functionality but clutters output
   - **Recommendation**: Update dr_plotter to specify `observed=True` in groupby operations

2. **Dynamic Grid Sizing Calculation**
   - Current manual calculation: `figwidth = max(12, num_recipes * 3.5)`
   - Works well but requires user-space logic
   - **Minor Enhancement**: Could be abstracted into FigureManager automatic sizing

#### Successfully Avoided Friction

1. **Data Consistency Across Filters** ✅
   - Per-metric NaN filtering ensures no data loss across different recipe/model combinations
   - Categorical ordering maintains consistent styling regardless of filter subset
   - All combinations tested successfully (1 recipe + 1 model → all recipes + all models)

2. **Theme System Integration** ✅
   - Axis scaling preferences properly stored and applied in themed version
   - Manual theme application pattern from earlier investigation worked seamlessly
   - No conflicts between filtering parameters and theme configuration

3. **Parameter Validation** ✅
   - Automatic assertion-based validation for missing recipes/models
   - Clear error messages when filtered combinations have no data
   - Robust handling of edge cases (single recipe, single model size)

### Advanced Controls Success Metrics

**Filtering Effectiveness**:
- ✅ All combinations work: 1×1 grid (30 rows) → 4×14 grid (1,396 rows)
- ✅ Order preservation: User-specified sequence matches subplot arrangement
- ✅ Data integrity: No unexpected data loss during filtering operations

**Implementation Completeness**:
- ✅ Both regular and themed versions feature-complete
- ✅ Full CLI argument support with help documentation
- ✅ Backward compatibility: Default arguments produce original behavior

**Code Quality**:
- ✅ <50 lines of additional code per example for complete filtering system
- ✅ No code duplication between regular and themed implementations
- ✅ Clear separation between filtering logic and plotting logic

## Next Steps for Phase 3

1. **Design FacetGrid API** - Create intuitive row_by/col_by interface
2. **Implement unified legend system** - Single legend spanning subplot grid  
3. **Build automatic axis labeling** - Smart defaults with manual override capability
4. **Create parameter ordering utilities** - Handle common ML parameter size formats
5. **Develop styling propagation** - Theme consistency across faceted layouts
6. **Address pandas warning noise** - Update groupby operations to specify `observed=True`

The Phase 2 implementation with advanced controls provides a comprehensive baseline demonstrating that current dr_plotter capabilities can produce highly flexible faceted visualizations. The filtering/ordering implementation revealed that most advanced control features integrate smoothly with existing architecture, while clearly identifying where abstractions would eliminate the most friction for researchers creating similar faceted plots.
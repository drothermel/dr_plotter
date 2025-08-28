# Faceted Plotting: Comprehensive Design & Implementation Plan

## Project Overview

**Objective**: Transform complex multi-dimensional data visualization from brittle one-off solutions to reusable, intuitive patterns through native faceting support in dr_plotter.

**Current Status**: 
- ✅ Phase 1: Data analysis complete
- ✅ Phase 2: Working examples implemented
- ❌ Phase 3: API design (pending)
- ❌ Phase 4: Native implementation (pending)

**Strategic Goal**: Enable researchers to create publication-ready faceted visualizations with minimal boilerplate while maintaining fine-grained control when needed.

## Target Use Case: Multi-Dimensional ML Training Visualization

**Current Working Example**: 2×4 grid showing training curves across:
- **Rows**: Different metrics (pile-valppl, mmlu_average_correct_prob) 
- **Columns**: Different data recipes (C4, Dolma1.7, FineWeb-Edu, DCLM-Baseline)
- **Lines within each subplot**: Different model sizes (4M, 6M, 8M, 10M, 14M, etc.)

## Evidence-Based Findings

### Data Structure Insights
- **Perfect data density**: 100% coverage across 350 model_size × data_recipe combinations
- **Training progression**: 6-54 steps per combination, varied training lengths normal
- **Metric scale**: 1,913 total metrics provides rich subset selection options
- **Model size ordering**: Alphabetic sorting (10M, 14M, 150M) vs logical numeric ordering requires explicit handling

### Current Boilerplate Analysis

Users currently need **95+ lines** for faceted plots, broken down as:

1. **Data Preparation** (20+ lines):
   ```python
   # Filter DataFrame for target metrics/recipes/model sizes
   filtered_df = df[df["data"].isin(target_recipes) & df["params"].isin(model_sizes)].copy()
   # Set up categorical ordering for consistent plotting
   filtered_df["params"] = pd.Categorical(filtered_df["params"], categories=model_sizes, ordered=True)
   ```

2. **Manual Subplot Iteration** (30+ lines):
   ```python
   for col_idx, recipe in enumerate(target_recipes):
       recipe_data = df[df["data"] == recipe].copy()
       for row_idx, (metric, metric_label) in enumerate(zip(metrics, metric_labels)):
           fm.plot("line", row_idx, col_idx, metric_data, x="step", y=metric, hue_by="params")
           # Manual axis configuration per subplot
   ```

3. **Styling Coordination** (15+ lines):
   - Consistent colors/markers across subplots for same model size
   - Proper axis labels only on edges
   - Legend configuration for multi-dimensional data

4. **Theme Management** (themed variant adds 50+ lines):
   - Custom theme creation with color cycles
   - Scale coordination across subplots

### Key Friction Points Identified

1. **Repetitive subplot iteration**: Manual loops for each metric × recipe combination
2. **Styling consistency**: Ensuring the same model size gets same color/marker across all subplots  
3. **Label coordination**: Managing axis labels, titles, and legend across grid
4. **Data preparation**: Converting multi-dimensional data to per-subplot format
5. **Performance consideration**: 14 lines per subplot × 8 subplots = 112 total line objects to manage

## Architectural Insights from Implementation

### Natural Scope Boundaries
- **dr_plotter responsibility**: Generic plotting infrastructure (grids, styling coordination, legend management)
- **User code responsibility**: Domain-specific logic (data selection, metric interpretation, data preparation)

### Complexity Source
Multi-dimensional data visualization complexity comes from **coordination across dimensions**, not individual subplot complexity.

### Design Patterns Discovered
1. **Grid Layout Management**: Systematic separation of data preparation, grid creation, styling coordination
2. **Multi-Dimensional Styling**: Color/marker consistency across subplots requires centralized coordination
3. **Legend Strategy**: Multi-dimensional legends need careful positioning and grouping strategies

## Phase 3: API Design Requirements

**Complete Requirements Specification**: See [`docs/plans/faceted_plotting_requirements.md`](./faceted_plotting_requirements.md) for the comprehensive requirements document.

### Core Design Questions Identified

1. **Scope Boundary**: Natural division between subplot grids/styling vs. data prep/metric selection
2. **Configuration Pattern**: Row/column semantic mapping feels intuitive for multi-dimensional data
3. **Data Integration**: 100% data density creates opportunities for streamlined API design
4. **Styling Control**: Cross-subplot consistency is complex but automatable
5. **Ordering and Filtering**: Dual-purpose `*_order` parameters solve styling inconsistencies
6. **Layout Flexibility**: Support both explicit grids and wrapped single-dimension layouts
7. **Layered Faceting**: Multiple composable calls enable sophisticated visualizations
8. **Selective Application**: Target-specific parameters enable precise subplot control

### API Design Summary

**Complete API Examples**: See [`docs/plans/faceted_plotting_requirements.md`](./faceted_plotting_requirements.md) for detailed API specifications and examples.

**Core Vision**: Transform 95+ lines of manual subplot management into intuitive, composable API calls:

```python
# Simple case: Full grid with automatic layout
fm.plot_faceted(
    data=df, plot_type="line",
    rows="metric", cols="data_recipe", lines="model_size",
    x="step", y="value"
)

# Advanced case: Layered plots with selective targeting
fm.plot_faceted(data=base_data, plot_type="scatter", ...)
fm.plot_faceted(data=trend_data, plot_type="line", target_row=0, ...)
```

### API Design Deliverables (Phase 3)

**Reference**: Complete deliverable specifications in [`docs/plans/faceted_plotting_requirements.md`](./faceted_plotting_requirements.md)

**Summary**:
1. **Core API specification** with `plot_faceted()` method signatures  
2. **Layout systems** for grids, wrapping, and selective targeting
3. **Styling coordination** maintaining consistency across subplots
4. **Data integration** with pandas DataFrame multi-dimensional handling
5. **Backwards compatibility** preserving all existing functionality

## Phase 4: Implementation Strategy

### Implementation Deliverables

**Reference**: Complete implementation requirements in [`docs/plans/faceted_plotting_requirements.md`](./faceted_plotting_requirements.md)

**Summary**:
1. **Enhanced FigureManager** with native faceting capabilities
2. **Configuration and coordination systems** for complex subplot management
3. **Refactored examples** demonstrating API simplification and new capabilities
4. **Comprehensive validation** ensuring quality and performance standards

### Success Criteria

- **Boilerplate reduction**: New API reduces example code by 60%+ lines
- **Functionality preservation**: All existing dr_plotter capabilities remain unchanged
- **Intuitive usage**: API feels natural for multi-dimensional visualization tasks
- **Performance maintenance**: No significant performance degradation for complex plots

## Key Technical Discoveries

### Model Size Ordering Challenge
- **Issue**: Alphabetic sorting (10M, 14M, 150M) vs logical numeric ordering (4M, 6M, 8M, 10M...)
- **Impact**: Affects line styling consistency and legend ordering
- **Solution**: API must provide explicit ordering control via `*_order` parameters (also serves as filtering)

### Metric Name Patterns
- **Discovery**: Actual metric names use underscores (pile_valppl) not hyphens (pile-valppl)
- **Impact**: API design must handle real-world naming conventions

### Theme Integration Complexity
- **Discovery**: Custom themes for faceted plots require 50+ additional lines
- **Opportunity**: Native faceting API could integrate theme management automatically

## Reusable Methodology

### Evidence-First Library Enhancement Pattern
1. **Phase 1**: Systematic data structure analysis
2. **Phase 2**: Working example implementation with current tools
3. **Phase 3**: API design based on friction point evidence  
4. **Phase 4**: Native implementation and validation

**Success Criteria**: Each phase provides concrete evidence for next phase design decisions.

### Multi-Dimensional Visualization Decomposition Pattern
1. **Data preparation**: Filter and structure multi-dimensional data
2. **Grid creation**: Establish subplot layout and coordination
3. **Styling coordination**: Ensure consistency across dimensions
4. **Legend management**: Handle multi-dimensional legend strategies

## Working Examples Status

### Current Implementation Files
- **`examples/06_faceted_training_curves.py`**: Main faceted plotting example (95+ lines)
- **`examples/06b_faceted_training_curves_themed.py`**: Themed variant (145+ lines)
- **`examples/plots/06_faceted_training_curves.png`**: Generated visualization
- **`examples/plots/06b_faceted_training_curves_themed.png`**: Themed visualization

### Integration Status
- **DataDecide integration**: Working with `uv add "dr_plotter[datadec]"`
- **CLI argument validation**: Complete with proper error handling
- **Theme system integration**: Demonstrated in themed variant

## Next Steps

### Immediate Phase 3 Tasks
1. **API specification design**: Define exact method signatures and parameters
2. **Configuration class design**: Create faceting configuration objects
3. **Data transformation design**: Define interface between user data and plotting system
4. **Styling coordination design**: Specify cross-subplot consistency mechanisms

### Phase 4 Implementation Tasks  
1. **Core faceting implementation**: Add `plot_faceted()` method to FigureManager
2. **Configuration system**: Implement faceting configuration classes
3. **Data utilities**: Build transformation functions for multi-dimensional data
4. **Example refactoring**: Convert current examples to use new API
5. **Testing and validation**: Comprehensive testing of new functionality

## Strategic Value

**Immediate**: Working visualization that meets complex multi-dimensional requirements
**Strategic**: Reusable patterns that handle entire classes of similar problems  
**Long-term**: Enhanced dr_plotter that makes complex visualizations significantly easier

**Key Architectural Insight**: Multi-dimensional visualization coordination patterns are applicable beyond ML evaluation data to scientific plotting generally.
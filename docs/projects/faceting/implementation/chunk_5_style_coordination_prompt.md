# Faceted Plotting Implementation: Chunk 5 - Style Coordination System

## Project Context

You are implementing **Chunk 5** - Style Coordination System, the most complex remaining chunk for dr_plotter's native faceting support.

**Your role**: Implement figure-level styling consistency and coordination across subplots for layered faceting scenarios.

**Foundation**: Chunks 1-4 completed successfully with working advanced layout features (83/83 faceting tests passing, 46/46 module tests passing) and comprehensive architecture.

## Key References

**MANDATORY**: Before starting, read these docs:
- `docs/DESIGN_PHILOSOPHY.md` - Core principles and coding standards
- `docs/plans/faceted_plotting_detailed_design.md` - Complete technical architecture 
- `docs/plans/faceted_plotting_implementation_plan.md` - Previous chunk implementation notes and patterns
- `docs/plans/context_restoration_guide_faceted_plotting.md` - Current capabilities and scope

## Problem Statement

**Current Issue**: Each `plot_faceted()` call creates independent styling, leading to inconsistent colors/markers across subplots and layers.

**Example Problem**:
```python
# Layer 1: Scatter plots
fm.plot_faceted(data=scatter_data, plot_type="scatter", 
               rows="metric", cols="recipe", lines="model_size", 
               x="step", y="value", alpha=0.6)
               
# Layer 2: Trend lines 
fm.plot_faceted(data=trend_data, plot_type="line",
               rows="metric", cols="recipe", lines="model_size",
               target_row=0, x="step", y="trend", linewidth=2)

# PROBLEM: "7B" model might be blue in scatter layer but red in line layer
```

**Required Solution**: Same `lines` dimension values must get identical colors/markers across all subplots and all layers within a single FigureManager instance.

## Your Tasks

### Task 1: Design FacetStyleCoordinator Class

**Problem**: Need centralized style management that persists across multiple `plot_faceted()` calls.

**File**: `src/dr_plotter/faceting/style_coordination.py` (create new)

**Implementation**:

```python
from typing import Any, Dict, List, Optional, Set, Tuple
import pandas as pd
from dr_plotter.faceting_config import FacetingConfig


class FacetStyleCoordinator:
    def __init__(self) -> None:
        self._dimension_values: Dict[str, Set[str]] = {}
        self._style_assignments: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self._cycle_positions: Dict[str, int] = {}
    
    def register_dimension_values(self, dimension: str, values: List[str]) -> None:
        """Register all possible values for a dimension across all plotting calls."""
        if dimension not in self._dimension_values:
            self._dimension_values[dimension] = set()
        self._dimension_values[dimension].update(values)
        
        # Ensure stable ordering for consistent style assignment
        ordered_values = sorted(self._dimension_values[dimension], key=str)
        if dimension not in self._style_assignments:
            self._style_assignments[dimension] = {}
            self._cycle_positions[dimension] = 0
        
        # Assign styles to new values
        self._assign_styles_to_new_values(dimension, ordered_values)
    
    def _assign_styles_to_new_values(self, dimension: str, ordered_values: List[str]) -> None:
        """Assign consistent styles to dimension values using figure-level cycles."""
        # This will integrate with existing dr_plotter style/theme system
        # For now, create placeholder that will be enhanced with actual style logic
        
        for value in ordered_values:
            if value not in self._style_assignments[dimension]:
                # Assign next style from cycle
                style_dict = self._get_next_style_from_cycle(dimension)
                self._style_assignments[dimension][value] = style_dict
                self._cycle_positions[dimension] += 1
    
    def _get_next_style_from_cycle(self, dimension: str) -> Dict[str, Any]:
        """Get next style from figure-level style cycle."""
        # Placeholder - will be enhanced with actual dr_plotter theme integration
        position = self._cycle_positions[dimension]
        
        # Basic color cycle for initial implementation
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                 '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        
        return {
            'color': colors[position % len(colors)],
            'marker': ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h'][position % 10]
        }
    
    def get_subplot_styles(self, row: int, col: int, dimension: Optional[str], 
                          subplot_data: pd.DataFrame, **plot_kwargs) -> Dict[str, Any]:
        """Get consistent styles for a specific subplot."""
        if dimension is None or dimension not in self._style_assignments:
            # No dimension-based styling needed
            return plot_kwargs
        
        # Extract dimension values present in this subplot
        if dimension not in subplot_data.columns:
            return plot_kwargs
        
        dimension_values = subplot_data[dimension].unique().tolist()
        
        # Build style mapping for this subplot's dimension values
        subplot_style_map = {}
        for value in dimension_values:
            if value in self._style_assignments[dimension]:
                subplot_style_map[value] = self._style_assignments[dimension][value]
        
        # Convert to plot parameters format
        plot_styles = self._convert_to_plot_params(subplot_style_map, dimension_values, plot_kwargs)
        return plot_styles
    
    def _convert_to_plot_params(self, style_map: Dict[str, Dict[str, Any]], 
                               values: List[str], base_kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Convert style assignments to plot method parameters."""
        # This needs integration with existing dr_plotter plot parameter patterns
        
        if len(values) == 1:
            # Single value - apply style directly
            value = values[0]
            if value in style_map:
                result_kwargs = base_kwargs.copy()
                result_kwargs.update(style_map[value])
                return result_kwargs
        else:
            # Multiple values - need hue-based styling
            # This will integrate with existing hue_by parameter patterns
            colors = [style_map.get(v, {}).get('color', '#1f77b4') for v in values]
            markers = [style_map.get(v, {}).get('marker', 'o') for v in values]
            
            result_kwargs = base_kwargs.copy()
            # Integration point with existing dr_plotter color/marker handling
            result_kwargs['_coordinated_colors'] = colors
            result_kwargs['_coordinated_markers'] = markers
            return result_kwargs
        
        return base_kwargs
```

### Task 2: Integrate Style Coordinator with FigureManager

**Problem**: Need figure-level style coordinator that persists across multiple `plot_faceted()` calls.

**File**: `src/dr_plotter/figure.py`

**Implementation**:

1. **Add style coordinator to FigureManager state**:
```python
# In FigureManager.__init__() or _init_from_configs()
def _init_from_configs(self, ...):
    # ... existing initialization ...
    
    self._facet_grid_info: Optional[Dict[str, Any]] = None
    self._facet_style_coordinator: Optional[FacetStyleCoordinator] = None  # ADD THIS
```

2. **Add style coordinator factory method**:
```python
def _get_or_create_style_coordinator(self) -> FacetStyleCoordinator:
    """Get existing or create new style coordinator for figure-level consistency."""
    if self._facet_style_coordinator is None:
        from dr_plotter.faceting.style_coordination import FacetStyleCoordinator
        self._facet_style_coordinator = FacetStyleCoordinator()
    return self._facet_style_coordinator
```

3. **Integrate into plot_faceted() pipeline**:
```python
def plot_faceted(self, data: pd.DataFrame, plot_type: str, 
                faceting: Optional[FacetingConfig] = None, **kwargs) -> None:
    # ... existing parameter resolution and validation ...
    
    # NEW: Style coordination setup
    style_coordinator = self._get_or_create_style_coordinator()
    
    # Register dimension values for consistent styling
    if config.lines is not None:
        dimension_analysis = analyze_data_dimensions(data, config)
        lines_values = dimension_analysis.get("lines", [])
        style_coordinator.register_dimension_values(config.lines, lines_values)
    
    # ... existing grid computation and data preparation ...
    
    # Enhanced plotting with style coordination
    for (row_idx, col_idx) in target_positions:
        if (row_idx, col_idx) in data_subsets:
            subset_data = data_subsets[(row_idx, col_idx)]
            
            # Get coordinated styles for this subplot
            coordinated_styles = style_coordinator.get_subplot_styles(
                row_idx, col_idx, config.lines, subset_data, **plot_kwargs
            )
            
            self._apply_subplot_configuration(row_idx, col_idx, config)
            self.plot(plot_type, row_idx, col_idx, subset_data, **coordinated_styles)
```

### Task 3: Enhance Existing Plotter Integration

**Problem**: Existing plot methods need to understand coordinated styling parameters.

**Files to investigate and potentially modify**:
- `src/dr_plotter/plotters/` - Existing plotter implementations
- Integration points with `hue_by` parameter handling

**Implementation Strategy**:

1. **Investigate current hue_by handling**:
```python
# Research how current plot() method handles hue_by parameter
# Look for existing color/marker assignment logic
# Understand integration points with theme system
```

2. **Extend hue_by handling for coordinated styles**:
```python
# In relevant plotter classes
def plot(self, ..., hue_by=None, _coordinated_colors=None, _coordinated_markers=None, ...):
    if _coordinated_colors is not None and hue_by is not None:
        # Use coordinated colors instead of automatic color assignment
        # Integrate with existing hue_by logic but with predetermined colors
        pass
    else:
        # Existing logic unchanged
        pass
```

3. **Maintain backward compatibility**:
   - All existing plot() calls continue to work unchanged
   - Coordinated styling only activates when `_coordinated_*` parameters present
   - No breaking changes to existing plotter interfaces

### Task 4: Create Comprehensive Tests

**File**: `tests/test_faceting_style_coordination.py` (create new)

**Test Strategy**:

```python
class TestStyleCoordination:
    def test_single_call_consistency(self):
        """Test that same dimension values get same styles within single plot_faceted call."""
        data = create_test_data_with_consistent_dimension()
        
        with FigureManager(figure=FigureConfig(rows=2, cols=2)) as fm:
            fm.plot_faceted(
                data=data,
                plot_type="scatter",
                rows="metric",
                cols="dataset", 
                lines="model_size",  # "7B", "13B" should get consistent colors
                x="step",
                y="value"
            )
            
            # Verify "7B" gets same color in all subplots where it appears
            # Verify "13B" gets same color in all subplots where it appears
            # Verify "7B" and "13B" get different colors from each other
    
    def test_layered_faceting_consistency(self):
        """Test that dimension values get same styles across multiple plot_faceted calls."""
        scatter_data = create_scatter_data()
        line_data = create_line_data()
        
        with FigureManager(figure=FigureConfig(rows=2, cols=2)) as fm:
            # Layer 1: Scatter plots
            fm.plot_faceted(
                data=scatter_data,
                plot_type="scatter",
                rows="metric",
                cols="dataset",
                lines="model_size",
                x="step", 
                y="value",
                alpha=0.6
            )
            
            # Layer 2: Trend lines on same grid
            fm.plot_faceted(
                data=line_data,
                plot_type="line", 
                rows="metric",
                cols="dataset",
                lines="model_size",
                x="step",
                y="trend_value",
                linewidth=2
            )
            
            # Verify "7B" model gets same color in both scatter and line layers
            # Verify styling consistency across all subplots and layers
    
    def test_targeting_with_style_coordination(self):
        """Test style coordination works with targeting system."""
        data = create_test_data()
        
        with FigureManager(figure=FigureConfig(rows=2, cols=3)) as fm:
            # Layer 1: Base plots on all subplots
            fm.plot_faceted(
                data=data,
                plot_type="scatter",
                rows="metric",
                cols="recipe", 
                lines="model_size",
                x="step",
                y="value"
            )
            
            # Layer 2: Overlay only on specific targets
            fm.plot_faceted(
                data=data,
                plot_type="line",
                rows="metric",
                cols="recipe",
                lines="model_size",
                target_row=0,       # Only first row
                target_cols=[1, 2], # Only last two columns
                x="step",
                y="value",
                linewidth=3
            )
            
            # Verify consistent styling between base layer and overlay
            # Verify "model_size" values have same colors in both layers

class TestStyleCoordinatorModule:
    def test_dimension_value_registration(self):
        """Test FacetStyleCoordinator dimension registration."""
        coordinator = FacetStyleCoordinator()
        
        # Register values across multiple calls
        coordinator.register_dimension_values("model", ["7B", "13B"])
        coordinator.register_dimension_values("model", ["30B"])  # Add new value
        coordinator.register_dimension_values("model", ["7B"])   # Duplicate (should handle)
        
        # Verify all values registered and have consistent style assignments
        
    def test_style_assignment_consistency(self):
        """Test that same values always get same styles."""
        coordinator = FacetStyleCoordinator()
        
        # Register and get styles multiple times
        coordinator.register_dimension_values("model", ["7B", "13B", "30B"])
        
        styles1 = coordinator._style_assignments["model"]["7B"]
        styles2 = coordinator._style_assignments["model"]["7B"] 
        
        assert styles1 == styles2  # Same value always gets same style

class TestIntegrationWithExistingPlotters:
    def test_coordinated_styling_parameters_passed_through(self):
        """Test that _coordinated_* parameters reach plot methods."""
        # This will depend on actual plotter integration implementation
        pass
    
    def test_backward_compatibility_preserved(self):
        """Test that existing plot() calls work unchanged."""
        data = create_test_data()
        
        with FigureManager(figure=FigureConfig(rows=1, cols=1)) as fm:
            # Existing plot() call should work exactly as before
            fm.plot("scatter", 0, 0, data, x="step", y="value", hue_by="model_size")
            
            # No style coordination should activate
            # Should use existing color assignment logic
```

### Task 5: Integration with Theme System

**Problem**: Style coordination needs to work with existing dr_plotter theme system.

**Investigation Required**:
1. **Research current theme integration**:
   - How does dr_plotter currently handle themes?
   - Where are color cycles defined and managed?
   - How do existing plot methods integrate with themes?

2. **Enhanced FacetStyleCoordinator**:
```python
class FacetStyleCoordinator:
    def __init__(self, theme: Optional[Any] = None) -> None:
        self._theme = theme
        # ... existing initialization ...
    
    def _get_next_style_from_cycle(self, dimension: str) -> Dict[str, Any]:
        """Get next style from figure-level theme cycle."""
        if self._theme and hasattr(self._theme, 'color_cycle'):
            # Use theme color cycle
            colors = self._theme.color_cycle
        else:
            # Fallback to default colors
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', ...]
        
        # Similar pattern for markers, line styles, etc.
```

3. **FigureManager integration**:
```python
def _get_or_create_style_coordinator(self) -> FacetStyleCoordinator:
    if self._facet_style_coordinator is None:
        # Pass figure-level theme to coordinator
        theme = getattr(self, '_theme', None)  # Investigate actual theme storage
        self._facet_style_coordinator = FacetStyleCoordinator(theme=theme)
    return self._facet_style_coordinator
```

### Task 6: Execute and Verify All Tests

**CRITICAL**: Comprehensive testing of style coordination functionality.

**Run Tests in Order**:

1. **Test new style coordination module**:
```bash
pytest tests/test_faceting_style_coordination.py -v
```

2. **Test existing functionality preserved**:
```bash
pytest tests/test_faceting_integration.py -v
pytest tests/test_faceting*.py -v
```

3. **Test all dr_plotter functionality**:
```bash
pytest tests/ -x  # Stop on first failure
```

**Expected Results**:
- All new style coordination tests pass
- All existing 83/83 faceting tests continue to pass
- All other dr_plotter tests continue to pass  
- Style coordination works across layered faceting scenarios

### Task 7: Create Real-World Style Coordination Examples

**File**: `tests/test_faceting_style_coordination.py` - Add advanced scenario test

```python
class TestAdvancedStyleCoordination:
    def test_complex_ml_dashboard_layered_styling(self):
        """Test complex layered ML dashboard with consistent styling."""
        
        # Base training data
        training_data = pd.DataFrame({
            'step': list(range(500)) * 24,
            'metric': ['train_loss', 'val_loss', 'train_acc', 'val_acc'] * 3000,
            'model_size': ['7B', '13B', '30B', '65B'] * 3000, 
            'dataset': ['squad', 'glue', 'c4'] * 4000,
            'value': [0.8 - i * 0.001 for i in range(12000)]
        })
        
        # Trend data (subset)
        trend_data = training_data[training_data['step'] % 50 == 0].copy()
        trend_data['trend_value'] = trend_data['value'] * 0.95
        
        # Confidence interval data  
        ci_data = training_data[training_data['step'] % 100 == 0].copy()
        ci_data['ci_lower'] = ci_data['value'] * 0.9
        ci_data['ci_upper'] = ci_data['value'] * 1.1
        
        with FigureManager(figure=FigureConfig(rows=2, cols=3, figsize=(18, 10))) as fm:
            # Layer 1: Base scatter plots (all subplots)
            fm.plot_faceted(
                data=training_data,
                plot_type="scatter",
                rows="metric",     # 4 metrics wrapped to 2×3 grid (actually 2×2)
                cols="dataset",    # 3 datasets
                lines="model_size", # 4 model sizes (consistent colors needed)
                x="step",
                y="value",
                alpha=0.4,
                s=20
            )
            
            # Layer 2: Trend lines (all subplots) 
            fm.plot_faceted(
                data=trend_data,
                plot_type="line",
                rows="metric",
                cols="dataset", 
                lines="model_size",  # MUST have same colors as Layer 1
                x="step",
                y="trend_value",
                linewidth=2
            )
            
            # Layer 3: Confidence intervals (only accuracy metrics)
            accuracy_metrics = ['train_acc', 'val_acc']
            ci_subset = ci_data[ci_data['metric'].isin(accuracy_metrics)]
            
            fm.plot_faceted(
                data=ci_subset,
                plot_type="fill_between",
                rows="metric",
                cols="dataset",
                lines="model_size",  # MUST have same colors as previous layers
                target_rows=[1],     # Only accuracy row (depends on ordering)
                x="step", 
                y1="ci_lower",
                y2="ci_upper", 
                alpha=0.2
            )
            
            # Verification: Check that model sizes have consistent colors across all layers
            # "7B" should be same color in scatter, line, and fill_between
            # "13B" should be same color across all layers
            # etc.
            
            style_coordinator = fm._facet_style_coordinator
            assert style_coordinator is not None
            assert "model_size" in style_coordinator._style_assignments
            
            # Verify each model size has consistent style assignment
            model_styles = style_coordinator._style_assignments["model_size"]
            for model_size in ["7B", "13B", "30B", "65B"]:
                assert model_size in model_styles
                # Each model should have consistent color assigned
```

### Task 8: Performance and Memory Considerations

**Problem**: Style coordination must not significantly impact performance.

**Implementation Requirements**:

1. **Efficient style storage**:
   - Use dictionaries for O(1) style lookup
   - Only store styles for values that actually exist in data
   - Don't pre-compute styles for all possible combinations

2. **Memory management**:
   - Style coordinator persists for FigureManager lifetime only
   - Clear style coordinator when FigureManager is destroyed
   - Don't accumulate unbounded style assignments

3. **Performance testing**:
```python
def test_style_coordination_performance(self):
    """Test that style coordination doesn't significantly slow plotting."""
    large_data = create_large_dataset(n_points=10000, n_models=20)
    
    import time
    
    # Timing without style coordination (baseline)
    start = time.time()
    with FigureManager() as fm:
        fm.plot("scatter", 0, 0, large_data, x="step", y="value", hue_by="model")
    baseline_time = time.time() - start
    
    # Timing with style coordination 
    start = time.time()
    with FigureManager(figure=FigureConfig(rows=2, cols=2)) as fm:
        fm.plot_faceted(large_data, "scatter", rows="metric", cols="dataset", 
                       lines="model", x="step", y="value")
    coordinated_time = time.time() - start
    
    # Should not be more than 50% slower
    assert coordinated_time < baseline_time * 1.5
```

## Success Criteria

Before marking Chunk 5 complete, verify ALL of these:

### Core Functionality 
- [ ] **Same dimension values get identical styles** across all subplots within single `plot_faceted()` call
- [ ] **Style consistency across layers** - multiple `plot_faceted()` calls maintain consistent styling for same dimension values
- [ ] **Integration with existing plotters** - coordinated styles work with all plot types (scatter, line, fill_between, etc.)
- [ ] **Theme system integration** - style coordination respects existing dr_plotter themes
- [ ] **Targeting compatibility** - style coordination works with targeting system from Chunk 4

### Quality and Performance
- [ ] **All existing tests pass** - 83/83 faceting tests + all other dr_plotter tests continue working
- [ ] **New style coordination tests comprehensive** - cover single call, layered faceting, targeting scenarios
- [ ] **Performance acceptable** - style coordination adds <50% overhead to plotting time
- [ ] **Memory usage reasonable** - style coordinator doesn't cause memory leaks or unbounded growth
- [ ] **Backward compatibility preserved** - all existing plot() calls work exactly as before

### Integration and Architecture  
- [ ] **Clean module structure** - style coordination properly integrated with `faceting/` module architecture
- [ ] **Import structure maintained** - no circular dependencies or import issues
- [ ] **State management correct** - style coordinator properly managed within FigureManager lifecycle
- [ ] **Error handling robust** - graceful handling of edge cases and invalid configurations

## Implementation Notes

### Key Architecture Challenges
- **State Persistence**: Style coordinator must persist across multiple `plot_faceted()` calls within same FigureManager
- **Plotter Integration**: Coordinated styles must integrate cleanly with existing plot method parameter handling  
- **Theme Compatibility**: Must work with existing dr_plotter theme system without conflicts
- **Performance**: Style coordination logic must be efficient for large datasets and complex grids

### Code Quality Requirements  
- **All imports at top**: No mid-function imports anywhere
- **Complete type hints**: Every new function fully typed
- **No comments**: Self-documenting code through clear names
- **Assertions for validation**: Use existing patterns, maintain consistency
- **Pure function extraction**: Style logic should be testable independently where possible

### Integration Strategy
- **Minimal plotter changes**: Prefer parameter-based integration over deep plotter modification
- **Backward compatibility**: Existing functionality must work exactly as before
- **Incremental enhancement**: Style coordination should activate only when faceting is used
- **Clean separation**: Style coordination logic separate from basic plotting logic

### Common Pitfalls to Avoid
- **Don't break existing styling**: Regular plot() calls must work unchanged
- **Don't create circular dependencies**: Style coordination should not require changes to core plotters
- **Don't ignore performance**: Style coordination must scale reasonably with data size
- **Don't skip theme integration**: Must work with existing theme patterns

## Documentation Requirements

When you complete this chunk, update the implementation plan:

**File**: `docs/plans/faceted_plotting_implementation_plan.md`

Add comprehensive "Chunk 5 Notes" section with:
- **Style coordination implementation**: How FacetStyleCoordinator works and integrates
- **Test execution results**: Pass/fail counts for new style coordination tests
- **Plotter integration details**: How coordinated styling interfaces with existing plot methods
- **Theme system integration**: How style coordination works with dr_plotter themes  
- **Performance observations**: Impact on execution speed and memory usage
- **Layered faceting capabilities**: Complex scenarios enabled by style coordination
- **Recommendations for Chunk 6**: How style coordination prepares for final validation and polish

## Next Steps After Completion

After successfully implementing Chunk 5:
1. **Execute comprehensive test suite** and verify no regressions
2. **Update progress tracking** with detailed implementation insights
3. **Ready for Chunk 6** (Validation & Polish) - the final chunk
4. **Style coordination complete** - layered faceting with consistent styling fully working

This is the most complex chunk - style coordination enables sophisticated layered visualizations while maintaining the intuitive simple API for basic cases. Take time to understand existing plotter integration patterns before implementation.
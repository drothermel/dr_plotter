# Faceted Plotting Implementation: Chunk 4 - Advanced Layout Features

## Project Context

You are implementing **Chunk 4** - Advanced Layout Features for dr_plotter's native faceting support.

**Your role**: Add wrapped layouts, targeting system, and per-subplot configuration while building on the clean refactored foundation from Chunk 3.5.

**Foundation**: Chunks 1-3.5 completed successfully with working end-to-end faceted plotting (73/73 faceting tests passing, 120/120 total tests passing) and clean modular architecture.

## Key References

**MANDATORY**: Before starting, read these docs:
- `docs/DESIGN_PHILOSOPHY.md` - Core principles and coding standards
- `docs/plans/faceted_plotting_detailed_design.md` - Complete technical architecture 
- `docs/plans/faceted_plotting_implementation_plan.md` - Previous chunk implementation notes and patterns
- `docs/plans/context_restoration_guide_faceted_plotting.md` - Current capabilities and scope

## Current Capabilities (From Chunk 3)

**What works now**:
```python
# Simple explicit grid faceting (rows + cols specified)
fm.plot_faceted(
    data=df,
    plot_type="line", 
    rows="metric",      # 2 metrics across rows
    cols="recipe",      # 4 recipes across columns  
    lines="model_size", # Multiple model sizes as different lines
    x="step",
    y="value"
)
```

**Current limitations (intentionally blocked in Chunk 3)**:
- No wrapped layouts (`rows + ncols`, `cols + nrows`)
- No targeting (`target_row`, `target_cols`, etc.)
- No per-subplot control (nested list parameters like `x_labels`, `xlim`)

## Your Tasks

### Task 1: Enable Wrapped Layout Support

**Problem**: Chunk 3 validation blocks wrapped layouts with assertion errors.

**Files to modify**:
- `src/dr_plotter/faceting_config.py` - Update validation logic
- `src/dr_plotter/figure.py` - Remove blocking validation in `plot_faceted()`
- `tests/test_faceting_integration.py` - Add wrapped layout tests

**Implementation**:

1. **Update FacetingConfig validation** to allow wrapped layouts:
```python
# In src/dr_plotter/faceting_config.py
def validate(self) -> None:
    # REMOVE or modify this assertion that blocks wrapped layouts:
    # assert not (self.rows and self.cols and (self.ncols or self.nrows)), "Cannot specify both..."
    
    # ADD proper wrapped layout validation:
    if self.rows and self.cols and (self.ncols or self.nrows):
        assert False, f"Cannot specify both explicit grid (rows+cols) and wrap layout (ncols/nrows). Current config: rows='{self.rows}', cols='{self.cols}', ncols={self.ncols}, nrows={self.nrows}"
    
    # Ensure wrapped layouts are properly configured
    if self.ncols is not None:
        assert self.rows is not None and self.cols is None, "ncols requires rows dimension and no cols dimension"
    if self.nrows is not None:
        assert self.cols is not None and self.rows is None, "nrows requires cols dimension and no rows dimension"
```

2. **Remove Chunk 3 blocking validation** in `plot_faceted()`:
```python
# In src/dr_plotter/figure.py
def plot_faceted(self, ...):
    # REMOVE these Chunk 3 blocking assertions:
    # assert config.ncols is None, "Wrapped layouts not supported in Chunk 3"
    # assert config.nrows is None, "Wrapped layouts not supported in Chunk 3"
    
    # The grid computation already supports wrapped layouts via grid_computation.py
```

3. **Add comprehensive wrapped layout tests**:
```python
# In tests/test_faceting_integration.py - new test class
class TestWrappedLayouts:
    def test_rows_with_ncols_layout(self):
        data = create_test_data_with_multiple_metrics()  # 4+ unique metrics
        
        with FigureManager(figure=FigureConfig(rows=2, cols=3, figsize=(15, 10))) as fm:
            fm.plot_faceted(
                data=data,
                plot_type="line",
                rows="metric",      # 4 metrics
                ncols=3,           # Wrap into 2×3 grid  
                x="step",
                y="value"
            )
            
            grid_info = fm._facet_grid_info
            assert grid_info["layout_metadata"]["grid_type"] == "wrapped_rows"
            assert grid_info["layout_metadata"]["n_rows"] == 2
            assert grid_info["layout_metadata"]["n_cols"] == 3

    def test_cols_with_nrows_layout(self):
        data = create_test_data_with_multiple_models()  # 5+ unique models
        
        with FigureManager(figure=FigureConfig(rows=3, cols=2, figsize=(10, 15))) as fm:
            fm.plot_faceted(
                data=data,
                plot_type="scatter",
                cols="model",       # 5 models  
                nrows=3,           # Wrap into 3×2 grid
                x="step", 
                y="value"
            )
            
            grid_info = fm._facet_grid_info
            assert grid_info["layout_metadata"]["grid_type"] == "wrapped_cols"
```

### Task 2: Enable Targeting System

**Problem**: Chunk 3 blocks all targeting parameters with assertion errors.

**Files to modify**:
- `src/dr_plotter/figure.py` - Remove targeting validation blocks
- `tests/test_faceting_integration.py` - Add targeting tests

**Implementation**:

1. **Remove Chunk 3 targeting blocks**:
```python
# In src/dr_plotter/figure.py - plot_faceted()
def plot_faceted(self, ...):
    # REMOVE these blocking assertions:
    # if any([target_row, target_col, target_rows, target_cols]):
    #     assert False, "Targeting not supported in Chunk 3"
    
    # The targeting logic already exists in grid_computation.resolve_target_positions()
```

2. **Add comprehensive targeting tests**:
```python
# In tests/test_faceting_integration.py - new test class  
class TestTargetingSystem:
    def test_single_row_targeting(self):
        data = create_test_data()
        
        with FigureManager(figure=FigureConfig(rows=2, cols=3, figsize=(15, 10))) as fm:
            # Plot only in row 0 (first row)
            fm.plot_faceted(
                data=data,
                plot_type="line",
                rows="metric",
                cols="recipe", 
                target_row=0,   # Only first row
                x="step",
                y="value"
            )
            
            # Verify plotting occurred only in targeted positions
            # Check that row 1 subplots remain empty/untouched

    def test_multiple_positions_targeting(self):
        data = create_test_data()
        
        with FigureManager(figure=FigureConfig(rows=2, cols=4, figsize=(20, 10))) as fm:
            # First layer: scatter plots in specific columns
            fm.plot_faceted(
                data=data,
                plot_type="scatter", 
                rows="metric",
                cols="recipe",
                target_cols=[0, 2],  # Only columns 0 and 2
                x="step",
                y="value",
                alpha=0.6
            )
            
            # Second layer: trend lines in specific row
            fm.plot_faceted(
                data=trend_data,
                plot_type="line",
                rows="metric", 
                cols="recipe",
                target_row=1,        # Only second row
                x="step",
                y="trend_value",
                linewidth=2
            )

    def test_targeting_with_wrapped_layouts(self):
        data = create_test_data_with_multiple_metrics()  # 6+ metrics
        
        with FigureManager(figure=FigureConfig(rows=2, cols=3, figsize=(15, 10))) as fm:
            fm.plot_faceted(
                data=data,
                plot_type="line",
                rows="metric",
                ncols=3,           # 6 metrics wrapped to 2×3
                target_rows=[0],   # Only first row (first 3 metrics)
                x="step",
                y="value"
            )
```

### Task 3: Enable Per-Subplot Configuration

**Problem**: Nested list parameters from FigureConfig (x_labels, xlim, ylim) are not supported in faceting.

**Files to modify**:
- `src/dr_plotter/figure.py` - Add `_apply_subplot_configuration()` method
- `src/dr_plotter/faceting/validation.py` - Add nested list validation
- `tests/test_faceting_integration.py` - Add per-subplot configuration tests

**Implementation**:

1. **Add subplot configuration method**:
```python
# In src/dr_plotter/figure.py
def _apply_subplot_configuration(self, row: int, col: int, config: FacetingConfig) -> None:
    """Apply nested list parameters (x_labels, xlim, etc.) to specific subplot."""
    
    # Apply x_labels if specified
    if config.x_labels is not None and len(config.x_labels) > row and len(config.x_labels[row]) > col:
        label = config.x_labels[row][col]
        if label is not None:
            ax = self.fig.axes[row * self._figure_config.cols + col]
            ax.set_xlabel(label)
    
    # Apply y_labels if specified  
    if config.y_labels is not None and len(config.y_labels) > row and len(config.y_labels[row]) > col:
        label = config.y_labels[row][col]
        if label is not None:
            ax = self.fig.axes[row * self._figure_config.cols + col]
            ax.set_ylabel(label)
    
    # Apply xlim if specified
    if config.xlim is not None and len(config.xlim) > row and len(config.xlim[row]) > col:
        limits = config.xlim[row][col]
        if limits is not None:
            ax = self.fig.axes[row * self._figure_config.cols + col]
            ax.set_xlim(limits)
    
    # Apply ylim if specified
    if config.ylim is not None and len(config.ylim) > row and len(config.ylim[row]) > col:
        limits = config.ylim[row][col]
        if limits is not None:
            ax = self.fig.axes[row * self._figure_config.cols + col]
            ax.set_ylim(limits)
```

2. **Integrate into plot execution**:
```python
# In src/dr_plotter/figure.py - plot_faceted()
for (row, col) in target_positions:
    if (row, col) in data_subsets:
        subplot_data = data_subsets[(row, col)]
        
        # Apply per-subplot configuration BEFORE plotting
        self._apply_subplot_configuration(row, col, config)
        
        # Execute the actual plot
        self.plot(plot_type, row, col, subplot_data, 
                 x=config.x, y=config.y, hue_by=config.lines, **plot_kwargs)
```

3. **Add nested list validation**:
```python
# In src/dr_plotter/faceting/validation.py
def validate_nested_list_dimensions(nested_list: List[List[Any]], 
                                   expected_rows: int, expected_cols: int, 
                                   param_name: str) -> None:
    """Validate nested list matches expected grid dimensions."""
    if nested_list is None:
        return
        
    assert len(nested_list) == expected_rows, (
        f"{param_name} must have {expected_rows} rows, got {len(nested_list)}"
    )
    
    for i, row in enumerate(nested_list):
        assert len(row) == expected_cols, (
            f"{param_name}[{i}] must have {expected_cols} columns, got {len(row)}"
        )
```

4. **Add per-subplot configuration tests**:
```python
# In tests/test_faceting_integration.py - new test class
class TestPerSubplotConfiguration:
    def test_nested_x_labels_application(self):
        data = create_test_data()
        
        x_labels = [
            ["Training Steps", "Validation Steps", "Test Steps"],
            ["Time", "Iterations", "Epochs"]  
        ]
        
        with FigureManager(figure=FigureConfig(rows=2, cols=3, figsize=(15, 10))) as fm:
            fm.plot_faceted(
                data=data,
                plot_type="line",
                rows="metric", 
                cols="dataset",
                x_labels=x_labels,
                x="step",
                y="value"
            )
            
            # Verify labels were applied correctly
            axes = fm.fig.axes
            assert axes[0].get_xlabel() == "Training Steps"  # Row 0, Col 0
            assert axes[1].get_xlabel() == "Validation Steps"  # Row 0, Col 1
            assert axes[3].get_xlabel() == "Time"  # Row 1, Col 0

    def test_nested_axis_limits(self):
        data = create_test_data()
        
        xlim = [
            [(0, 100), None, (50, 150)],      # Row 0 limits
            [None, (0, 200), (25, 125)]       # Row 1 limits  
        ]
        
        with FigureManager(figure=FigureConfig(rows=2, cols=3, figsize=(15, 10))) as fm:
            fm.plot_faceted(
                data=data,
                plot_type="scatter", 
                rows="metric",
                cols="dataset",
                xlim=xlim,
                x="step",
                y="value"
            )
            
            # Verify limits were applied
            axes = fm.fig.axes
            assert axes[0].get_xlim() == (0, 100)    # Row 0, Col 0
            assert axes[2].get_xlim() == (50, 150)   # Row 0, Col 2
            assert axes[4].get_xlim() == (0, 200)    # Row 1, Col 1

    def test_per_subplot_config_with_targeting(self):
        """Test that per-subplot config works with targeting."""
        data = create_test_data()
        
        # Only apply labels to targeted subplots
        x_labels = [
            ["Target Label", "Not Applied", "Not Applied"],
            ["Not Applied", "Not Applied", "Not Applied"]  
        ]
        
        with FigureManager(figure=FigureConfig(rows=2, cols=3, figsize=(15, 10))) as fm:
            fm.plot_faceted(
                data=data,
                plot_type="line",
                rows="metric",
                cols="dataset", 
                target_row=0,        # Only first row targeted
                target_col=0,        # Only first column targeted  
                x_labels=x_labels,
                x="step",
                y="value"
            )
            
            # Verify label applied only to targeted subplot
            axes = fm.fig.axes
            assert axes[0].get_xlabel() == "Target Label"  # (0,0) - targeted
            # Other subplots should have default/empty labels
```

### Task 4: Extend Grid Computation Integration

**Problem**: Need to ensure new advanced features integrate properly with existing grid computation.

**Files to modify**:
- `src/dr_plotter/figure.py` - Enhanced integration with faceting modules
- Test integration between advanced features and grid computation

**Implementation**:

1. **Enhance grid computation integration**:
```python
# In src/dr_plotter/figure.py - plot_faceted()
def plot_faceted(self, ...):
    # ... existing parameter resolution ...
    
    # Compute grid layout (supports all modes now)
    from dr_plotter.faceting import compute_grid_dimensions, compute_grid_layout_metadata
    
    grid_rows, grid_cols = compute_grid_dimensions(data, config)
    layout_metadata = compute_grid_layout_metadata(data, config, grid_rows, grid_cols)
    
    # Validate grid against FigureManager if needed
    self._validate_facet_grid_against_existing(grid_rows, grid_cols)
    
    # Resolve targeting (now supports all targeting modes)
    from dr_plotter.faceting import resolve_target_positions
    target_positions = resolve_target_positions(config, grid_rows, grid_cols)
    
    # Validate nested list parameters against computed grid
    from dr_plotter.faceting.validation import validate_nested_list_dimensions
    if config.x_labels is not None:
        validate_nested_list_dimensions(config.x_labels, grid_rows, grid_cols, "x_labels")
    if config.xlim is not None:
        validate_nested_list_dimensions(config.xlim, grid_rows, grid_cols, "xlim")
```

### Task 5: Execute and Verify All Tests

**CRITICAL**: You must verify that advanced features work correctly and don't break existing functionality.

**Run Tests in Order**:

1. **Test FacetingConfig validation updates**:
```bash
pytest tests/test_faceting_config.py -v
```

2. **Test new advanced features**:
```bash
pytest tests/test_faceting_integration.py::TestWrappedLayouts -v
pytest tests/test_faceting_integration.py::TestTargetingSystem -v  
pytest tests/test_faceting_integration.py::TestPerSubplotConfiguration -v
```

3. **Test all faceting functionality**:
```bash
pytest tests/test_faceting*.py -v
```

4. **Full test suite**:
```bash
pytest tests/ -x  # Stop on first failure
```

**Expected Results**:
- All new advanced feature tests pass
- All existing 73/73 faceting tests continue to pass  
- All 120+ total dr_plotter tests continue to pass
- No performance regressions

### Task 6: Create Real-World Advanced Examples

**File**: `tests/test_faceting_integration.py` - Add comprehensive real-world test

```python
class TestAdvancedRealWorldScenarios:
    def test_ml_training_dashboard_advanced(self):
        """Test complex ML training dashboard with all advanced features."""
        training_data = pd.DataFrame({
            'step': list(range(1000)) * 12,
            'metric': ['train_loss', 'val_loss', 'train_acc', 'val_acc', 'train_f1', 'val_f1'] * 2000,
            'model_size': ['7B', '13B', '30B', '65B'] * 3000,
            'dataset': ['squad', 'glue'] * 6000,
            'value': [0.5 - i * 0.001 + random.uniform(-0.1, 0.1) for i in range(12000)]
        })
        
        # Complex nested configuration
        x_labels = [
            ["Training Steps", "Training Steps", "Steps", "Steps"],
            ["Steps", "Steps", "Validation Steps", "Validation Steps"],
            ["Steps", "Steps", "Steps", "Steps"]
        ]
        
        xlim = [
            [(0, 800), (0, 800), None, None], 
            [None, None, (100, 900), (100, 900)],
            [(0, 1000), (0, 1000), (0, 1000), (0, 1000)]
        ]
        
        with FigureManager(figure=FigureConfig(rows=3, cols=4, figsize=(20, 15))) as fm:
            # Base layer: All metrics, wrapped layout
            fm.plot_faceted(
                data=training_data,
                plot_type="line",
                rows="metric",           # 6 metrics
                ncols=4,                # Wrap to 2×4 grid (becomes 3×4 with 6 metrics)
                lines="model_size",     # Different model sizes as lines
                x_labels=x_labels,
                xlim=xlim,
                x="step",
                y="value",
                alpha=0.7
            )
            
            # Overlay layer: Highlight specific model on specific metrics  
            highlight_data = training_data[
                (training_data['model_size'] == '65B') & 
                (training_data['metric'].isin(['train_loss', 'val_loss']))
            ]
            
            fm.plot_faceted(
                data=highlight_data,
                plot_type="line", 
                rows="metric",
                ncols=4,
                target_rows=[0, 1],     # Only first two metric rows
                target_cols=[0, 1],     # Only first two dataset columns
                lines="model_size",
                x="step",
                y="value",
                linewidth=3,
                color='red'
            )
            
            # Verify complex integration worked
            grid_info = fm._facet_grid_info
            assert grid_info["layout_metadata"]["grid_type"] == "wrapped_rows"
            assert len(grid_info["data_subsets"]) > 0
```

## Success Criteria

Before marking Chunk 4 complete, verify ALL of these:

### Functionality Verification
- [ ] **Wrapped layouts work correctly** - `rows + ncols` and `cols + nrows` create proper grids
- [ ] **Targeting system functional** - `target_row`, `target_cols`, etc. apply plots to correct subplots only
- [ ] **Per-subplot configuration working** - `x_labels`, `xlim`, `ylim` nested lists apply correctly
- [ ] **Advanced features integrate** - wrapped layouts + targeting + per-subplot config work together
- [ ] **Layered faceting enhanced** - multiple `plot_faceted()` calls with advanced features compose correctly

### Quality Verification  
- [ ] **All existing tests pass** - 73/73 faceting tests + all other dr_plotter tests (120+)
- [ ] **New advanced feature tests comprehensive** - good coverage of wrapped layouts, targeting, per-subplot config
- [ ] **Real-world scenarios work** - complex ML dashboard examples execute successfully
- [ ] **Error handling robust** - clear errors for invalid configurations and missing data
- [ ] **Performance maintained** - no significant slowdown from advanced features

### Integration Verification
- [ ] **Grid computation integration** - advanced features use existing `faceting/` modules correctly
- [ ] **Parameter validation updated** - FacetingConfig properly validates advanced configurations
- [ ] **Existing API preserved** - simple explicit grid faceting continues to work unchanged
- [ ] **Import structure clean** - no new import issues or circular dependencies

## Implementation Notes

### Key Architecture Points
- **Build on Chunk 3.5 foundation**: Use clean modular structure with pure functions
- **Remove validation blocks**: Chunk 3 intentionally blocked advanced features - remove those blocks
- **Preserve existing functionality**: All current capabilities must continue working
- **Leverage existing computation**: Grid computation already supports advanced features mathematically

### Code Quality Requirements
- **All imports at top**: No mid-function imports anywhere  
- **Complete type hints**: Every new/modified function fully typed
- **No comments**: Self-documenting code through clear names
- **Assertions for validation**: Use existing patterns, don't introduce exceptions
- **Pure function usage**: Leverage extracted functions from `faceting/` modules

### Testing Strategy
- **Layer testing**: Test each advanced feature independently, then together
- **Real-world scenarios**: Complex multi-layered examples that mirror actual use cases
- **Edge case coverage**: Invalid configurations, missing data, boundary conditions
- **Performance verification**: Ensure advanced features don't significantly impact speed

### Common Pitfalls to Avoid
- **Don't change existing behavior**: Only add new capabilities, don't modify working features
- **Don't skip validation**: Advanced features need proper error checking
- **Don't break simple cases**: Ensure basic `rows + cols` faceting still works perfectly
- **Don't ignore integration**: Advanced features must work together seamlessly

## Documentation Requirements

When you complete this chunk, update the implementation plan:

**File**: `docs/plans/faceted_plotting_implementation_plan.md`

Add comprehensive "Chunk 4 Notes" section with:
- **Advanced features implemented**: Wrapped layouts, targeting, per-subplot configuration details
- **Test execution results**: Pass/fail counts for new advanced feature tests  
- **Integration validation**: How advanced features work with existing functionality
- **Real-world scenario verification**: Complex dashboard examples working correctly
- **Performance observations**: Any impact on execution speed or memory usage
- **API enhancement summary**: New capabilities added to `plot_faceted()` method
- **Recommendations for Chunk 5**: How advanced layout features prepare for style coordination

## Next Steps After Completion

After successfully implementing Chunk 4:
1. **Execute comprehensive test suite** and verify no regressions
2. **Update progress tracking** in implementation plan with detailed notes
3. **Ready for Chunk 5** (Style Coordination) - the most complex remaining chunk
4. **Advanced layout foundation complete** - targeting, wrapping, per-subplot control all working

This chunk transforms dr_plotter faceting from basic grid support to a comprehensive multi-dimensional visualization system with fine-grained control while maintaining the simple API for common cases.
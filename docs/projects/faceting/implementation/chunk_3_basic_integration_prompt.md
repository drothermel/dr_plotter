# Faceted Plotting Implementation: Chunk 3 - Basic Plot Integration

## Project Context

You are implementing **Chunk 3 of 6** for native faceting support in dr_plotter. This chunk creates the first working end-to-end faceted plotting functionality by integrating grid computation with actual plot execution.

**Your role**: Transform the mathematical foundation from Chunk 2 into working faceted plots, focusing on simple cases without advanced features.

**Foundation**: Chunks 1-2 completed successfully with `FacetingConfig` and robust grid computation engine available.

## Key References

**MANDATORY**: Before starting, read these docs to understand the project:
- `docs/DESIGN_PHILOSOPHY.md` - Core principles and coding standards
- `docs/plans/faceted_plotting_detailed_design.md` - Complete technical architecture 
- `docs/plans/faceted_plotting_implementation_plan.md` - Your place in the overall plan and previous chunk learnings

## Your Tasks

### Task 1: Implement Core Plot Integration

**File**: `src/dr_plotter/figure.py`

Replace the stub `plot_faceted()` method from Chunk 2 with full implementation:

```python
def plot_faceted(self, data: pd.DataFrame, plot_type: str, 
                faceting: Optional['FacetingConfig'] = None, **kwargs) -> None:
    """
    Create faceted plots across subplot grid.
    
    This implementation supports:
    - Explicit grid layouts (rows + cols)
    - Simple data subsetting and plotting
    - Basic parameter resolution (direct params override config)
    - Integration with existing plot() method
    
    NOT yet supported (future chunks):
    - Wrapped layouts (rows/cols + ncols/nrows) 
    - Targeting (target_row, target_col, etc.)
    - Per-subplot configuration (x_labels, xlim nested lists)
    - Cross-subplot style coordination
    """
    from dr_plotter.faceting_config import FacetingConfig
    
    # 1. Input validation and configuration resolution
    # 2. Grid computation using Chunk 2 methods
    # 3. Data preparation and subsetting
    # 4. Execute plots for each subplot position
    # 5. Store state for future faceting calls
```

**Scope Limitations** (Important):
- **ONLY explicit grids**: `rows` + `cols` specified (no wrapped layouts)
- **NO targeting**: Ignore `target_*` parameters for now  
- **NO nested list parameters**: Ignore `x_labels`, `xlim`, etc. for now
- **NO advanced styling**: Use default styling for now

### Task 2: Implement Data Preparation

**File**: `src/dr_plotter/figure.py`

Add method to prepare data subsets for each subplot:

```python
def _prepare_facet_data(self, data: pd.DataFrame, config: FacetingConfig, 
                       layout_metadata: Dict[str, Any]) -> Dict[Tuple[int, int], pd.DataFrame]:
    """
    Prepare data subsets for each subplot position based on grid layout.
    
    Args:
        data: Source DataFrame
        config: Resolved faceting configuration  
        layout_metadata: Output from _compute_facet_grid()
        
    Returns:
        Dictionary mapping (row_idx, col_idx) -> DataFrame subset for that position
        
    Logic:
        - Extract row_values and col_values from layout_metadata
        - For each grid position, filter data matching row and col values
        - Handle missing combinations gracefully (empty DataFrames)
        - Preserve data types and column structure
    """
```

**Data Handling Requirements**:
- Use `data.copy()` to avoid mutating original DataFrame
- Filter based on exact value matches for row/col dimensions
- Handle missing data combinations (some grid positions may have no data)
- Preserve all columns needed for plotting (x, y, lines dimension)
- Return empty DataFrame (not None) for positions with no data

### Task 3: Add Input Validation

**File**: `src/dr_plotter/figure.py`

Add comprehensive validation method:

```python
def _validate_faceting_inputs(self, data: pd.DataFrame, config: FacetingConfig) -> None:
    """
    Validate all inputs for faceted plotting with helpful error messages.
    
    Validation checks:
    - DataFrame has required columns (rows, cols, lines, x, y)
    - Dimension columns contain expected values  
    - Configuration is valid (calls config.validate())
    - No unsupported features for Chunk 3 scope
    """
```

**Validation Rules for Chunk 3**:
1. **Data validation**: All required columns exist in DataFrame
2. **Dimension validation**: `rows`, `cols`, `lines` columns have values
3. **Coordinate validation**: `x` and `y` columns exist and have plottable data
4. **Scope validation**: No wrapped layouts, targeting, or nested lists specified
5. **Configuration validation**: Call `config.validate()` from Chunk 1

**Error Message Standards**:
- List available columns when required columns missing
- Show actual data values when dimension values don't match
- Provide specific guidance about unsupported features
- Use assertion-based validation following dr_plotter standards

### Task 4: Integrate with Existing Plot Methods

**File**: `src/dr_plotter/figure.py`

Ensure smooth integration with existing plotting infrastructure:

```python
def _execute_faceted_plotting(self, data_subsets: Dict[Tuple[int, int], pd.DataFrame],
                             config: FacetingConfig, plot_type: str, **plot_kwargs) -> None:
    """
    Execute individual plot calls for each data subset using existing plot() method.
    
    For each (row_idx, col_idx) position with data:
    - Call self.plot(plot_type, row_idx, col_idx, subset_data, ...)
    - Pass through x, y, hue_by (lines), and other plot parameters
    - Skip positions with empty data subsets
    """
```

**Integration Requirements**:
- Use existing `self.plot()` method for actual plotting
- Pass `plot_type` exactly as provided by user
- Forward `x`, `y`, and `hue_by` parameters correctly
- Map `config.lines` to `hue_by` parameter for series differentiation
- Pass through all additional `**plot_kwargs` unchanged
- Handle empty data subsets gracefully (skip, don't error)

### Task 5: Handle Configuration Resolution

**File**: `src/dr_plotter/figure.py`

Improve the configuration resolution from Chunk 2:

```python
def _resolve_faceting_config(self, faceting: Optional['FacetingConfig'], **kwargs) -> 'FacetingConfig':
    """
    Merge faceting config with direct parameters, with direct params taking precedence.
    
    Enhanced for Chunk 3:
    - Extract x, y parameters from kwargs for validation
    - Handle plot-specific parameters vs faceting parameters  
    - Clear unsupported parameters for current chunk scope
    """
```

**Parameter Handling**:
- **Faceting parameters**: `rows`, `cols`, `lines`, `row_order`, `col_order`, `lines_order`
- **Coordinate parameters**: `x`, `y` (required for plotting)
- **Plot parameters**: Everything else passes through to `plot()` method
- **Scope filtering**: Remove unsupported parameters (targeting, nested lists) with warnings

### Task 6: Add Basic State Management

**File**: `src/dr_plotter/figure.py`

Extend grid state management for plotting integration:

```python
def _store_faceting_state(self, config: FacetingConfig, layout_metadata: Dict[str, Any]) -> None:
    """
    Store faceting state for potential future faceting calls on same figure.
    
    Stores:
    - Grid layout information
    - Dimension mappings  
    - Configuration used
    - Plot type and parameters (for style coordination in future chunks)
    """
```

This prepares for advanced features in later chunks while keeping current implementation simple.

### Task 7: Write Comprehensive Integration Tests

**File**: `tests/test_faceting_integration.py` (create new file)

Write end-to-end integration tests:

**Basic Integration Tests**:
```python
class TestBasicFacetedPlotting:
    def test_simple_line_plots_explicit_grid(self):
        # Test basic 2x2 grid with line plots
        
    def test_scatter_plots_with_hue_by_lines(self):
        # Test that lines parameter maps to hue_by correctly
        
    def test_different_plot_types(self):
        # Test line, scatter, bar plots work
        
    def test_missing_data_combinations_handled(self):
        # Test grid positions with no data are skipped gracefully

class TestParameterResolution:
    def test_direct_params_override_config(self):
        # Test parameter precedence logic
        
    def test_plot_kwargs_passed_through(self):
        # Test additional parameters reach plot() method

class TestDataPreparation:
    def test_data_subsetting_correctness(self):
        # Test each subplot gets correct data subset
        
    def test_empty_subsets_handled(self):
        # Test missing combinations don't break plotting

class TestValidation:
    def test_missing_columns_error_messages(self):
        # Test helpful error messages for missing columns
        
    def test_unsupported_features_warnings(self):
        # Test warnings for features not yet implemented

class TestRealWorldScenarios:
    def test_ml_training_data_pattern(self):
        # Test with realistic ML evaluation data structure
        
    def test_ordering_applied_correctly(self):
        # Test row_order/col_order affect subplot layout
```

**Integration with Existing Examples**:
```python
class TestExampleCompatibility:
    def test_simplify_existing_faceted_example(self):
        # Take current 06_faceted_training_curves.py logic
        # Show how new API reduces it significantly
        # Verify same output is produced
```

### Task 8: Execute and Verify All Tests

**CRITICAL**: You must actually run the tests and verify results.

**Run New Integration Tests**:
```bash
pytest tests/test_faceting_integration.py -v
```

**Run All Faceting Tests**:
```bash
pytest tests/test_faceting*.py -v
```

**Run Full Test Suite**:
```bash
pytest tests/ -x  # Stop on first failure
```

**Verify Results**:
- All new integration tests pass
- All previous faceting tests continue to pass  
- All existing dr_plotter tests continue to pass
- No warnings or deprecation messages
- Test execution time reasonable (<30 seconds total)

### Task 9: Create Working Example

**File**: `tests/test_working_faceted_example.py` (create new file)

Create a working demonstration:

```python
def test_working_faceted_example():
    """
    Demonstrate working faceted plotting with realistic data.
    
    This test serves as both validation and documentation of current capabilities.
    """
    # Create realistic ML training data
    data = create_ml_training_data()  # Helper function
    
    # Create faceted plot using new API
    with FigureManager(figure=FigureConfig(rows=2, cols=3, figsize=(15, 8))) as fm:
        fm.plot_faceted(
            data=data,
            plot_type="line",
            rows="metric",        # 2 metrics: loss, accuracy  
            cols="dataset",       # 3 datasets: train, val, test
            lines="model_size",   # 3 model sizes: small, medium, large
            x="epoch",
            y="value"
        )
        
        # Verify this produces the expected 2x3 grid
        # Each subplot should show 3 lines (one per model size)
        # Should be much simpler than current 95+ line examples
        
        # Save plot for manual inspection
        plt.savefig("tests/outputs/chunk_3_working_example.png")
```

## Success Criteria

Before marking this chunk complete, verify ALL of these:

- [ ] **End-to-end working faceted plots**: Simple explicit grid layouts produce correct visualizations
- [ ] **Data subsetting correctness**: Each subplot contains exactly the right data subset
- [ ] **Integration with existing plot methods**: All plot types work (line, scatter, bar, etc.)
- [ ] **Parameter resolution logic**: Direct parameters override config parameters correctly
- [ ] **Missing data handling**: Empty subplots don't cause errors or break plotting
- [ ] **Coordinate parameter handling**: `x`, `y` parameters work correctly
- [ ] **Lines mapping**: `lines` parameter correctly maps to `hue_by` for series differentiation
- [ ] **Plot parameter pass-through**: Additional kwargs reach underlying plot() method
- [ ] **Scope limitations respected**: Unsupported features properly ignored/warned about
- [ ] **All new tests pass when executed**
- [ ] **All existing tests continue to pass**
- [ ] **Working example demonstrates significant simplification** over current manual approach
- [ ] **Code follows dr_plotter standards** (all imports at top, no comments, assertions over exceptions)

## Implementation Notes

### Code Quality Requirements
- **All imports at file top**: No mid-function imports (lesson from Chunk 2)
- **No comments**: Code must be self-documenting
- **Complete type hints**: Every parameter and return value typed
- **Assertions for validation**: Use `assert condition, "message"` format
- **Error message quality**: Include current values and helpful suggestions

### Data Handling Standards
- Always use `.copy()` when subsetting DataFrames
- Handle missing combinations gracefully
- Preserve column data types
- Use exact value matching for filtering

### Integration Requirements
- Build on Chunk 2 grid computation without modification
- Use existing `plot()` method without changes
- Maintain compatibility with all existing functionality
- Store state for future chunk integration

### Scope Management (Critical)
- **Only implement explicit grids** - no wrapped layouts yet
- **Ignore targeting parameters** - implement in Chunk 4
- **Skip nested list parameters** - implement in Chunk 4  
- **Use default styling** - advanced styling in Chunk 5
- **Warn about unsupported features** rather than erroring

### Testing Strategy
- Test basic functionality first (2×2 grids, simple data)
- Test integration with different plot types
- Test edge cases (missing data, empty subsets)
- Create realistic working example for validation
- Verify significant reduction in boilerplate vs current approach

### Common Pitfalls to Avoid
- Don't try to implement advanced features yet (stay in scope)
- Don't modify Chunk 2 grid computation methods
- Don't break existing non-faceted plotting functionality
- Don't assume data is clean - validate and handle edge cases
- Don't hardcode plot parameters - pass everything through

## Documentation Requirements

When you complete this chunk, update the implementation plan:

**File**: `docs/plans/faceted_plotting_implementation_plan.md`

In the "Chunk 3 Notes" section, document:
- **Test execution results**: Specific pass/fail counts and any issues
- **Integration discoveries**: How well existing plot() method integration worked
- **Data handling insights**: Edge cases found with real-world data patterns
- **Performance observations**: How end-to-end faceted plotting performs  
- **Simplification achieved**: Comparison of new API vs current manual approach
- **Scope management lessons**: What was successfully deferred vs what needed implementation
- **Recommendations for Chunk 4**: What advanced layout features will need based on basic integration learnings

## Next Steps

After completing this chunk successfully:
1. **Execute all tests** and verify comprehensive pass results
2. **Manually test working example** to verify visual output correctness
3. Update progress checkboxes in implementation plan  
4. Document learnings and integration insights
5. Ready for code review before proceeding to Chunk 4 (Advanced Layout Features)

This chunk represents the first major milestone - working end-to-end faceted plotting! Focus on correctness and solid integration with existing infrastructure rather than feature completeness. Chunks 4-6 will add the advanced features on top of this solid foundation.
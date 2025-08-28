# Faceted Plotting Implementation: Chunk 2 - Grid Computation Engine

## Project Context

You are implementing **Chunk 2 of 6** for native faceting support in dr_plotter. This chunk builds the core grid layout computation engine that determines subplot layouts and targeting.

**Your role**: Implement the mathematical and logical foundation for all faceting operations - no plotting yet, just pure grid computation and validation.

**Foundation**: Chunk 1 completed successfully with `FacetingConfig` available and tested.

## Key References

**MANDATORY**: Before starting, read these docs to understand the project:
- `docs/DESIGN_PHILOSOPHY.md` - Core principles and coding standards
- `docs/plans/faceted_plotting_detailed_design.md` - Complete technical architecture 
- `docs/plans/faceted_plotting_implementation_plan.md` - Your place in the overall plan and Chunk 1 learnings

## Your Tasks

### Task 1: Implement Grid Computation Logic

**File**: `src/dr_plotter/figure.py`

Add `_compute_facet_grid()` method to `FigureManager` class. This is the core mathematical engine for all grid layouts:

```python
def _compute_facet_grid(self, data: pd.DataFrame, config: FacetingConfig) -> Tuple[int, int, Dict[str, Any]]:
    """
    Compute grid dimensions and layout metadata from data and configuration.
    
    Returns:
        Tuple of (n_rows, n_cols, layout_metadata)
        
    Layout metadata includes:
        - row_values: ordered unique values for row dimension
        - col_values: ordered unique values for col dimension  
        - grid_type: "explicit", "wrapped_rows", "wrapped_cols"
        - fill_order: list of (row_idx, col_idx) positions in fill order
    """
```

**Required Logic**:

1. **Explicit Grid Layout** (`config.rows` AND `config.cols` specified):
   - Extract unique values from data columns
   - Apply ordering from `config.row_order` and `config.col_order` if specified
   - Compute dimensions: `n_rows = len(row_values)`, `n_cols = len(col_values)`

2. **Wrapped Rows Layout** (`config.rows` specified, `config.ncols` specified):
   - Extract unique values from `config.rows` column
   - Apply ordering from `config.row_order` if specified
   - Compute dimensions: `n_cols = config.ncols`, `n_rows = ceil(len(row_values) / config.ncols)`
   - Generate fill order: row-major wrapping

3. **Wrapped Cols Layout** (`config.cols` specified, `config.nrows` specified):
   - Extract unique values from `config.cols` column
   - Apply ordering from `config.col_order` if specified  
   - Compute dimensions: `n_rows = config.nrows`, `n_cols = ceil(len(col_values) / config.nrows)`
   - Generate fill order: column-major wrapping

**Data Validation**:
- Assert required columns exist in DataFrame
- Assert row/col values exist in data
- Handle empty data gracefully with clear error messages

### Task 2: Implement Targeting Resolution

**File**: `src/dr_plotter/figure.py`

Add `_resolve_targeting()` method to determine which subplot positions to target:

```python
def _resolve_targeting(self, config: FacetingConfig, grid_rows: int, grid_cols: int) -> List[Tuple[int, int]]:
    """
    Resolve targeting configuration to specific (row, col) position list.
    
    Returns:
        List of (row_idx, col_idx) tuples to target for plotting
    """
```

**Required Logic**:

1. **No targeting specified**: Return all positions in grid
2. **Single targets** (`target_row`, `target_col`):
   - `target_row` only: All positions in that row
   - `target_col` only: All positions in that column
   - Both specified: Single position `(target_row, target_col)`
3. **Multiple targets** (`target_rows`, `target_cols`):
   - `target_rows` only: All positions in those rows
   - `target_cols` only: All positions in those columns  
   - Both specified: Cartesian product of specified rows and columns

**Validation**:
- Assert target indices are within grid bounds
- Assert no conflicts between single and multiple targeting
- Provide helpful error messages with valid ranges

### Task 3: Add Grid Validation and Management

**File**: `src/dr_plotter/figure.py`

Add grid state management to `FigureManager`:

```python
def __init__(self, ...):
    # ... existing init logic ...
    self._facet_grid_info: Optional[Dict[str, Any]] = None

def _validate_facet_grid_against_existing(self, new_rows: int, new_cols: int) -> None:
    """
    Validate computed grid against existing FigureManager state.
    
    Rules:
    - If no existing plots: grid can be set freely
    - If existing plots: new grid must match current dimensions
    - If existing facet grid: new grid must be compatible
    """

def _set_facet_grid_info(self, grid_info: Dict[str, Any]) -> None:
    """Store grid information for future faceting calls."""
    
def _has_existing_plots(self) -> bool:
    """Check if FigureManager has any existing plots."""
```

**Implementation Notes**:
- Check existing `self.fig.axes` to detect existing plots
- Store grid metadata for style coordination in later chunks
- Validate against current `FigureConfig` dimensions if set

### Task 4: Add Data Dimension Analysis

**File**: `src/dr_plotter/figure.py`  

Add helper method for analyzing data dimensions:

```python
def _analyze_data_dimensions(self, data: pd.DataFrame, config: FacetingConfig) -> Dict[str, List[str]]:
    """
    Analyze data to extract dimension values and validate against configuration.
    
    Returns:
        Dictionary with keys: 'rows', 'cols', 'lines' containing ordered unique values
    """
```

**Required Logic**:
- Extract unique values for each specified dimension column
- Apply ordering from `*_order` parameters if provided
- Validate that ordered values exist in data
- Handle missing dimension columns with clear errors

### Task 5: Integration Stub for FigureManager

**File**: `src/dr_plotter/figure.py`

Add placeholder method that will be implemented in Chunk 3:

```python
def plot_faceted(self, data: pd.DataFrame, plot_type: str, 
                faceting: Optional['FacetingConfig'] = None, **kwargs) -> None:
    """
    Create faceted plots across subplot grid.
    
    This is a STUB implementation for Chunk 2 - only validates inputs
    and computes grid without plotting.
    """
    from dr_plotter.faceting_config import FacetingConfig
    
    # Import validation
    assert isinstance(data, pd.DataFrame), f"data must be DataFrame, got {type(data)}"
    assert isinstance(plot_type, str), f"plot_type must be string, got {type(plot_type)}"
    
    # Grid computation (your implemented methods)
    config = self._resolve_faceting_config(faceting, **kwargs) 
    grid_rows, grid_cols, layout_metadata = self._compute_facet_grid(data, config)
    target_positions = self._resolve_targeting(config, grid_rows, grid_cols)
    
    # Store results for testing
    self._debug_grid_info = {
        'config': config,
        'grid_dimensions': (grid_rows, grid_cols),
        'layout_metadata': layout_metadata,
        'target_positions': target_positions
    }
    
    print(f"Grid computed: {grid_rows}×{grid_cols}, targeting {len(target_positions)} positions")

def _resolve_faceting_config(self, faceting: Optional['FacetingConfig'], **kwargs) -> 'FacetingConfig':
    """Merge faceting config with direct parameters (from detailed design)."""
    from dr_plotter.faceting_config import FacetingConfig
    
    if faceting is None:
        return FacetingConfig(**kwargs)
    
    # Direct params override config values
    config_dict = {k: v for k, v in faceting.__dict__.items()}
    for key, value in kwargs.items():
        if hasattr(FacetingConfig, key) and value is not None:
            config_dict[key] = value
    
    return FacetingConfig(**config_dict)
```

### Task 6: Write Comprehensive Tests

**File**: `tests/test_faceting_grid_computation.py` (create new file)

Write unit tests covering all grid computation logic:

**Grid Computation Tests**:
```python
class TestGridComputation:
    def test_explicit_grid_layout(self):
        # Test rows + cols specified
        
    def test_wrapped_rows_layout(self):
        # Test rows + ncols specified
        
    def test_wrapped_cols_layout(self):
        # Test cols + nrows specified
        
    def test_ordering_applied_correctly(self):
        # Test row_order/col_order parameters
        
    def test_missing_data_columns_error(self):
        # Test validation of required columns

class TestTargetingResolution:
    def test_no_targeting_returns_all_positions(self):
        # Test default behavior
        
    def test_single_row_targeting(self):
        # Test target_row parameter
        
    def test_multiple_targeting_combinations(self):
        # Test target_rows, target_cols combinations
        
    def test_targeting_validation_errors(self):
        # Test out-of-bounds targeting

class TestGridValidation:
    def test_grid_compatible_with_existing_plots(self):
        # Test validation against existing state
        
    def test_grid_state_management(self):
        # Test _facet_grid_info storage

class TestDataDimensionAnalysis:
    def test_dimension_extraction_and_ordering(self):
        # Test _analyze_data_dimensions method
        
class TestFacetedPlotStub:
    def test_parameter_resolution_override_logic(self):
        # Test direct params override config
        
    def test_end_to_end_grid_computation_no_plotting(self):
        # Test full pipeline without plotting
```

**Test Data Requirements**:
- Create realistic test DataFrames mimicking ML training data structure
- Include edge cases: empty data, single values, missing combinations
- Test with various data types and column names

### Task 7: Execute and Verify All Tests

**CRITICAL**: You must actually run the tests, not just write them.

**Run New Tests**:
```bash
pytest tests/test_faceting_grid_computation.py -v
```

**Run Existing Test Suite**:
```bash
pytest tests/ -x  # Stop on first failure to catch regressions
```

**Verify Results**:
- All new tests pass with clear output
- All existing tests continue to pass
- No warnings or deprecation messages
- Test coverage is comprehensive

**Report Results**: Document test execution results in implementation plan notes.

## Success Criteria

Before marking this chunk complete, verify ALL of these:

- [ ] `_compute_facet_grid()` correctly handles all three layout modes (explicit, wrapped rows, wrapped cols)
- [ ] `_resolve_targeting()` resolves all targeting parameter combinations correctly
- [ ] Grid validation prevents conflicts with existing plots and manages state properly
- [ ] Data dimension analysis extracts and orders values correctly with clear error messages
- [ ] `plot_faceted()` stub validates inputs and demonstrates full grid computation pipeline
- [ ] Parameter resolution logic (direct params override config) works correctly
- [ ] **All new tests pass when executed** 
- [ ] **All existing tests continue to pass**
- [ ] Code follows dr_plotter standards (no comments, assertions over exceptions, complete type hints)
- [ ] Grid computation works with realistic test data resembling ML training scenarios

## Implementation Notes

### Mathematical Requirements
- Use `math.ceil()` for wrapped layout dimension calculations
- Handle edge cases: empty data, single values, exact grid fits
- Ensure consistent ordering across all operations

### Data Handling Standards  
- Always work with pandas DataFrame copies to avoid mutations
- Validate column existence before accessing
- Provide helpful error messages listing available columns

### State Management
- Store grid information for use by future chunks
- Don't mutate FigureManager state unnecessarily
- Validate against existing subplot configurations

### Testing Strategy
- Test happy path scenarios first (explicit grids with clean data)
- Test each layout mode independently
- Test validation and error conditions thoroughly
- Use realistic data that matches actual use cases

### Common Pitfalls to Avoid
- Don't implement any actual plotting logic (that's Chunk 3)
- Don't assume data is clean - validate everything
- Don't hardcode grid dimensions - compute from data
- Don't ignore edge cases in wrapped layouts (uneven fills)

## Documentation Requirements

When you complete this chunk, update the implementation plan:

**File**: `docs/plans/faceted_plotting_implementation_plan.md`

In the "Chunk 2 Notes" section, document:
- **Test execution results**: Pass/fail counts, any issues encountered
- **Mathematical edge cases discovered**: How wrapped layouts handle uneven fills
- **Data validation insights**: What validation catches real-world issues  
- **Performance observations**: How grid computation scales with data size
- **Integration discoveries**: Any interactions with existing FigureManager functionality
- **Recommendations for Chunk 3**: What grid computation reveals about data preparation needs

## Next Steps

After completing this chunk successfully:
1. **Execute all tests** and verify they pass
2. Update progress checkboxes in implementation plan
3. Document learnings and test results
4. Ready for code review before proceeding to Chunk 3 (Basic Plot Integration)

This chunk provides the mathematical foundation for all faceting operations. Focus on correctness, edge case handling, and comprehensive testing - Chunk 3 will build the plotting logic on top of your grid computation engine.
# Faceted Plotting Implementation: Chunk 3.5 - Code Organization Refactoring

## Project Context

You are implementing **Chunk 3.5** - a focused refactoring to improve code organization before adding advanced features in Chunks 4-6.

**Your role**: Extract pure functions from `figure.py` into well-organized modules without changing any functionality or breaking any tests.

**Foundation**: Chunk 3 completed successfully with working end-to-end faceted plotting (14/14 tests passing, 73/73 total tests passing).

## Key References

**MANDATORY**: Before starting, read these docs:
- `docs/DESIGN_PHILOSOPHY.md` - Core principles and coding standards
- `docs/plans/faceted_plotting_detailed_design.md` - Complete technical architecture 
- `docs/plans/faceted_plotting_implementation_plan.md` - Chunk 3 implementation notes and patterns

## Problem Statement

Based on Chunk 3 completion, `figure.py` now contains:
- Grid computation logic (`_compute_facet_grid()`, `_resolve_targeting()`)
- Data analysis and preparation (`_analyze_data_dimensions()`, `_prepare_facet_data()`)
- Validation helpers (`_validate_faceting_inputs()` components)
- Parameter resolution (`_resolve_faceting_config()` logic)
- Plot orchestration (`_execute_faceted_plotting()`)

**Issue**: FigureManager is becoming a "god class" with too many responsibilities, making testing harder and code discovery difficult.

**Solution**: Extract pure functions (those not using `self`) into focused modules.

## Your Tasks

### Task 1: Create Faceting Module Structure

**Create new directory**: `src/dr_plotter/faceting/`

**Files to create**:
```
src/dr_plotter/faceting/
├── __init__.py           # Public API exports
├── grid_computation.py   # Grid layout algorithms and targeting
├── data_analysis.py      # Data dimension analysis and validation
├── data_preparation.py   # Data subsetting and filtering logic
├── validation.py         # Input validation helpers
└── types.py             # Common types and data structures
```

### Task 2: Extract Grid Computation Logic

**File**: `src/dr_plotter/faceting/grid_computation.py`

Extract pure mathematical functions from `_compute_facet_grid()` and `_resolve_targeting()`:

```python
from typing import Dict, List, Tuple, Any
import pandas as pd
from dr_plotter.faceting_config import FacetingConfig

def compute_grid_dimensions(data: pd.DataFrame, config: FacetingConfig) -> Tuple[int, int]:
    """
    Pure function to compute grid dimensions from data and configuration.
    
    Extracted from FigureManager._compute_facet_grid()
    """
    
def compute_grid_layout_metadata(data: pd.DataFrame, config: FacetingConfig) -> Dict[str, Any]:
    """
    Pure function to compute layout metadata (row_values, col_values, etc.).
    
    Extracted from FigureManager._compute_facet_grid()
    """

def resolve_target_positions(config: FacetingConfig, grid_rows: int, grid_cols: int) -> List[Tuple[int, int]]:
    """
    Pure function for targeting resolution.
    
    Extracted from FigureManager._resolve_targeting()
    """
```

**Extraction Strategy**:
- Identify code that only uses parameters (data, config) and returns computed values
- Leave FigureManager state management and validation in original methods
- Extract mathematical/algorithmic logic only

### Task 3: Extract Data Analysis Functions

**File**: `src/dr_plotter/faceting/data_analysis.py`

Extract pure data analysis functions:

```python
from typing import Dict, List
import pandas as pd
from dr_plotter.faceting_config import FacetingConfig

def extract_dimension_values(data: pd.DataFrame, column: str, order: List[str] = None) -> List[str]:
    """
    Extract and order unique values from a DataFrame column.
    
    Extracted from dimension analysis logic in various methods.
    """

def analyze_data_dimensions(data: pd.DataFrame, config: FacetingConfig) -> Dict[str, List[str]]:
    """
    Analyze data to extract dimension values for all specified dimensions.
    
    Extracted from FigureManager._analyze_data_dimensions()
    """

def detect_missing_combinations(data: pd.DataFrame, row_values: List[str], 
                               col_values: List[str], row_col: str, col_col: str) -> List[Tuple[str, str]]:
    """
    Detect missing row/column combinations in the data.
    
    Pure function for missing data analysis.
    """
```

### Task 4: Extract Data Preparation Logic

**File**: `src/dr_plotter/faceting/data_preparation.py`

Extract core data subsetting logic:

```python
from typing import Dict, List, Tuple
import pandas as pd

def create_data_subset(data: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    """
    Create DataFrame subset based on column value filters.
    
    Pure function extracted from _prepare_facet_data() core logic.
    """

def prepare_subplot_data_subsets(data: pd.DataFrame, row_values: List[str], col_values: List[str],
                                row_col: str, col_col: str) -> Dict[Tuple[int, int], pd.DataFrame]:
    """
    Prepare data subsets for each subplot position.
    
    Extracted from FigureManager._prepare_facet_data() core logic.
    """
```

### Task 5: Extract Validation Helpers

**File**: `src/dr_plotter/faceting/validation.py`

Extract pure validation functions:

```python
from typing import List, Optional
import pandas as pd
from dr_plotter.faceting_config import FacetingConfig

def validate_required_columns(data: pd.DataFrame, required_columns: List[str]) -> None:
    """
    Validate that required columns exist in DataFrame.
    
    Extracted from _validate_faceting_inputs() logic.
    """

def validate_dimension_values(data: pd.DataFrame, column: str, expected_values: Optional[List[str]] = None) -> None:
    """
    Validate dimension column values against expectations.
    
    Extracted from validation logic.
    """

def get_available_columns_message(data: pd.DataFrame, missing_columns: List[str]) -> str:
    """
    Generate helpful error message for missing columns.
    
    Pure function for error message generation.
    """
```

### Task 6: Create Common Types

**File**: `src/dr_plotter/faceting/types.py`

Define shared data structures:

```python
from typing import Dict, List, Tuple, Any, NamedTuple

class GridLayout(NamedTuple):
    """Grid layout information"""
    rows: int
    cols: int  
    row_values: List[str]
    col_values: List[str]
    grid_type: str
    metadata: Dict[str, Any]

type SubplotPosition = Tuple[int, int]
type DataSubsets = Dict[SubplotPosition, pd.DataFrame]
```

### Task 7: Set Up Module Exports

**File**: `src/dr_plotter/faceting/__init__.py`

```python
from .grid_computation import (
    compute_grid_dimensions,
    compute_grid_layout_metadata, 
    resolve_target_positions,
)
from .data_analysis import (
    extract_dimension_values,
    analyze_data_dimensions,
    detect_missing_combinations,
)
from .data_preparation import (
    create_data_subset,
    prepare_subplot_data_subsets,
)
from .validation import (
    validate_required_columns,
    validate_dimension_values,
    get_available_columns_message,
)
from .types import GridLayout, SubplotPosition, DataSubsets

__all__ = [
    # Grid computation
    "compute_grid_dimensions", 
    "compute_grid_layout_metadata",
    "resolve_target_positions",
    # Data analysis  
    "extract_dimension_values",
    "analyze_data_dimensions", 
    "detect_missing_combinations",
    # Data preparation
    "create_data_subset",
    "prepare_subplot_data_subsets", 
    # Validation
    "validate_required_columns",
    "validate_dimension_values",
    "get_available_columns_message",
    # Types
    "GridLayout", "SubplotPosition", "DataSubsets",
]
```

### Task 8: Update FigureManager to Use New Modules

**File**: `src/dr_plotter/figure.py`

Update imports and method implementations:

```python
from dr_plotter.faceting import (
    compute_grid_dimensions,
    compute_grid_layout_metadata,
    resolve_target_positions,
    analyze_data_dimensions, 
    prepare_subplot_data_subsets,
    validate_required_columns,
    GridLayout,
    DataSubsets,
)

class FigureManager:
    def _compute_facet_grid(self, data: pd.DataFrame, config: FacetingConfig) -> GridLayout:
        """
        Orchestration method - now uses extracted functions.
        
        Handles:
        - FigureManager state validation  
        - Grid info storage
        - Integration with FigureConfig
        
        Delegates pure computation to extracted functions.
        """
        # Use: compute_grid_dimensions(), compute_grid_layout_metadata()
        # Keep: state management, validation integration, grid info storage
        
    def _prepare_facet_data(self, data: pd.DataFrame, config: FacetingConfig, 
                           layout: GridLayout) -> DataSubsets:
        """
        Orchestration method - now uses extracted functions.
        
        Handles:
        - Integration with FigureManager state
        - Error handling and logging
        
        Delegates pure data preparation to extracted functions.
        """
        # Use: prepare_subplot_data_subsets()
        # Keep: state integration, error handling
```

**Refactoring Principles**:
- **Pure functions go to modules**: No `self` dependency, just computation
- **Orchestration stays in FigureManager**: State management, integration, validation
- **Same interfaces**: Method signatures remain unchanged
- **Same behavior**: All existing functionality preserved exactly

### Task 9: Create Module-Level Tests

**Files**: `tests/faceting/` (create new directory)

Create focused tests for each module:

```
tests/faceting/
├── test_grid_computation.py     # Test pure grid computation functions
├── test_data_analysis.py        # Test data analysis functions  
├── test_data_preparation.py     # Test data preparation functions
├── test_validation.py           # Test validation helpers
└── test_integration.py          # Test module integration
```

**Testing Strategy**:
- **Unit tests for pure functions**: Much easier to test isolated functions
- **Integration tests**: Verify FigureManager still works correctly
- **Existing tests unchanged**: All current tests should pass without modification

### Task 10: Execute and Verify All Tests

**CRITICAL**: You must verify that refactoring doesn't break anything.

**Run Module Tests**:
```bash
pytest tests/faceting/ -v
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
- All new module tests pass
- All existing faceting tests (73/73) continue to pass
- All other dr_plotter tests continue to pass
- No performance regressions
- Import paths all work correctly

## Success Criteria

Before marking this refactoring complete, verify ALL of these:

- [ ] **All extracted functions are pure** - no `self` dependencies, just computation
- [ ] **FigureManager methods preserved** - same signatures and behavior as before refactoring
- [ ] **All existing tests pass** - 73/73 faceting tests + all other dr_plotter tests
- [ ] **New module tests comprehensive** - good coverage of extracted functions
- [ ] **Import structure clean** - clear, logical imports in `__init__.py`
- [ ] **Code organization improved** - related functionality grouped logically
- [ ] **Documentation updated** - type hints and docstrings maintained
- [ ] **No performance regressions** - refactoring doesn't slow down existing functionality
- [ ] **File structure logical** - clear separation between computation, analysis, preparation, validation

## Implementation Notes

### Extraction Principles
- **Pure functions only**: If it uses `self`, it stays in FigureManager
- **Preserve interfaces**: FigureManager method signatures unchanged  
- **Same behavior**: No functional changes, only organizational
- **Clear boundaries**: Computation vs orchestration vs state management

### Code Quality Requirements
- **All imports at top**: No mid-function imports anywhere
- **Complete type hints**: Every extracted function fully typed
- **No comments**: Self-documenting code through clear names
- **Assertions for validation**: Use existing patterns

### Testing Strategy
- **Test pure functions independently**: Much easier than testing through FigureManager
- **Verify integration**: FigureManager orchestration still works
- **No test changes**: Existing integration tests should pass unchanged
- **Performance verification**: No measurable slowdown

### Common Pitfalls to Avoid
- **Don't change functionality**: Only move code, don't modify logic
- **Don't break imports**: Ensure all import paths work correctly
- **Don't extract too much**: Leave orchestration and state management in FigureManager
- **Don't skip testing**: Verify every extracted function works correctly

## Documentation Requirements

When you complete this chunk, update the implementation plan:

**File**: `docs/plans/faceted_plotting_implementation_plan.md`

Add new section "Chunk 3.5 Notes" with:
- **Refactoring results**: What functions were extracted to which modules
- **Test execution results**: Pass/fail counts for new module tests
- **Code organization improvements**: How the new structure improves maintainability
- **Integration validation**: Confirmation that all existing functionality preserved
- **Performance observations**: Any changes in execution speed or memory usage
- **Recommendations for Chunks 4-6**: How new structure simplifies future development

## Next Steps

After completing this refactoring successfully:
1. **Execute all tests** and verify no regressions
2. Update progress in implementation plan
3. Update Chunk 4 prompt to use new module structure
4. Ready for advanced layout features with cleaner foundation

This refactoring creates a much better foundation for the remaining chunks while preserving all working functionality from Chunk 3.
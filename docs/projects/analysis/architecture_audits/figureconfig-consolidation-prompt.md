# FigureConfig Consolidation & Example Update: SubplotLayoutConfig Elimination

## Your Mission
You are implementing the consolidation of SubplotLayoutConfig into FigureConfig and updating all examples to use the simplified architecture. This eliminates artificial parameter separation and creates a cleaner user interface.

## Context
Based on our architectural audits, we determined that SubplotLayoutConfig and FigureConfig have artificial separation. Users think: *"I want to set up my figure with 2 rows, 4 columns, this size"* - not separate "layout" vs "figure" concerns.

**Current Architecture** (artificial separation):
```python
FigureManager(
    layout=SubplotLayoutConfig(rows=2, cols=4, layout_pad=0.3),
    figure=FigureConfig(figsize=(16, 9), subplot_kwargs={'sharey': 'row'})
)
```

**Target Architecture** (consolidated):
```python
FigureManager(
    figure=FigureConfig(
        rows=2, cols=4, layout_pad=0.3, figsize=(16, 9),
        subplot_kwargs={'sharey': 'row'}
    )
)
```

## Your Systematic Implementation

### 1. Create Consolidated FigureConfig Class
**Location**: `src/dr_plotter/figure_config.py`

**Consolidate into single FigureConfig**:
```python
@dataclass
class FigureConfig:
    # Explicit for usability (most common parameters)
    rows: int = 1
    cols: int = 1  
    figsize: Tuple[int, int] = (12, 8)
    
    # Explicit for non-matplotlib function parameters  
    tight_layout_pad: float = 0.5  # → plt.tight_layout(pad=...)
    
    # Integration parameters
    external_ax: Optional[plt.Axes] = None
    shared_styling: Optional[bool] = None
    
    # Direct matplotlib function parameters (kwargs only)  
    figure_kwargs: Dict[str, Any] = field(default_factory=dict)    # → plt.figure()
    subplot_kwargs: Dict[str, Any] = field(default_factory=dict)   # → plt.subplots()
    
    def validate(self) -> None:
        # Add validation for rows > 0, cols > 0, figsize valid, etc.
        pass
```

**Key Changes**:
- **Move from SubplotLayoutConfig**: `rows`, `cols`, `layout_pad` (rename to `tight_layout_pad`)
- **Keep from existing FigureConfig**: `figsize`, `external_ax`, `shared_styling`, kwargs
- **Remove**: `layout_rect` parameter (was matplotlib direct param - goes in `subplot_kwargs` if needed)

### 2. Remove SubplotLayoutConfig Class
**Delete entirely**: The `SubplotLayoutConfig` class and any related imports/references.

### 3. Update FigureManager Constructor
**Location**: `src/dr_plotter/figure.py`

**Current signature**:
```python
def __init__(
    self,
    layout: Optional[SubplotLayoutConfig] = None,
    legend: Optional[LegendConfig] = None,
    figure: Optional[FigureConfig] = None,
    theme: Optional[Any] = None,
    faceting: Optional[SubplotFacetingConfig] = None,
) -> None:
```

**Target signature**:
```python
def __init__(
    self,
    figure: Optional[FigureConfig] = None,
    legend: Optional[LegendConfig] = None, 
    theme: Optional[Any] = None,
    faceting: Optional[SubplotFacetingConfig] = None,
) -> None:
```

**Update constructor logic**:
- Remove all `layout` parameter handling
- Get `rows`, `cols`, `tight_layout_pad` from `figure` config
- Update `plt.subplots()` call to use `figure.rows`, `figure.cols`
- Update `tight_layout()` calls to use `figure.tight_layout_pad`

### 4. Update create_figure_manager() Factory
**Location**: `src/dr_plotter/figure_config.py`

**Current signature**:
```python
def create_figure_manager(
    layout: Optional[SubplotLayoutConfig] = None,
    legend: Optional[LegendConfig] = None,
    coordination: Optional[FigureCoordinationConfig] = None,
    faceting: Optional[SubplotFacetingConfig] = None,
) -> "FigureManager":
```

**Target signature** (if this factory still exists):
```python
def create_figure_manager(
    figure: Optional[FigureConfig] = None,
    legend: Optional[LegendConfig] = None,
    theme: Optional[Any] = None,
    faceting: Optional[SubplotFacetingConfig] = None,
) -> "FigureManager":
```

### 5. Update All Examples to Consolidated Architecture
**Target examples**: All files in `examples/` directory

**For each example using FigureManager**:

**Before**:
```python
fm = FigureManager(
    rows=2, 
    cols=num_recipes, 
    figsize=(figwidth, 9),
    legend_strategy="figure_below",
    legend_ncol=min(num_model_sizes, 8),
    plot_margin_bottom=0.12,
    tight_layout_pad=0.3,
    sharey="row"
)
```

**After**:
```python
fm = FigureManager(
    figure=FigureConfig(
        rows=2,
        cols=num_recipes, 
        figsize=(figwidth, 9),
        tight_layout_pad=0.3,
        subplot_kwargs={'sharey': 'row'}
    ),
    legend=LegendConfig(
        strategy=LegendStrategy.FIGURE_BELOW,
        ncol=min(num_model_sizes, 8),
        layout_bottom_margin=0.12
    )
)
```

**Update patterns to look for**:
- Individual `rows`, `cols` parameters → `figure=FigureConfig(rows=..., cols=...)`
- Individual `figsize` parameters → `figure.figsize`
- Individual `layout_pad` parameters → `figure.tight_layout_pad`
- Matplotlib parameters → `figure.subplot_kwargs` or `figure.figure_kwargs`

## Code Requirements

**CRITICAL - Follow Project Standards**:
1. **No comments or docstrings anywhere** - code must be self-documenting
2. **Comprehensive type hints** on ALL functions and methods
3. **All imports at the very top** of files - never in middle
4. **Use assertions for validation**: `assert condition, "message"` instead of exceptions
5. **Remove any existing comments** when editing files

## Validation Requirements

**Test consolidated architecture works**:
1. **Examples run successfully** with new consolidated FigureConfig
2. **Visual output identical** to previous version
3. **All functionality preserved** - margins, spacing, subplot coordination
4. **Cleaner user interface** - fewer config objects needed

**Specific validation**:
- `examples/06_faceted_training_curves.py` works with consolidated FigureConfig
- Subplot grid creation works (rows, cols from figure config)
- tight_layout spacing works (tight_layout_pad from figure config) 
- Legend positioning works (should be unaffected)
- Matplotlib parameter passing works (subplot_kwargs routing)

## Expected Benefits

**User Experience**:
- **Fewer config objects** - single FigureConfig instead of separate layout + figure
- **Natural parameter grouping** - all figure setup in one place
- **Consistent mental model** - "configure my figure" not "configure layout + figure"

**Code Quality**:
- **Eliminated artificial separation** - no arbitrary boundary between layout and figure
- **Cleaner constructor** - fewer parameters, clearer organization
- **Simplified examples** - less boilerplate configuration

## Success Criteria
- ✅ SubplotLayoutConfig class completely removed from codebase
- ✅ Consolidated FigureConfig with rows, cols, figsize, tight_layout_pad
- ✅ FigureManager constructor takes only figure config (no separate layout)
- ✅ All examples updated to use consolidated architecture
- ✅ All functionality preserved - visual outputs identical
- ✅ Cleaner user interface demonstrated through simplified example code

## Strategic Impact
This consolidation eliminates artificial architectural complexity and provides a cleaner foundation for any future parameter routing enhancements (axes_kwargs, plotter_kwargs). The simpler architecture will make it easier to assess what additional parameter routing is actually needed vs what was just architectural over-engineering.
# Phase 2 Step 2 Agent Prompt: Legacy Bridge Removal & Clean Config-First Implementation

## Your Mission
You are implementing a complete legacy bridge removal and clean config-first FigureManager reconstruction. Based on the comprehensive audit in `/docs/legacy-bridge-audit.md`, you will remove ALL individual parameter handling and create a clean config-only constructor for FigureManager.

## Context
This is Step 2 of Phase 2 in our FigureManager parameter organization project. The audit identified exactly what needs removal:
- **2 legacy bridge methods** to delete (~100 lines)
- **13 individual parameters** to remove from constructor
- **Config-first constructor** to implement using existing `create_figure_manager()` pattern
- **Enhanced FigureConfig** to create with organized kwargs

**CRITICAL**: No backwards compatibility - complete clean slate implementation.

## Your Systematic Implementation

### 1. Delete Legacy Bridge Methods
**Remove these exact methods from src/dr_plotter/figure.py:**
- `_convert_legacy_legend_params()` (line 71, ~25 lines)
- `_build_legend_config()` (line 209, ~50 lines)
- Delete the strategy mapping dictionary used by these methods

**Validation**: Search codebase to confirm no other code calls these methods (audit confirmed they're only called from constructor).

### 2. Clean FigureManager Constructor Signature  
**Replace the current constructor with config-only interface:**

**Current (from audit)**:
```python
def __init__(
    self,
    rows: int = 1,
    cols: int = 1, 
    external_ax: Optional[plt.Axes] = None,
    layout_rect: Optional[List[float]] = None,
    layout_pad: Optional[float] = 0.5,
    legend_config: Optional[LegendConfig] = None,
    legend_strategy: Optional[str] = None,
    # ... 13 total individual parameters
    **fig_kwargs: Any,
) -> None:
```

**Target (config-first)**:
```python
def __init__(
    self,
    layout: Optional[SubplotLayoutConfig] = None,
    legend: Optional[LegendConfig] = None,
    figure: Optional[FigureConfig] = None,
    theme: Optional[Theme] = None,
    faceting: Optional[SubplotFacetingConfig] = None,
) -> None:
```

### 3. Create Enhanced FigureConfig Class
**Location**: Extend or replace `FigureCoordinationConfig` in `src/dr_plotter/figure_config.py`

**Requirements**:
```python
@dataclass
class FigureConfig:
    # Explicit parameters for common use cases
    figsize: Tuple[int, int] = (12, 8)
    plot_margin_top: float = 0.1
    plot_margin_bottom: float = 0.1
    plot_margin_left: float = 0.1
    plot_margin_right: float = 0.1
    
    # Organized kwargs for matplotlib parameter routing
    figure_kwargs: Dict[str, Any] = field(default_factory=dict)     # → plt.figure()
    subplot_kwargs: Dict[str, Any] = field(default_factory=dict)    # → plt.subplots()
    axes_kwargs: Dict[str, Any] = field(default_factory=dict)       # → individual axes
    plotter_kwargs: Dict[str, Any] = field(default_factory=dict)    # → plotter-specific params
    
    # Integration parameters
    external_ax: Optional[plt.Axes] = None
    shared_styling: Optional[bool] = None
    
    def validate(self) -> None:
        # Add validation logic for figsize, margins, etc.
        pass
```

### 4. Implement Clean Constructor Logic
**Replace all parameter conversion with direct config usage:**

**Remove**:
- All individual parameter processing
- All calls to `_convert_legacy_legend_params()`
- All calls to `_build_legend_config()`
- Special default handling (layout_pad fallback, etc.)

**Implement**:
- Default config object creation if None provided
- Config object validation calls
- Direct config usage (no conversion)
- Use existing `_init_from_configs()` pattern

### 5. Update Parameter Routing System
**Route FigureConfig organized kwargs to correct destinations:**

**Figure kwargs routing** → `plt.figure(**figure.figure_kwargs)`
**Subplot kwargs routing** → `plt.subplots(**figure.subplot_kwargs)` 
**Axes kwargs routing** → Applied to individual axes during plot creation
**Plotter kwargs routing** → Pass to specific plotters to fix format/positioning issues

### 6. Fix Broken Functionality
**Use audit findings to fix known issues:**
- **Margin controls**: Ensure `plot_margin_top`, `plot_margin_bottom` work correctly via proper config routing
- **Parameter routing**: Enable plotter-specific parameters to reach destinations
- **Theme integration**: Maintain seamless theme + config integration

## Code Requirements

**CRITICAL - Follow Project Standards**:
1. **No comments or docstrings anywhere** - code must be self-documenting
2. **Comprehensive type hints** on ALL functions and methods
3. **All imports at the very top** of files - never in middle or bottom
4. **Use assertions for validation**: `assert condition, "message"` instead of exceptions
5. **Remove any existing comments** when editing files

## Expected Outcome

### FigureManager Usage Pattern
**After your changes, this should be the ONLY way to use FigureManager**:
```python
from dr_plotter.figure_config import SubplotLayoutConfig, FigureConfig
from dr_plotter.legend_manager import LegendConfig

fm = FigureManager(
    layout=SubplotLayoutConfig(rows=2, cols=4),
    legend=LegendConfig(strategy=LegendStrategy.FIGURE_BELOW, ncol=8),
    figure=FigureConfig(
        figsize=(16, 9),
        plot_margin_bottom=0.12,
        subplot_kwargs={'sharey': 'row'},
        plotter_kwargs={'format': 'int', 'xlabel_pos': 'bottom'}
    )
)
```

### Functionality Preservation
**All current functionality must work, but accessed via config objects:**
- Legend positioning and strategy
- Plot margins and spacing
- Theme integration
- Matplotlib parameter passing
- Subplot coordination (sharey, sharex)

## Validation Requirements

**Before submitting**:
1. **All legacy methods deleted** - confirm `_convert_legacy_*` methods don't exist
2. **Constructor is config-only** - no individual parameters accepted
3. **Enhanced FigureConfig created** - with organized kwargs structure
4. **Parameter routing implemented** - kwargs reach correct matplotlib/plotter destinations
5. **Code standards compliance** - no comments, imports at top, type hints complete

## Success Criteria
- ✅ Clean config-first FigureManager constructor (no individual parameters)
- ✅ Enhanced FigureConfig with organized kwargs for parameter routing
- ✅ All legacy bridge code removed (~100 lines deleted)
- ✅ Parameter routing system enables matplotlib and plotter-specific parameters
- ✅ All broken functionality (margins, routing) now works correctly
- ✅ Foundation ready for examples migration (Step 3)

## Strategic Impact
This removal creates the clean config-first foundation that will:
- Fix broken margin controls through proper config routing
- Enable plotter-specific parameters (format, positioning) via organized kwargs
- Eliminate theme-parameter conflicts through clear separation
- Provide foundation for faceting features via SubplotFacetingConfig integration

**Critical**: Missing ANY legacy code will break the clean implementation. Use the audit findings to ensure complete removal of all individual parameter handling.
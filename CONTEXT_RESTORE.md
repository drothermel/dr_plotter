# Context Restoration Guide

## Current Work: Architectural Improvements to dr_plotter Configuration System

### What We've Accomplished

1. **Enhanced 00_datadec_grids.py example** with native dr_plotter features:
   - Main title using `figure_title` in LayoutConfig (no more manual `fm.fig.suptitle()`)
   - Row/column titles using `row_titles=True, col_titles=True` in faceting config
   - Exterior axis labels using `exterior_x_label="Training Steps"` in faceting config
   - All grid styling handled automatically by unified styling system
   - **CRITICAL FIX**: Added `row_order=params, col_order=data` to fix row label mismatch issue

2. **Major Architectural Refactor - PlotConfig now handles all configuration**:
   - **OLD**: `FigureManager(PlotConfig(...), suptitle_y=0.5)` - kwargs bypass PlotConfig
   - **NEW**: `FigureManager(PlotConfig(..., kwargs={"suptitle_y": 0.5}))` - all config through PlotConfig
   - **Benefits**: Single configuration interface, proper architectural boundaries, styler integration

3. **Unified Styling System** created:
   - Created `styling_utils.py` with shared utilities both faceted and non-faceted plotting use
   - Functions: `apply_title_styling()`, `apply_xlabel_styling()`, `apply_ylabel_styling()`, `apply_grid_styling()`
   - **Problem Solved**: Faceted plotting was bypassing normal styling (no grid, no themed fonts/colors)
   - **Result**: Both pathways now use identical styling logic - fix once, benefits everywhere

4. **Theme Integration Improvements**:
   - Added `suptitle_fontsize=16` and `suptitle_y=0.99` to theme system  
   - FigureManager now has StyleApplicator for proper theme-based styling
   - Grid visibility fixed by adding `grid=True` to base theme's axes_styles

### Current Architecture

**PlotConfig Structure**:
```python
PlotConfig(
    layout={...},           # LayoutConfig - positioning, sizing, figure-level layout
    style={...},            # StyleConfig - colors, themes, visual styling  
    legend={...},           # LegendConfig - legend positioning and appearance
    kwargs={"suptitle_y": 0.98}  # Ad-hoc overrides with styler priority
)
```

**Styler Priority**: kwargs > theme > default (automatic via StyleApplicator)

### Key Files Modified

- `src/dr_plotter/configs/plot_config.py` - added `kwargs: dict[str, Any] = field(default_factory=dict)`
- `src/dr_plotter/figure_manager.py` - removed kwargs param, uses `config.kwargs` for styler
- `src/dr_plotter/configs/layout_config.py` - added `figure_title: str | None = None`
- `src/dr_plotter/configs/faceting_config.py` - added `row_titles`, `col_titles`, `exterior_x_label`, `exterior_y_label`
- `src/dr_plotter/faceting/faceting_core.py` - added native title/label support, unified grid styling
- `src/dr_plotter/theme.py` - added `suptitle_fontsize=16, suptitle_y=0.99, grid=True`
- `src/dr_plotter/styling_utils.py` - NEW: shared styling utilities for both pathways
- `src/dr_plotter/plotters/base.py` - updated to use shared styling utilities
- `examples/00_datadec_grids.py` - demonstrates all new native features

### API Examples

**Native row/column titles**:
```python
fm.plot_faceted(
    row_titles=True,          # Auto-generate from dimension values
    col_titles=True,
    exterior_x_label="Training Steps"  # Bottom row only
)
```

**Custom positioning via kwargs**:
```python
PlotConfig(
    layout={"figure_title": "My Title"},
    kwargs={"suptitle_y": 0.85}  # Overrides theme default of 0.99
)
```

### Testing Status

✅ **Faceted plotting**: `uv run python examples/00_datadec_grids.py` - all features working
✅ **Non-faceted plotting**: `uv run python examples/01_basic_line.py` - backward compatibility maintained
✅ **Styling unification**: Both pathways use same styling logic, grid appears correctly

### Next Steps (if needed)

The core architecture is complete and working. Future enhancements could include:
- Additional exterior label patterns (top row, right column)
- More theme-configurable positioning parameters
- Further styling unification opportunities

### Key Insight

The major breakthrough was recognizing that faceted plotting was bypassing the normal plotter styling pipeline, creating two separate systems. By creating shared utilities and proper PlotConfig integration, we now have a unified, maintainable architecture where styling improvements benefit all plotting modes automatically.
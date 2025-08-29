# FigureConfig Architecture Audit: Parameter Classification & Side Effects Analysis

## Executive Summary

**✅ ARCHITECTURE VALIDATED** - Current FigureConfig design is sound with minor recommendations for improvement.

**Key Finding**: The parameter classification rule is architecturally correct, but nrows/ncols should remain explicit for usability and integration consistency.

## Matplotlib Function Call Inventory

### plt.subplots() Usage in dr_plotter
- **Location**: `src/dr_plotter/figure.py:102-103`
- **Current parameters used**: `layout.rows, layout.cols, constrained_layout=False, **combined_kwargs`
- **Our subplot_kwargs coverage**: ✅ Complete - all additional matplotlib parameters can be passed through `subplot_kwargs`

### plt.tight_layout() Usage in dr_plotter
- **Locations**: Multiple calls in `figure.py:finalize_layout()` method (lines 171, 179, 181, 183, 185)
- **Current parameters used**: 
  - `rect` parameter: Dynamic calculation based on legend strategy and layout requirements
  - `pad` parameter: Always uses `self._layout_pad` from SubplotLayoutConfig
- **Our coverage**: ✅ Complete - `layout_pad` correctly explicit, `rect` computed internally

### Other Layout Functions Used
- **constrained_layout**: Set to `False` in plt.subplots() call - no additional configuration needed
- **plt.figure()**: Not directly called - figure created via plt.subplots()
- **plt.subplots_adjust()**: Not used - tight_layout preferred
- **gridspec**: Not used - using standard subplot grid

## Missing Explicit Parameters Analysis

### Parameters That Should Be Explicit
- **tight_layout_pad (currently layout_pad)**: 
  - **Why explicit**: Used across multiple separate `tight_layout()` function calls
  - **Current usage**: In SubplotLayoutConfig as `layout_pad`, accessed as `self._layout_pad`
  - **Status**: ✅ Correctly explicit in SubplotLayoutConfig
  
- **layout_rect**:
  - **Why explicit**: Controls tight_layout rect parameter, requires special processing
  - **Current usage**: Optional explicit parameter in SubplotLayoutConfig
  - **Status**: ✅ Correctly explicit

### Parameters Correctly Classified

**Confirmed kwargs parameters** (direct matplotlib function parameters):
- **figsize**: Direct parameter to plt.subplots() - belongs in `subplot_kwargs`
- **sharex/sharey**: Direct parameters to plt.subplots() - belongs in `subplot_kwargs`
- **constrained_layout**: We override to False, but could be in `subplot_kwargs` if needed
- **All other plt.subplots() parameters**: Correctly handled through `subplot_kwargs`

**Confirmed explicit parameters**:
- **nrows/ncols**: Should remain explicit despite being plt.subplots() parameters (see reasoning below)
- **figsize**: Should remain explicit for consistency and usability
- **plot_margin_***: Dr_plotter specific, not direct matplotlib parameters - correctly explicit
- **external_ax**: Integration parameter - correctly explicit
- **shared_styling**: Dr_plotter specific - correctly explicit

## Side Effects Assessment

### Parameter Extraction Complexity

**Grid dimension extraction impact**:
- **FigureManager storage**: `self.rows = layout.rows` and `self.cols = layout.cols` in line 110-111
- **Usage frequency**: Grid dimensions referenced only during initialization for internal state
- **Performance implications**: Zero impact - values extracted once during construction
- **Code complexity**: Minimal - straightforward attribute access pattern

**Parameter routing complexity**:
- **Current approach**: Clean separation with explicit constructor parameters
- **Alternative kwargs approach**: Would require `layout.rows`, `layout.cols` or extraction from `subplot_kwargs`

### Integration Impact

**Theme system integration**:
- **Current dependency**: No direct dependency on figure dimensions or grid layout
- **StyleEngine integration**: Passes figure_manager reference, no direct grid dimension access needed
- **Impact assessment**: ✅ No integration issues with parameter classification

**Legend system integration**:
- **LegendManager constructor**: Takes `figure_manager` reference (line 88 in legend_manager.py)  
- **Grid dimension usage**: No direct access to grid dimensions in legend code
- **Legend positioning**: Uses layout_rect and margin calculations, not raw grid dimensions
- **Impact assessment**: ✅ No integration issues

**Plotter system integration**:
- **BasePlotter constructor**: Takes `figure_manager` reference (line 86 in base.py)
- **Grid dimension access**: Plotters access individual axes via `figure_manager.get_axes(row, col)`
- **Direct grid dimension usage**: No direct access to grid dimensions in plotter code
- **Impact assessment**: ✅ No integration issues - plotters work through axes access pattern

### Validation & Usability

**User experience comparison**:

```python
# Current explicit approach (recommended)
layout = SubplotLayoutConfig(rows=2, cols=3)
figure = FigureConfig(figsize=(16, 9), subplot_kwargs={'sharey': 'row'})

# Pure kwargs approach (not recommended)  
figure = FigureConfig(subplot_kwargs={
    'nrows': 2, 'ncols': 3, 'figsize': (16, 9), 'sharey': 'row'
})
```

**Usability assessment**:
- **✅ Explicit approach advantages**:
  - Clear separation of grid structure vs. matplotlib customization
  - Consistent with existing dr_plotter patterns (layout separate from figure)
  - IDE autocomplete and type checking for common parameters
  - Matches user mental model: "I want a 2x3 grid with these figure properties"

- **❌ Pure kwargs disadvantages**:
  - Mixes structural parameters with styling parameters
  - Requires users to know matplotlib parameter names (`nrows` vs `rows`)
  - Less discoverable interface
  - Breaks consistency with SubplotLayoutConfig architecture

**Type checking impact**:
- **Explicit parameters**: Full type hints, IDE support, validation at config creation
- **Kwargs parameters**: Limited type checking within dictionaries

**Default handling complexity**:
- **Current approach**: Simple dataclass defaults work perfectly
- **Kwargs approach**: Would require custom default extraction logic

## Recommendations

### Architecture Validation
- **✅ APPROVE current architecture** with minor refinements
- **✅ Parameter classification rule is sound and well-executed**
- **✅ No significant implementation concerns identified**

### Recommended Refinements

1. **Keep nrows/ncols explicit** in SubplotLayoutConfig despite being matplotlib parameters
   - **Rationale**: Maintains clear structural vs. customization separation
   - **Benefit**: Superior usability and consistency with existing patterns

2. **Keep figsize explicit** in FigureConfig  
   - **Rationale**: Most commonly customized parameter, deserves first-class treatment
   - **Benefit**: Easier discovery and configuration

3. **Maintain current subplot_kwargs for advanced users**
   - **Rationale**: Provides escape hatch for matplotlib power users
   - **Implementation**: Current conflict resolution (explicit overrides kwargs) is correct

### Implementation Validation
- **✅ Current parameter routing is optimal**
- **✅ Integration points are clean and maintainable**
- **✅ No performance or complexity issues identified**
- **✅ Architecture scales well for future matplotlib function integration**

## Conclusion

The current FigureConfig architecture successfully achieves the design goals:
- Clear parameter classification with intuitive user interface
- Complete matplotlib function coverage through organized kwargs
- Clean integration with all dr_plotter systems
- Maintainable and extensible design

**Recommendation**: Proceed with current architecture - no modifications needed before example migration.
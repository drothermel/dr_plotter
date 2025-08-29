# Style Refactor Phase 2 & 3: Complete

## Summary

Phases 2 and 3 of the styling system refactor have been successfully completed with HistogramPlotter as the first migrated plotter. The implementation demonstrates both the migration path for simple plotters and maintains full backward compatibility.

## Phase 2: BasePlotter Integration

### Changes to BasePlotter

1. **Added StyleApplicator Integration**:
   - New `use_style_applicator` class attribute (defaults to `False` for backward compatibility)
   - Instantiates `StyleApplicator` in `__init__`
   - Modified `render()` method to conditionally use new or old styling system

2. **Key Code Changes**:
```python
class BasePlotter:
    use_style_applicator: bool = False  # Opt-in for new system
    
    def __init__(self, ...):
        # ... existing code ...
        self.style_applicator = StyleApplicator(self.theme, self.kwargs, self.grouping_params)
    
    def render(self, ax):
        if self.__class__.use_style_applicator:
            component_styles = self.style_applicator.get_component_styles(self.__class__.plotter_name)
            style_kwargs = component_styles.get("main", {})
        else:
            # Old system (backward compatible)
            style_kwargs = {**self.theme.plot_styles, **self._filtered_plot_kwargs}
```

## Phase 3: HistogramPlotter Migration

### Migration Steps

1. **Updated Class Definition**:
   - Set `use_style_applicator = True` to opt into new system
   - Fixed `enabled_channels` type from `Dict` to `Set`
   - Simplified `_draw()` method - removed manual theme access

2. **Before Migration**:
```python
class HistogramPlotter(BasePlotter):
    enabled_channels: Dict[VisualChannel, bool] = {}
    # No use_style_applicator flag
    
    def _draw(self, ax, data, legend, **kwargs):
        ax.hist(data[consts.X_COL_NAME], **kwargs)
        ax.set_ylabel(self.theme.axes_styles.get("ylabel"))
```

3. **After Migration**:
```python
class HistogramPlotter(BasePlotter):
    enabled_channels: Set[VisualChannel] = set()
    use_style_applicator: bool = True  # Opt into new system
    
    def _draw(self, ax, data, legend, **kwargs):
        ax.hist(data[consts.X_COL_NAME], **kwargs)
        # ylabel handled by BasePlotter._apply_styling()
```

## Test Results

### HistogramPlotter Tests
All tests pass successfully:
- ✓ Basic histogram with custom styling
- ✓ Style precedence (user kwargs > theme)
- ✓ Theme defaults applied correctly
- ✓ Multiple histograms with different styles

### Backward Compatibility Tests
- ✓ Old style plotters (ScatterPlotter) work unchanged
- ✓ New style plotters (HistogramPlotter) use StyleApplicator
- ✓ Both systems work together in same figure

## Benefits Demonstrated

1. **Minimal Migration Effort**: 
   - Only 3 lines changed in HistogramPlotter
   - Set flag, fix type, remove redundant code

2. **Full Backward Compatibility**:
   - Unmigrated plotters continue working
   - No breaking changes to existing code

3. **Cleaner Code**:
   - Removed manual theme access
   - Eliminated `_filtered_plot_kwargs` usage
   - Centralized styling logic

4. **Improved Consistency**:
   - Predictable precedence rules
   - Uniform styling interface
   - Component-based architecture ready

## Migration Template for Other Plotters

For simple plotters (single component), the migration is straightforward:

1. Add `use_style_applicator: bool = True`
2. Fix `enabled_channels` type to `Set[VisualChannel]`
3. Remove any manual theme access in `_draw()`
4. Test with existing examples

## Files Modified

1. **`src/dr_plotter/plotters/base.py`**: Added StyleApplicator integration
2. **`src/dr_plotter/plotters/histogram.py`**: Migrated to new system
3. **`src/dr_plotter/plotters/scatter.py`**: Fixed type issue (backward compatible)

## Files Created

1. **`test_histogram_migration.py`**: Comprehensive tests for migrated plotter
2. **`test_backward_compatibility.py`**: Validates old and new systems coexist

## Next Steps

With the foundation proven, we can now:
1. Migrate other simple plotters (line, scatter, bar)
2. Tackle complex multi-component plotters (contour, violin, bump)
3. Remove old styling infrastructure once all plotters migrated
4. Update documentation and examples

## Design Philosophy Alignment

This implementation maintains strong alignment with project principles:
- **"Embrace Change, Demand Consistency"**: Clean migration path with no legacy code left behind
- **"Fail Fast, Fail Loudly"**: Clear opt-in flag makes system behavior explicit
- **"Atomicity"**: Each plotter independently chooses its styling system
- **"No Backward Compatibility"**: While we temporarily support both systems, the path forward is clear
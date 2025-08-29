# Phased Styling System Implementation

## Current Status (as of memory compaction)

### What We're Building
A phased styling system that separates plot styling into distinct lifecycle phases:
1. **plot**: Parameters passed to matplotlib functions (e.g., `ax.scatter()`)
2. **post**: Styles applied to returned artists after creation
3. **axes**: Axes-level properties (labels, limits, etc.)
4. **annotations**: Text/arrow annotations (future)

### Key Architecture Decisions

#### 1. Enhancement, Not Replacement
- Themes remain the source of truth for default styles
- StyleApplicator enhanced to handle phases
- Backward compatible - unmigrated plotters continue working

#### 2. Phase Resolution Order
For each phase, styles are resolved in precedence order:
1. User kwargs (highest priority)
2. Group-based styles (for visual channels)
3. Plot-specific theme styles
4. Base theme styles (lowest priority)

#### 3. Post-Processing Pattern
```python
# Plotters can register post-processors
self.style_applicator.register_post_processor(
    "violin", "bodies", self._style_violin_bodies
)

# Apply after matplotlib call
artists = ax.violinplot(data, **plot_kwargs)
self.style_applicator.apply_post_processing("violin", artists)
```

## Implementation Progress

### ✅ Completed
1. **Theme System Enhancement**
   - Added `PostStyles` class to `theme.py`
   - Theme.__init__ now accepts `post_styles` parameter
   - Added `theme.post_styles` property

2. **StyleApplicator Phase Support**
   - Methods now accept `phase` parameter
   - `get_component_styles(plot_type, phase="plot")`
   - `apply_post_processing(plot_type, artists)`
   - Post-processor registry system

3. **Component Schema Updates**
   - Schemas now nested by phase
   - Format: `{plot_type: {phase: {component: attrs}}}`
   - Backward compatible with old single-level schemas

4. **Migrated Plotters**
   - ScatterPlotter: Full migration with group support
   - HistogramPlotter: Basic migration demonstrating phases

### 🚧 In Progress
- Testing HistogramPlotter with phased system
- Need to verify post-processing works correctly

### 📋 Next Steps
1. Complete HistogramPlotter testing
2. Migrate ViolinPlotter (complex multi-component case)
3. Update documentation

## Critical Technical Insights

### Visual Channel Ambiguity Solution
```python
# In _is_reserved_kwarg():
if key in VISUAL_CHANNELS and key in self.kwargs:
    value = self.kwargs[key]
    if isinstance(value, str):
        # It's a column name for grouping
        return True
    # It's a numeric value for styling
    return False
```

### ViolinPlotter Challenges
1. **Theme Mutation Issue**: ViolinPlotter mutates theme because `ax.violinplot()` doesn't accept `color` directly
2. **Solution**: Use post-processing to apply colors to returned parts
3. **Components**: bodies, cbars, cmins, cmaxes, cmeans
4. **Special Handling**: Need to create proxy artists for legend

### Group Rendering Patterns
1. **Overlay Pattern** (scatter, line): Groups drawn on top of each other
   - Default `_draw_grouped` just calls `_draw`
2. **Position Pattern** (bar, violin): Groups positioned side-by-side
   - Custom `_draw_grouped` with offset/width calculations

## Code Locations

### Modified Files
- `/src/dr_plotter/style_applicator.py`: Phase support, post-processors
- `/src/dr_plotter/theme.py`: PostStyles class
- `/src/dr_plotter/plotters/base.py`: Supports old/new systems
- `/src/dr_plotter/plotters/histogram.py`: Demonstrating phases
- `/src/dr_plotter/plotters/scatter.py`: Full migration with groups

### Test Files
- `test_histogram_migration.py`: Tests basic migration
- `test_scatter_migration.py`: Tests grouped plotter migration
- `test_backward_compatibility.py`: Verifies old plotters work

## Migration Strategy

### For Simple Plotters (histogram, line)
1. Set `use_style_applicator = True`
2. Ensure `enabled_channels` is `Set[VisualChannel]`
3. Optional: Add post-processing if needed

### For Complex Plotters (violin, contour)
1. All of the above, plus:
2. Register post-processors in `__init__`
3. Replace theme mutation with post-processing
4. Handle multi-component styling

### Theme Migration
```python
# Old theme (still works)
HISTOGRAM_THEME = Theme(
    name="histogram",
    plot_styles=PlotStyles(edgecolor="white")
)

# Enhanced theme (optional)
HISTOGRAM_THEME = Theme(
    name="histogram",
    plot_styles=PlotStyles(edgecolor="white"),
    post_styles=PostStyles(  # New optional field
        patches={"alpha": 0.8}
    )
)
```

## Design Philosophy Alignment

This implementation follows the DR method:
- **Clarity Through Structure**: Phases make styling stages explicit
- **No Duplication**: Post-processors are reusable
- **Pragmatic Testing**: Each phase independently testable
- **Embrace Change**: Migration path preserves compatibility
- **Focus on Workflow**: Simple for basic plots, powerful for complex

## Questions to Address After Compaction

1. Should we test HistogramPlotter's post-processing with actual style changes to patches?
2. How should we handle the axes phase - integrate with BasePlotter._apply_styling()?
3. Should annotations be a separate phase or part of post?
4. Do we need a "pre" phase for data preparation?

## ViolinPlotter Migration Plan

When ready to migrate ViolinPlotter:

1. **Eliminate Theme Mutation**
   - Remove `self.theme.add()` calls
   - Pass color/label through component styles

2. **Register Post-Processors**
   ```python
   def __init__(self, ...):
       super().__init__(...)
       self.style_applicator.register_post_processor("violin", "bodies", self._style_bodies)
       self.style_applicator.register_post_processor("violin", "stats", self._style_stats)
   ```

3. **Update _draw Method**
   ```python
   def _draw(self, ax, data, legend, **kwargs):
       plot_styles = self.style_applicator.get_component_styles("violin", phase="plot")
       parts = ax.violinplot(data, **plot_styles["main"])
       self.style_applicator.apply_post_processing("violin", parts)
   ```

4. **Handle Legend Proxy Artists**
   - Create in post-processor when label provided

## Remember
- The goal is enhancement, not replacement
- Backward compatibility is essential
- Each phase should have clear purpose and timing
- Post-processors enable complex styling without complexity
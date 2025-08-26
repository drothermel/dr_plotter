# Lab Notebook: FigureManager Parameter Organization & Theme Integration

## Project Info
- **Date**: 2025-08-26
- **Project**: Reorganize FigureManager parameter architecture and fix theme integration conflicts
- **Duration**: Infrastructure cleanup project - Phase 1 starting
- **Status**: Planning complete, ready to begin Phase 1 analysis

## Problem Discovery Context
- **Origin**: Discovered during faceted plotting implementation project Phase 2
- **Trigger**: Visual evidence that margin controls are broken, theme conflicts preventing full integration
- **Scope**: FigureManager architecture needs systematic reorganization before advanced features

## Evidence Base

### Parameter Chaos Discovered
**Location**: FigureManager.__init__() method signature
- **Current parameters**: `plot_margin_bottom`, `legend_y_offset`, `layout_pad`, `legend_ncol`, `legend_strategy`, `plot_margin_top`, `sharey`, `figsize`
- **Problem**: No logical grouping or clear separation of concerns
- **Impact**: 15+ separate parameters with unclear relationships and conflicts

### Visual Evidence of Broken Controls
**Location**: examples/06_faceted_training_curves.py output
- **Issue**: `plot_margin_top=0.1`, `plot_margin_bottom=0.5` parameters not producing expected visual layout
- **Symptoms**: Legend spacing and plot margins not responding to parameter changes
- **Code reference**: Lines 72-76 in create_faceted_grid() function

### Theme Integration Conflicts
**Location**: examples/06b_faceted_training_curves_themed.py analysis
- **Conflict**: Theme system AxesStyles can store `xscale`/`yscale` but requires manual application
- **Conflict**: Legend configuration split between theme and FigureManager parameters
- **Code reference**: Lines 123-132 manual theme scale application workaround

### Parameter Categories Identified
1. **Layout Parameters**: `figsize`, `plot_margin_top`, `plot_margin_bottom`, `layout_pad`
2. **Legend Parameters**: `legend_strategy`, `legend_ncol`, `legend_y_offset`  
3. **Matplotlib Parameters**: `sharey`, `sharex`
4. **Theme Parameters**: Styling, colors, fonts - should be theme-controlled
5. **Uncategorized**: Mixed parameters without clear organizational logic

## Technical Discoveries

### Theme System Architecture Analysis
**Location**: docs/theme-system-analysis.md findings
- **Discovery**: Theme system is sophisticated but has coverage gaps
- **Finding**: 60% of styling can be themed, 40% requires manual configuration
- **Issue**: No clear boundary between theme responsibility and manager responsibility

### Backwards Compatibility Requirements
**Evidence**: Existing examples in examples/ directory
- **Constraint**: Must maintain functionality of examples/01-05 during reorganization
- **Risk**: Breaking changes would disrupt existing user code
- **Strategy**: Deprecation warnings + backwards compatibility layer needed

### Parameter Dependency Mapping
**Discovered Dependencies**:
- `legend_strategy="figure_below"` requires `plot_margin_bottom` adjustment
- `legend_ncol` affects required `legend_y_offset` values
- `theme` parameter conflicts with direct styling parameters

## Ideas & Notes

### Proposed Parameter Architecture
```python
# Current (chaotic):
FigureManager(legend_strategy, legend_ncol, plot_margin_bottom, legend_y_offset, layout_pad, ...)

# Proposed (organized):
FigureManager(
    layout=LayoutConfig(figsize=(16,9), margins=Margins(top=0.1, bottom=0.5), padding=0.3),
    legend=LegendConfig(strategy="figure_below", columns=8, offset=0.02),
    theme=custom_theme
)
```

### Theme Integration Improvements
- **Automatic axis scaling**: Theme should automatically apply scale settings
- **Layout theme integration**: Some layout parameters should be theme-controlled
- **Clear responsibility boundaries**: Document what belongs to theme vs manager

### Migration Strategy Considerations
- **Backwards compatibility**: Keep old parameter signatures with deprecation warnings
- **Progressive enhancement**: New architecture available alongside old parameters
- **Documentation**: Clear migration guide from old to new parameter organization

## Environment Notes
- **Impact scope**: All existing examples potentially affected
- **Testing requirements**: Comprehensive validation needed across all plot types
- **Dependencies**: Must not break existing dr_plotter functionality during reorganization

## Next Steps for Phase 1
1. **Complete parameter inventory**: Catalog all FigureManager parameters with current behavior
2. **Document theme conflicts**: Specific examples of theme-manager parameter conflicts
3. **Test current functionality**: Establish baseline behavior before changes
4. **Map parameter dependencies**: Document how parameters interact with each other

## References
- **Discovery source**: docs/phase-2-friction-analysis.md friction points
- **Theme analysis**: docs/theme-system-analysis.md conflict documentation  
- **Visual evidence**: examples/plots/06_faceted_training_curves.png layout issues
- **Code locations**: examples/06_faceted_training_curves.py lines 66-83 parameter usage
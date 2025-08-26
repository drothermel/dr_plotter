# FigureManager Parameter Organization & Theme Integration

## Overview
Systematic reorganization of FigureManager parameter architecture to resolve parameter chaos, fix theme integration conflicts, and establish clean foundation for advanced features like faceted plotting.

**Root Problem**: FigureManager has grown organically with unorganized parameters causing theme conflicts, broken controls, and poor developer experience.

## Evidence Base

### Issues Discovered in Faceted Plotting Project
- **Parameter Chaos**: `plot_margin_bottom`, `legend_y_offset`, `layout_pad`, `legend_ncol`, `legend_strategy` lack logical grouping
- **Theme Conflicts**: Theme system cannot properly integrate due to overlapping parameter responsibilities  
- **Broken Controls**: Visual evidence that margin parameters don't work as expected
- **Poor Developer UX**: 15+ separate parameters with unclear relationships and priorities
- **Data Ordering Override**: Internal data processing (e.g., `pandas.pivot()` in HeatmapPlotter) overrides user data ordering intentions, requiring categorical workarounds
- **Parameter Routing Failures**: Plotter-specific parameters (e.g., `format='int'`, `xlabel_pos='bottom'` in heatmap) cannot be passed through API due to poor parameter routing architecture
- **Theme-Behavior Misalignment**: `GROUPED_BAR_THEME` doesn't control bar grouping behavior - themes only affect styling, not fundamental plot structure/layout

### Architecture Inventory Findings (Phase 1a Complete)
- **Rich Configuration Infrastructure Exists**: 6 config classes already implemented (LegendConfig, SubplotLayoutConfig, SubplotFacetingConfig, etc.)
- **Legacy Bridge Pattern**: FigureManager converts individual parameters to config objects internally via `_convert_legacy_*()` methods
- **SubplotFacetingConfig Ready**: Infrastructure for Phase 3 faceted plotting already exists but unused
- **80% Complete Architecture**: Most parameter organization infrastructure already built, just needs proper integration

### Strategic Impact
- **Foundation Already Exists**: Need refactoring, not redesign - remove legacy bridges and use existing config infrastructure
- **Faceted Plotting Ready**: SubplotFacetingConfig provides immediate foundation for advanced features
- **Clean Config-First API Possible**: `create_figure_manager()` factory function already exists for config-based construction

## Systematic Process

### Phase 1: Architecture Analysis ✅ COMPLETE
**Phase 1a**: Existing architecture inventory - discovered rich config infrastructure already exists
**Phase 1b**: Parameter mapping to existing configs - identify what needs new homes vs what can use existing infrastructure

### Phase 2: Clean Slate Implementation 
**Objective**: Remove legacy bridges completely and implement clean config-first FigureManager

**No Backwards Compatibility Decision**: Remove all legacy parameter support and `_convert_legacy_*()` methods for clean API

**Implementation Strategy**:
1. **Remove Legacy Bridges**: Delete all `_convert_legacy_*()` methods and individual parameter handling
2. **Expand Existing Configs**: Extend FigureCoordinationConfig → FigureConfig with organized kwargs
3. **Config-First Constructor**: Make FigureManager accept only config objects
4. **Factory Function Primary**: Make `create_figure_manager()` the main interface

**Target Architecture**:
```python
FigureManager(
    layout=SubplotLayoutConfig(...),
    legend=LegendConfig(...),
    figure=FigureConfig(
        figsize=(12, 8), 
        plot_margin_top=0.1,
        figure_kwargs={'dpi': 150},  # → plt.figure()
        subplot_kwargs={'sharex': True},  # → plt.subplots()
        axes_kwargs={'axisbelow': True}  # → individual axes
    ),
    theme=Theme(...),
    faceting=SubplotFacetingConfig(...)  # Ready for Phase 3!
)
```

**Deliverables**:
- FigureConfig class with organized kwargs (figure_kwargs, subplot_kwargs, axes_kwargs)
- Clean FigureManager constructor accepting only config objects
- All legacy bridge code removed
- Data ordering preservation system for plotter pipeline
- Parameter routing system enabling plotter-specific parameters to reach their destinations
- Examples updated to use new config-first API

**Success Criteria**:
- Clean config-first API with no individual parameters
- All layout controls working correctly via proper config routing
- Theme integration seamless with config objects
- Data ordering preserved through entire plotting pipeline
- Plotter-specific parameters (format, positioning, etc.) successfully routed to correct destinations
- Theme system clearly separated from behavioral parameters (themes control styling, configs control behavior)
- Foundation ready for faceted plotting features

### Phase 3: Example Migration & Testing
**Objective**: Update all examples to use new config-first API and validate functionality

**Migration Strategy**:
- Update all examples/ to use config objects
- Verify all visual outputs remain identical
- Test that broken margin controls now work correctly
- Validate data ordering preservation in heatmaps and other plotters
- Validate theme integration improvements

**Deliverables**:
- All examples using new config-first FigureManager
- Visual regression testing showing identical outputs
- Documentation of config-first API patterns
- Performance validation

**Success Criteria**:
- All examples work with new API
- Previously broken functionality now works
- Clean foundation established for advanced features
- No functional regressions from refactoring

### Phase 4: Faceting Integration Readiness
**Objective**: Validate that clean architecture enables SubplotFacetingConfig integration

**Validation Approach**:
- Test SubplotFacetingConfig integration with new FigureManager
- Verify config-first approach enables faceted plotting API
- Confirm foundation ready for Phase 3 faceted plotting project

**Success Criteria**:
- SubplotFacetingConfig integrates cleanly with new architecture
- Config-first approach proven to enable advanced features
- Clean handoff to Phase 3 faceted plotting development

## Key Architectural Decisions ✅ RESOLVED

1. **Parameter Grouping Strategy**: Use existing config classes (LegendConfig, SubplotLayoutConfig) + new FigureConfig for figure-level parameters
2. **Theme Integration Boundary**: Theme system already well-defined, integrates cleanly with config objects
3. **Backwards Compatibility**: REMOVED - clean slate implementation with no legacy support
4. **Kwargs Organization**: FigureConfig with `figure_kwargs`, `subplot_kwargs`, `axes_kwargs` for organized matplotlib parameter routing

## Success Metrics

**Immediate**: Clean config-first API with all layout controls working correctly
**Strategic**: Seamless theme integration with organized parameter architecture  
**Long-term**: SubplotFacetingConfig ready for immediate use in faceted plotting Phase 3

## Implementation Philosophy

**Clean Slate Approach**: Remove all legacy bridges and individual parameter handling for clean, maintainable API
**Build on Existing**: Leverage 80% complete config infrastructure rather than redesigning
**Organized Flexibility**: Explicit parameters for common use cases + organized kwargs for matplotlib power users
**Faceting Ready**: Clean foundation immediately enables advanced features
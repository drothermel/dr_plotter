# Plotter Kwargs Routing - Full Impact Analysis

## Executive Summary

This analysis examines the complete scope of changes required to implement systematic `plotter_kwargs` routing in dr_plotter without backward compatibility constraints. The analysis reveals that implementing this system would require **fundamental architectural changes** that would break the existing clean design patterns and introduce significant complexity.

**Key Finding**: The proposed plotter_kwargs system would require redesigning core architectural components, breaking extensive user code, and introducing maintenance complexity that likely outweighs the benefits of solving "stranded parameter" issues.

## 1. Current Parameter Flow Architecture

### Parameter Entry and Routing

The current system routes parameters through a sophisticated multi-layered architecture:

**Flow Path**: `FigureManager.plot()` → `_add_plot()` → `BasePlotter.__init__()` → `StyleApplicator` → Individual plotters

**Current Parameter Categories**:
1. **Reserved Parameters**: Data mapping (`x`, `y`), visual channels (`hue_by`, `style_by`), system (`theme`, `legend`)
2. **Base Plotter Parameters**: `BASE_PLOTTER_PARAMS = ["x", "y", "colorbar_label", "_figure_manager", "_shared_hue_styles"]`
3. **Plotter-Specific Parameters**: Most plotters define `plotter_params: List[str] = []` (empty)
4. **Component Schema Parameters**: Defined per plotter per phase
5. **Filtered Parameters**: `_filtered_plot_kwargs` removes reserved/plotter-specific params before matplotlib passthrough

### StyleApplicator Precedence System

Current precedence hierarchy (highest to lowest):
```python
component_kwargs > group_styles > plot_styles > base_styles
```

Where:
- **component_kwargs**: Direct parameters from plot() call
- **group_styles**: Visual channel styling (hue, size, marker, etc.)
- **plot_styles**: Plot-specific theme styling (LINE_THEME, SCATTER_THEME)
- **base_styles**: BASE_THEME defaults

### Stranded Parameters Discovery

**Current Issues**:
1. **Hardcoded Parameter Handling**: Parameters like `cmap`, `s` in ScatterPlotter have custom logic
2. **Inconsistent Filtering**: `_filtered_plot_kwargs` varies across plotters
3. **Direct Matplotlib Passthrough**: Remaining kwargs pass directly to matplotlib without validation
4. **Parameter Discovery Gap**: No systematic way to expose available parameters per plotter

## 2. Architectural Changes Required

### FigureManager Changes

**Current Constructor**:
```python
def __init__(
    self,
    figure: Optional["FigureConfig"] = None,
    legend: Optional[LegendConfig] = None,
    theme: Optional[Any] = None,
    faceting: Optional["SubplotFacetingConfig"] = None,
) -> None:
```

**Required Changes**:
```python
def __init__(
    self,
    figure: Optional["FigureConfig"] = None,
    legend: Optional[LegendConfig] = None,
    theme: Optional[Any] = None,
    faceting: Optional["SubplotFacetingConfig"] = None,
    # NEW: Global plotter overrides
    plotter_kwargs: Optional[Dict[str, Dict[str, Any]]] = None,
) -> None:
```

**New Responsibilities**:
1. **Parameter Validation**: Validate plotter_kwargs against plotter schemas
2. **Parameter Storage**: Store per-plotter parameter overrides
3. **Parameter Routing**: Route appropriate kwargs to each plot() call
4. **Conflict Resolution**: Handle conflicts between themes and plotter_kwargs

### Plotter Architecture Changes

**Current BasePlotter**:
```python
def __init__(
    self,
    data: pd.DataFrame,
    grouping_cfg: GroupingConfig,
    theme: Optional[Theme] = None,
    figure_manager: Optional[Any] = None,
    **kwargs: Any,
) -> None:
```

**Required Changes**:
```python
def __init__(
    self,
    data: pd.DataFrame,
    grouping_cfg: GroupingConfig,
    theme: Optional[Theme] = None,
    figure_manager: Optional[Any] = None,
    plotter_kwargs: Optional[Dict[str, Any]] = None,  # NEW
    **kwargs: Any,
) -> None:
```

**New Parameter Processing**:
```python
def _process_parameter_precedence(self) -> Dict[str, Any]:
    """New method to resolve parameter precedence"""
    # 1. Start with theme defaults
    # 2. Apply plotter_kwargs overrides  
    # 3. Apply group styles
    # 4. Apply direct kwargs
    # 5. Handle conflicts and validation
```

### Component Schema Expansion

**Current Schema**:
```python
component_schema: Dict[Phase, ComponentSchema] = {
    "plot": {"main": {"s", "alpha", "color", "marker"}},
    "axes": {"title": {"text", "fontsize", "color"}},
}
```

**Required Schema Extensions**:
```python
component_schema: Dict[Phase, ComponentSchema] = {
    "plot": {"main": {"s", "alpha", "color", "marker"}},
    "axes": {"title": {"text", "fontsize", "color"}},
    # NEW: plotter-specific parameters
    "plotter_specific": {
        "matplotlib_direct": {"linewidth", "linestyle", "zorder"},
        "layout_params": {"spacing", "padding", "margins"},
        "formatting": {"format_string", "precision", "units"},
    }
}
```

## 3. Theme System Integration Conflicts

### Precedence System Redesign

**Current System**:
```python
component_kwargs > group_styles > plot_styles > base_styles
```

**Proposed System**:
```python
component_kwargs > group_styles > plotter_kwargs > plot_styles > base_styles
```

**Critical Conflicts**:

1. **Parameter Overlap**: When both `component_kwargs` and `plotter_kwargs` contain the same parameter, precedence becomes ambiguous
2. **Theme Inheritance Disruption**: plotter_kwargs would need to integrate with theme parent-child relationships
3. **Visual Channel Conflicts**: What happens when plotter_kwargs conflicts with visual channel styling?

### Theme Storage Redesign

**Current Theme Structure**:
```python
class Theme:
    plot_styles: PlotStyles
    axes_styles: AxesStyles
    figure_styles: FigureStyles
```

**Proposed Changes**:
```python
class Theme:
    plot_styles: PlotStyles
    axes_styles: AxesStyles  
    figure_styles: FigureStyles
    # NEW: Per-plotter overrides
    plotter_specific_styles: Dict[str, PlotStyles]
```

This would break the clean separation between theme definition and application.

### StyleApplicator Complexity Explosion

The StyleApplicator would need new logic for:
```python
def _resolve_plotter_kwargs_precedence(
    self, 
    plot_type: str,
    theme_styles: Dict[str, Any],
    plotter_kwargs: Dict[str, Any],
    component_kwargs: Dict[str, Any],
    group_styles: Dict[str, Any]
) -> Dict[str, Any]:
    # Complex precedence resolution
    # Conflict detection and resolution
    # Parameter validation  
    # Error reporting
```

## 4. Breaking Changes Analysis

### FigureManager API Changes

**BREAKING**: Constructor signature changes
```python
# OLD
fm = FigureManager(figure=config, theme=theme)

# NEW  
fm = FigureManager(
    figure=config, 
    theme=theme,
    plotter_kwargs={"scatter": {"s": 100}, "line": {"linewidth": 3}}
)
```

**BREAKING**: Parameter precedence changes
```python
# OLD behavior
fm.plot("scatter", data=df, s=50)  # s=50 takes highest precedence

# NEW behavior  
fm.plot("scatter", data=df, s=50)  # Precedence now depends on plotter_kwargs configuration
```

### Theme System Breaking Changes

**BREAKING**: Theme inheritance behavior changes
```python
# OLD
CUSTOM_THEME = Theme(parent=BASE_THEME, plot_styles=PlotStyles(alpha=0.8))

# NEW - Potentially different behavior
CUSTOM_THEME = Theme(
    parent=BASE_THEME, 
    plot_styles=PlotStyles(alpha=0.8),
    plotter_specific_styles={"scatter": PlotStyles(alpha=0.6)}  # Which wins?
)
```

**BREAKING**: StyleApplicator precedence changes
- Existing themes might resolve parameters differently
- Group styling behavior could change
- Component kwargs precedence could shift

### Plotter Implementation Changes

**BREAKING**: All plotter constructors require updates
```python
# OLD
class ScatterPlotter(BasePlotter):
    def __init__(self, data, grouping_cfg, theme=None, figure_manager=None, **kwargs):

# NEW
class ScatterPlotter(BasePlotter):
    def __init__(self, data, grouping_cfg, theme=None, figure_manager=None, 
                 plotter_kwargs=None, **kwargs):
```

**BREAKING**: `_filtered_plot_kwargs` behavior changes
- Parameter filtering logic would change
- Direct matplotlib parameter passing would be controlled
- New validation requirements

## 5. User Migration Complexity

### Code Patterns That Would Break

**Direct Parameter Usage**:
```python
# OLD - Works
fm.plot("scatter", data=df, s=100, alpha=0.7, color="red")

# NEW - Behavior changes
fm.plot("scatter", data=df, s=100, alpha=0.7, color="red")  # Precedence unclear
```

**Theme-Based Styling**:
```python
# OLD - Clear precedence
THEME = Theme(plot_styles=PlotStyles(alpha=0.8))
fm = FigureManager(theme=THEME)
fm.plot("scatter", data=df, alpha=0.6)  # alpha=0.6 wins

# NEW - Confusing precedence
fm = FigureManager(
    theme=THEME, 
    plotter_kwargs={"scatter": {"alpha": 0.5}}
)
fm.plot("scatter", data=df, alpha=0.6)  # Which alpha wins?
```

**Complex Theme Hierarchies**:
```python
# OLD - Clear inheritance
BASE = Theme(plot_styles=PlotStyles(linewidth=2))
CUSTOM = Theme(parent=BASE, plot_styles=PlotStyles(alpha=0.8))

# NEW - Unclear interaction
BASE = Theme(plot_styles=PlotStyles(linewidth=2))
CUSTOM = Theme(
    parent=BASE, 
    plot_styles=PlotStyles(alpha=0.8),
    plotter_specific_styles={"line": {"linewidth": 3}}
)
```

### Migration Path Requirements

Users would need to:
1. **Audit all theme definitions** for parameter conflicts with plotter_kwargs
2. **Update all direct parameter usage** to understand new precedence rules
3. **Modify complex styling logic** to account for three-tier parameter system
4. **Learn new debugging techniques** for parameter routing issues
5. **Rewrite theme inheritance patterns** to work with plotter-specific overrides

## 6. Testing and Validation Impact

### Test Coverage Explosion

**New Test Categories Needed**:
1. **Parameter Precedence Tests**: Every combination of theme/plotter_kwargs/component_kwargs
2. **Conflict Resolution Tests**: Behavior when parameters appear in multiple sources
3. **Validation Tests**: plotter_kwargs validation against component schemas
4. **Migration Tests**: Ensuring existing behavior is preserved where expected
5. **Performance Tests**: Impact of additional parameter routing logic

**Existing Test Updates**:
- Every plotter test needs plotter_kwargs variants
- Theme system tests need precedence validation
- StyleApplicator tests need complex precedence scenarios
- Integration tests need multi-layer parameter scenarios

### Validation System Requirements

**New Validation Logic**:
```python
class PlotterKwargsValidator:
    def validate_against_schema(
        self, 
        plot_type: str, 
        plotter_kwargs: Dict[str, Any]
    ) -> ValidationResult:
        # Validate parameters are supported by plotter
        # Check for conflicts with visual channels
        # Warn about theme overrides
        # Provide helpful error messages
```

## 7. Documentation Impact

### Complete Documentation Rewrite Required

**Affected Documentation**:
1. **Theme System Docs**: Complete rewrite to explain three-tier precedence
2. **Plotter Docs**: Every plotter would need plotter_kwargs examples
3. **Parameter Reference**: New categorization of theme vs plotter_kwargs parameters
4. **Migration Guide**: Extensive guide for upgrading existing code
5. **Advanced Usage**: Complex precedence rules and conflict resolution

**New User Guidance Needed**:
1. **When to use themes vs plotter_kwargs**: Decision flowchart
2. **Parameter precedence debugging**: Tools and techniques
3. **Best practices**: Avoiding parameter conflicts
4. **Performance considerations**: Impact of complex parameter routing

### Example Updates Required

**All 25 example files would need updates**:
- Show plotter_kwargs usage patterns
- Demonstrate precedence rules
- Illustrate conflict resolution
- Show migration from old patterns

## 8. Implementation Scope and Risk Assessment

### Complexity Estimate

**High Complexity Components**:
- **StyleApplicator Redesign**: ~1000+ lines of complex precedence logic
- **Theme System Integration**: ~500+ lines of inheritance and override logic  
- **Parameter Validation Framework**: ~800+ lines of validation and error handling
- **Plotter Constructor Updates**: ~50+ lines per plotter × 12 plotters
- **Test Suite Expansion**: ~2000+ lines of new test coverage

**Total Estimated Impact**: ~5000+ lines of new/modified code across core systems

### Risk Categories

**High Risk**:
1. **System Complexity**: Multi-tier parameter system becomes unmaintainable
2. **User Experience**: Confusion about parameter routing and precedence rules
3. **Breaking Changes**: Extensive user code requires updates with unclear migration path
4. **Performance Impact**: Additional parameter routing logic in hot paths
5. **Maintenance Burden**: Complex precedence rules create ongoing debugging challenges

**Medium Risk**:
1. **Theme System Fragility**: Changes to theme inheritance could introduce subtle bugs
2. **Documentation Debt**: Extensive documentation updates required
3. **Testing Complexity**: Exponential growth in test scenario combinations

**Low Risk**:
1. **Component Schema Extensions**: Relatively straightforward additions
2. **Plotter Registration**: Existing patterns can be extended

## 9. Alternative Approaches

### Less Disruptive Solutions

**1. Theme System Extensions**:
```python
# Extend existing theme categories instead of adding plotter_kwargs
class ExtendedTheme(Theme):
    matplotlib_styles: Dict[str, Any]  # Direct matplotlib parameters
    layout_styles: LayoutStyles         # Layout-specific parameters  
    formatting_styles: FormattingStyles # Format-specific parameters
```

**2. Plotter-Specific Theme Variants**:
```python
# Create specialized themes instead of plotter_kwargs
SCATTER_DETAILED_THEME = Theme(
    parent=BASE_THEME,
    plot_styles=PlotStyles(s=100, alpha=0.8, edgecolors="black")
)
```

**3. Helper Function Approach**:
```python
# Utility functions for common parameter patterns
def configure_scatter_styling(s=50, alpha=0.8, **kwargs):
    return {"s": s, "alpha": alpha, **kwargs}

fm.plot("scatter", data=df, **configure_scatter_styling(s=100))
```

## 10. Final Recommendations

### Assessment: **DO NOT PROCEED**

Based on this comprehensive analysis, implementing systematic plotter_kwargs routing would:

1. **Break Core Design Principles**: dr_plotter's clean theme-based styling system
2. **Introduce Excessive Complexity**: Multi-tier parameter precedence system
3. **Create User Experience Problems**: Confusing parameter routing and debugging
4. **Require Massive Breaking Changes**: Extensive user code migration required
5. **Add Maintenance Burden**: Complex precedence rules and validation logic

### Recommended Alternative: **Incremental Theme System Improvements**

Instead of plotter_kwargs routing, consider:

1. **Expand Theme Categories**: Add `matplotlib_styles`, `layout_styles`, `formatting_styles` to Theme
2. **Improve Parameter Documentation**: Better guidance on theme vs direct parameter usage  
3. **Add Theme Debugging Tools**: Utilities to inspect parameter resolution
4. **Create Parameter Helper Functions**: Common parameter pattern utilities
5. **Enhance Component Schemas**: Better parameter discovery and validation

These approaches would solve the "stranded parameters" problem without breaking the existing architecture or user experience.

## Conclusion

The proposed plotter_kwargs routing system would require fundamental changes to dr_plotter's core architecture that would break its clean design, introduce significant complexity, and create extensive user migration challenges. The existing theme system, while having some parameter routing limitations, provides a solid foundation that can be incrementally improved without the risks associated with the plotter_kwargs approach.

The cost-benefit analysis strongly favors **incremental improvements to the existing theme system** over implementing the proposed plotter_kwargs routing architecture.
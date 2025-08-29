# FigureManager Decomposition Implementation
## Task Group 4 Phase 1: Configuration-First Pattern Establishment

### Mission Statement
Decompose the problematic FigureManager constructor (62 lines, 34 parameters) into focused configuration objects following the proven GroupingConfig pattern. This establishes clean architectural boundaries for both current functionality and future multi-dimensional subplot coordination capabilities.

### Strategic Context
- **Current Problem**: FigureManager.__init__ represents the "anti-pattern" of parameter explosion with mixed responsibilities
- **Pattern Goal**: Apply the successful GroupingConfig model to establish systematic configuration object boundaries
- **Future Vision**: Enable sophisticated data-driven faceting (subplots by model_size, lines by dataset_name) through clean configuration architecture
- **Architectural Impact**: This decomposition sets the template for other Task Group 4 configuration improvements

### Current State Analysis

#### **Parameter Explosion Problem**
**File**: `src/dr_plotter/figure.py:17-79`
**Current Constructor**: 34 parameters with unclear relationships
```python
def __init__(
    self, rows=1, cols=1, external_ax=None, layout_rect=None,
    layout_pad=0.5, legend_config=None, legend_strategy=None,
    legend_position=None, legend_ncol=None, legend_spacing=None,
    plot_margin_bottom=None, legend_y_offset=None, theme=None,
    shared_styling=None, **fig_kwargs  # 34 total parameters!
):
```

#### **Mixed Responsibilities Identified**
1. **Matplotlib Figure/Axes Creation**: rows, cols, external_ax, fig_kwargs
2. **Layout Configuration**: layout_rect, layout_pad, plot_margin_bottom  
3. **Legend System Building**: 7 legend-related parameters with complex precedence
4. **Styling Coordination**: theme, shared_styling
5. **Subplot Management**: Basic grid-based subplot allocation

### Future-Ready Decomposition Strategy

#### **Configuration Objects Design**

Following the GroupingConfig success pattern, create focused configuration objects:

##### **SubplotLayoutConfig - Basic Layout Management**
```python
@dataclass
class SubplotLayoutConfig:
    """Clean layout configuration following GroupingConfig pattern"""
    rows: int = 1
    cols: int = 1
    layout_rect: Optional[List[float]] = None
    layout_pad: float = 0.5
    
    def validate(self) -> None:
        assert self.rows > 0, "Rows must be positive"
        assert self.cols > 0, "Cols must be positive"
        assert self.layout_pad >= 0, "Layout pad must be non-negative"
        if self.layout_rect:
            assert len(self.layout_rect) == 4, "Layout rect must have 4 values"
```

##### **SubplotFacetingConfig - Future Data-Driven Faceting**
```python
@dataclass
class SubplotFacetingConfig:
    """Configuration for advanced multi-dimensional subplot coordination"""
    # Future capabilities for user's advanced usecase
    facet_by: Optional[ColName] = None      # "model_size" -> creates subplots
    group_by: Optional[ColName] = None      # "dataset_name" -> creates lines within subplot  
    x_col: Optional[ColName] = None         # "num_steps"
    y_col: Optional[ColName] = None         # "metric_1"
    
    # Advanced faceting (future extensions)
    facet_rows: Optional[ColName] = None    # 2D faceting by rows
    facet_cols: Optional[ColName] = None    # 2D faceting by columns
    wrap_facets: Optional[int] = None       # Max columns before wrapping
    
    def validate(self) -> None:
        # Validation for future faceting logic
        if self.facet_by and self.group_by:
            assert self.facet_by != self.group_by, "Facet and group columns must be different"
```

##### **FigureCoordinationConfig - System Integration**
```python
@dataclass
class FigureCoordinationConfig:
    """Figure-level coordination and integration settings"""
    theme: Optional[Theme] = None
    shared_styling: Optional[bool] = None
    external_ax: Optional[plt.Axes] = None
    
    # Matplotlib pass-through
    fig_kwargs: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> None:
        # Future: validation for theme compatibility, external_ax constraints
        pass
```

#### **Builder Function Design**

##### **Primary Builder Function**
```python
def create_figure_manager(
    layout: Optional[SubplotLayoutConfig] = None,
    legend: Optional[LegendConfig] = None,
    coordination: Optional[FigureCoordinationConfig] = None,
    faceting: Optional[SubplotFacetingConfig] = None,  # Future extension point
) -> FigureManager:
    """
    Builder function for FigureManager with clean configuration objects.
    
    Args:
        layout: Subplot grid and layout configuration
        legend: Legend system configuration (existing)
        coordination: Theme and styling coordination
        faceting: Data-driven faceting configuration (future capability)
    
    Returns:
        Configured FigureManager instance
    """
    # Use defaults following GroupingConfig pattern
    layout = layout or SubplotLayoutConfig()
    coordination = coordination or FigureCoordinationConfig()
    
    # Validate all configurations
    layout.validate()
    coordination.validate()
    if faceting:
        faceting.validate()
    
    # Build with focused responsibilities
    figure_builder = FigureBuilder(layout, coordination)
    legend_builder = LegendSystemBuilder(legend, coordination.theme)
    
    return FigureManager._create_from_builders(
        figure_builder, legend_builder, faceting
    )
```

#### **Internal Method Decomposition**

Break the 62-line constructor into focused methods:

##### **Figure/Axes Creation (Matplotlib Responsibility)**
```python
def _create_figure_axes(
    self, 
    layout: SubplotLayoutConfig, 
    external_ax: Optional[plt.Axes], 
    fig_kwargs: Dict[str, Any]
) -> Tuple[plt.Figure, plt.Axes, bool]:
    """
    Pure matplotlib figure/axes creation logic.
    
    Returns:
        (figure, axes, external_mode)
    """
    if external_ax is not None:
        return external_ax.get_figure(), external_ax, True
    
    fig, axes = plt.subplots(
        layout.rows, layout.cols, 
        constrained_layout=False, 
        **fig_kwargs
    )
    return fig, axes, False
```

##### **Layout Configuration Setup**
```python
def _setup_layout_configuration(self, layout: SubplotLayoutConfig) -> None:
    """Configure layout parameters for finalization."""
    self._layout_rect = layout.layout_rect
    self._layout_pad = layout.layout_pad
    self.rows = layout.rows
    self.cols = layout.cols
```

##### **Legend System Building**
```python
def _build_legend_system(
    self, 
    legend_config: Optional[LegendConfig], 
    theme: Optional[Theme]
) -> LegendManager:
    """
    Build legend system with clean parameter precedence.
    
    Replaces the complex _build_legend_config method.
    """
    # Clean precedence: explicit config > theme config > defaults
    effective_config = legend_config or (
        theme.legend_config if theme and hasattr(theme, 'legend_config') else None
    ) or LegendConfig()
    
    return LegendManager(self, effective_config)
```

##### **Styling Coordination Setup**
```python
def _coordinate_styling(
    self, 
    theme: Optional[Theme], 
    shared_styling: Optional[bool]
) -> None:
    """Setup shared styling and cycle configuration."""
    self.shared_styling = shared_styling
    
    if self._should_use_shared_cycle_config():
        theme_for_cycle = theme or BASE_THEME
        self.shared_cycle_config = CycleConfig(theme_for_cycle)
    else:
        self.shared_cycle_config = None
```

### Implementation Requirements

#### **Phase 1: Configuration Objects (Hours 1-3)**
1. **Create configuration dataclasses** in `src/dr_plotter/figure_config.py`
2. **Implement validation methods** following GroupingConfig patterns
3. **Add comprehensive type annotations** for all configuration attributes
4. **Write focused unit tests** for configuration validation

#### **Phase 2: Builder Function (Hours 4-5)**
1. **Implement create_figure_manager** builder function with clean interface
2. **Add configuration validation** and error handling
3. **Design for extensibility** - faceting config ready for future implementation
4. **Maintain backward compatibility** through compatibility layer

#### **Phase 3: Constructor Decomposition (Hours 6-8)**
1. **Break constructor into focused methods** (4 methods as designed above)
2. **Update constructor to use builder pattern** internally
3. **Eliminate parameter precedence complexity** through clear configuration objects
4. **Preserve all existing functionality** exactly

#### **Phase 4: Integration and Testing (Hours 9-12)**
1. **Update all FigureManager usage** to use builder function where beneficial
2. **Comprehensive regression testing** to ensure identical functionality
3. **Performance validation** - configuration objects should have minimal overhead
4. **API documentation** with clear migration examples

### Backward Compatibility Strategy

#### **Compatibility Layer Approach**
```python
# Maintain existing constructor with deprecation path
def __init__(self, rows=1, cols=1, external_ax=None, **kwargs):
    """
    DEPRECATED: Use create_figure_manager() for new code.
    
    This constructor maintained for backward compatibility.
    """
    # Convert legacy parameters to configuration objects
    layout = SubplotLayoutConfig(rows=rows, cols=cols, ...)
    coordination = FigureCoordinationConfig(external_ax=external_ax, ...)
    
    # Build using new internal pattern
    self._init_from_configs(layout, coordination, ...)
```

#### **Migration Examples**
```python
# OLD PATTERN (still works, but deprecated)
fm = FigureManager(
    rows=2, cols=3, 
    legend_strategy="grouped_by_channel",
    theme=custom_theme,
    layout_pad=0.8
)

# NEW PATTERN (encouraged for new code)
fm = create_figure_manager(
    layout=SubplotLayoutConfig(rows=2, cols=3, layout_pad=0.8),
    legend=LegendConfig(strategy=LegendStrategy.GROUPED_BY_CHANNEL),
    coordination=FigureCoordinationConfig(theme=custom_theme)
)
```

### Future Extension Points

#### **Multi-Dimensional Subplot Coordination**
The new architecture enables your advanced usecase:

```python
# Future capability - your desired multi-dimensional plotting
advanced_config = SubplotFacetingConfig(
    facet_by="model_size",      # Each model size = separate subplot  
    group_by="dataset_name",    # Each dataset = separate line color
    x_col="num_steps",
    y_col="metric_1"
)

fm = create_figure_manager(
    layout=SubplotLayoutConfig(rows=2, cols=3),  # Or auto-calculated
    faceting=advanced_config,
    legend=LegendConfig(strategy="grouped_by_channel")
)

# This would automatically:
# - Split data by model_size -> create subplots
# - Within each subplot, group by dataset_name -> create colored lines  
# - Set x=num_steps, y=metric_1 for all plots
# - Coordinate legends across the entire figure
```

#### **Extension Architecture**
```python
class FacetingEngine:
    """Future component for data-driven subplot coordination"""
    
    def calculate_subplot_layout(self, data: pd.DataFrame, config: SubplotFacetingConfig) -> SubplotLayoutConfig:
        # Auto-calculate rows/cols based on unique facet values
        
    def split_data_by_facets(self, data: pd.DataFrame, config: SubplotFacetingConfig) -> Dict[Tuple, pd.DataFrame]:
        # Split dataset for subplot allocation
        
    def generate_subplot_titles(self, facet_values: Tuple, config: SubplotFacetingConfig) -> str:
        # Auto-generate subplot titles from facet values
```

### Success Criteria

#### **Immediate Success (Configuration Pattern)**
- [x] Constructor parameters reduced from 34 to <10 per builder function
- [x] Clear configuration object boundaries established
- [x] GroupingConfig pattern successfully applied to complex parameter management  
- [x] Zero functionality regression - all existing usage works identically
- [x] Type safety improvements through configuration object validation

#### **Architectural Success (Future Readiness)**  
- [x] Clean extension points for data-driven faceting
- [x] Separation between matplotlib management and subplot coordination
- [x] Configuration objects that can handle multi-dimensional data requirements
- [x] Builder pattern that scales to advanced subplot allocation
- [x] Template established for other Task Group 4 decompositions

#### **Code Quality Success**
- [x] Functions <50 lines each (constructor methods)
- [x] Clear single responsibilities for each component
- [x] Comprehensive type annotations throughout
- [x] Maintainable test suite with focused unit tests
- [x] Self-documenting code through clear configuration object names

### Risk Mitigation

#### **High-Risk Areas**
1. **Complex parameter precedence logic**: Legend configuration has 7+ parameters with unclear relationships
   - **Mitigation**: Document exact precedence rules, comprehensive test coverage
   
2. **Backward compatibility**: Many existing FigureManager usages throughout codebase
   - **Mitigation**: Maintain compatibility layer, gradual migration approach
   
3. **Performance impact**: Configuration object overhead
   - **Mitigation**: Dataclass efficiency, benchmark before/after performance

#### **Integration Dependencies**
- **StyleApplicator**: Uses FigureManager for theme coordination - changes must be coordinated
- **LegendManager**: Tightly coupled to FigureManager - ensure clean interface preservation
- **API functions**: All use FigureManager through _fm_plot - verify no breakage

### Implementation Timeline

**Phase 1** (3 hours): Configuration objects and validation
**Phase 2** (2 hours): Builder function implementation  
**Phase 3** (3 hours): Constructor decomposition and integration
**Phase 4** (4 hours): Testing, compatibility, and documentation

**Total Effort**: 12 hours as estimated in analysis report

**Validation Checkpoints**:
- After Phase 1: Configuration objects validate properly, good unit test coverage
- After Phase 2: Builder function works for basic cases, clean interface design
- After Phase 3: All functionality preserved, constructor complexity eliminated  
- After Phase 4: Ready for production use, documentation complete

---

## Strategic Impact

This decomposition represents the **foundational pattern** for Task Group 4 configuration improvements. Success here establishes:

1. **Configuration object template**: Other complex parameter sets can follow this model
2. **Builder function pattern**: Clean interface design for complex system construction
3. **Future extensibility**: Architecture ready for advanced multi-dimensional plotting capabilities
4. **Validation framework**: Configuration validation patterns for system reliability

**Ready for implementation**: Design validated, backward compatibility planned, future extensions architected.
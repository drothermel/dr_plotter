# Architecture Inventory: Configuration Infrastructure Analysis

## Configuration Classes Found

### LegendConfig
- **Location**: src/dr_plotter/legend_manager.py:62
- **Parameters**: 
  - `strategy: LegendStrategy = LegendStrategy.PER_AXES`
  - `collect_strategy: str = "smart"`
  - `position: str = "lower center"`
  - `deduplication: bool = True`
  - `ncol: Optional[int] = None`
  - `max_col: int = 4`
  - `spacing: float = 0.1`
  - `remove_axes_legends: bool = True`
  - `layout_left_margin: float = 0.0`
  - `layout_bottom_margin: float = 0.15`
  - `layout_right_margin: float = 1.0`
  - `layout_top_margin: float = 0.95`
  - `bbox_y_offset: float = 0.08`
  - `single_legend_x: float = 0.5`
  - `two_legend_left_x: float = 0.25`
  - `two_legend_right_x: float = 0.75`
  - `multi_legend_start_x: float = 0.15`
  - `multi_legend_spacing: float = 0.35`
- **Purpose**: Comprehensive legend configuration including strategy, positioning, layout margins, and multi-legend coordination
- **Current Usage**: Accepted by FigureManager constructor, processed via `_convert_legacy_legend_params()`, controls legend management system

### SubplotLayoutConfig
- **Location**: src/dr_plotter/figure_config.py:13
- **Parameters**:
  - `rows: int = 1`
  - `cols: int = 1` 
  - `layout_rect: Optional[List[float]] = None`
  - `layout_pad: float = 0.5`
- **Purpose**: Controls subplot grid layout and spacing
- **Current Usage**: Created internally by FigureManager from individual parameters (`rows`, `cols`, `layout_rect`, `layout_pad`)

### SubplotFacetingConfig  
- **Location**: src/dr_plotter/figure_config.py:35
- **Parameters**:
  - `facet_by: Optional[ColName] = None`
  - `group_by: Optional[ColName] = None`
  - `x_col: Optional[ColName] = None`
  - `y_col: Optional[ColName] = None`
  - `facet_rows: Optional[ColName] = None`
  - `facet_cols: Optional[ColName] = None`
  - `wrap_facets: Optional[int] = None`
- **Purpose**: Configuration for future faceted plotting functionality
- **Current Usage**: Defined but not yet used by FigureManager - appears to be prepared infrastructure

### FigureCoordinationConfig
- **Location**: src/dr_plotter/figure_config.py:57
- **Parameters**:
  - `theme: Optional[Theme] = None`
  - `shared_styling: Optional[bool] = None`
  - `external_ax: Optional[plt.Axes] = None`
  - `fig_kwargs: Dict[str, Any] = field(default_factory=dict)`
- **Purpose**: Figure-level coordination and matplotlib integration
- **Current Usage**: Created internally by FigureManager from individual parameters (`theme`, `shared_styling`, `external_ax`, `**fig_kwargs`)

### CycleConfig
- **Location**: src/dr_plotter/cycle_config.py:14
- **Parameters**: Not dataclass - uses dynamic cycle management
  - `theme: Theme` (constructor)
  - `_cycles: Dict[VisualChannel, Any]` (internal cycle storage)
  - `_value_assignments: Dict[StyleCacheKey, Any]` (internal assignment cache)
- **Purpose**: Manages visual style cycles (colors, markers, line styles) for consistent styling across plots
- **Current Usage**: Used by StyleEngine for style value assignment, not directly exposed to FigureManager

### GroupingConfig
- **Location**: src/dr_plotter/grouping_config.py:8
- **Parameters**:
  - `hue: Optional[ColName] = None`
  - `style: Optional[ColName] = None`
  - `size: Optional[ColName] = None`
  - `marker: Optional[ColName] = None`
  - `alpha: Optional[ColName] = None`
- **Purpose**: Maps visual channels to data columns for aesthetic grouping
- **Current Usage**: Used by plotting system for visual channel management, not directly exposed to FigureManager

## Dataclasses Discovered

### LegendEntry
- **Location**: src/dr_plotter/legend_manager.py:14
- **Fields**: `artist: Any`, `label: str`, `axis: Any = None`, `visual_channel: Optional[str] = None`, `channel_value: Any = None`, `group_key: Dict[str, Any] = field(default_factory=dict)`, `plotter_type: str = "unknown"`, `artist_type: str = "main"`
- **Usage**: Internal legend system for tracking legend entries
- **Parameter Grouping**: Legend entry metadata and artist tracking

### ChannelSpec
- **Location**: src/dr_plotter/channel_metadata.py:6
- **Fields**: `name: str`, `channel_type: Literal["categorical", "continuous"]`, `legend_behavior: Literal["per_value", "min_max", "none"]`
- **Usage**: Metadata for visual channel specifications
- **Parameter Grouping**: Visual channel behavior configuration

## Style System Components

### Theme Class
- **Location**: src/dr_plotter/theme.py:61
- **Responsibilities**: Central theme management with inheritance, style composition, and integration with legend configuration
- **Key Features**: Parent theme inheritance, style type categorization (plot/post/axes/figure), LegendConfig integration

### Style Classes
- **PlotStyles** (src/dr_plotter/theme.py:45): Plot-phase styling parameters
- **PostStyles** (src/dr_plotter/theme.py:49): Post-plot styling parameters  
- **AxesStyles** (src/dr_plotter/theme.py:53): Axes-level styling parameters
- **FigureStyles** (src/dr_plotter/theme.py:57): Figure-level styling parameters
- **Style** (src/dr_plotter/theme.py:18): Base style class with generic style storage

### Style Integration Infrastructure
- **StyleApplicator** (src/dr_plotter/style_applicator.py:15): Applies theme styles to plot components
- **StyleEngine** (src/dr_plotter/plotters/style_engine.py:10): Manages cycle configuration and continuous style ranges
- **BASE_THEME**: Comprehensive default theme with color cycles, style cycles, and default parameters

## FigureManager Integration Analysis

### Current Config Parameters
**Directly Accepted**:
- `legend_config: Optional[LegendConfig]` - Full legend configuration object
- `theme: Optional[Any]` - Theme object for styling

**Legacy Parameters Converted to Config Objects**:
- Individual legend parameters → `LegendConfig` via `_convert_legacy_legend_params()`
- Layout parameters → `SubplotLayoutConfig` internally  
- Coordination parameters → `FigureCoordinationConfig` internally

### Parameter Processing
1. **LegendConfig**: Processed via `_convert_legacy_legend_params()` and `_build_legend_config()`
2. **Layout Parameters**: Converted to `SubplotLayoutConfig` in constructor
3. **Theme Integration**: Theme object passed to coordination config and used by style system
4. **Legacy Bridge**: Individual parameters converted to appropriate config objects for backward compatibility

### Missing Integrations
- **SubplotFacetingConfig**: Defined but not used by FigureManager
- **GroupingConfig**: Used by plotting system but not exposed at FigureManager level
- **CycleConfig**: Used internally by StyleEngine but not directly configurable via FigureManager

## Architectural Patterns Identified

### Parameter Grouping Strategy
1. **Semantic Grouping**: Parameters grouped by functional area (legend, layout, coordination, faceting)
2. **Config Object Pattern**: Dataclass-based configuration objects with validation methods
3. **Legacy Bridge Pattern**: Individual parameters converted to config objects for backward compatibility
4. **Hierarchical Organization**: Theme system with inheritance and style type categorization

### Integration Approach
1. **Constructor Conversion**: FigureManager converts individual parameters to config objects internally
2. **Theme Integration**: Theme object provides unified styling across all components
3. **Validation Pipeline**: Config objects have `validate()` methods for parameter checking
4. **Factory Functions**: `create_figure_manager()` function provides config-first interface

### Design Principles
1. **Backward Compatibility**: Legacy individual parameters preserved alongside config objects
2. **Progressive Enhancement**: Config objects provide richer functionality than individual parameters
3. **Separation of Concerns**: Different config objects handle different aspects (layout, legend, coordination, faceting)
4. **Validation at Boundaries**: Config objects validate parameters at construction time

## Gap Analysis

### Ungrouped Parameters (Current FigureManager individual parameters)
**Layout-Related** (have SubplotLayoutConfig but used individually):
- `rows: int`, `cols: int`, `layout_rect: Optional[List[float]]`, `layout_pad: Optional[float]`

**Legend-Related** (have LegendConfig but used individually): 
- `legend_strategy`, `legend_position`, `legend_ncol`, `legend_spacing`, `plot_margin_bottom`, `plot_margin_top`, `legend_y_offset`

**Matplotlib Pass-through**:
- `**fig_kwargs` (figsize, dpi, facecolor, etc.)

**New Parameters Added During Phase 2**:
- No additional config object integration for newly added parameters

### Missing Config Classes
1. **MatplotlibConfig**: For `figsize`, `dpi`, `facecolor`, `sharex`, `sharey` and other matplotlib-specific parameters
2. **LayoutMarginConfig**: For plot margins (`plot_margin_top`, `plot_margin_bottom`, `plot_margin_left`, `plot_margin_right`)
3. **AxisSharingConfig**: For `sharex`, `sharey`, and related subplot coordination parameters

### Integration Opportunities
1. **SubplotFacetingConfig**: Ready for integration but not yet used - could enable Phase 3 faceted plotting API
2. **Config-First Constructor**: Alternative FigureManager constructor accepting config objects directly
3. **Theme-Config Integration**: Tighter integration between theme system and config object defaults
4. **Parameter Validation Unification**: Centralized validation across all config objects

## Key Findings

### Architectural Strengths
- **Rich Configuration Infrastructure**: Comprehensive config object system already exists
- **Theme System Integration**: Sophisticated theming with proper inheritance and style categorization
- **Legacy Compatibility**: Smooth transition path from individual parameters to config objects
- **Validation Framework**: Built-in validation methods in config objects

### Current State Assessment
- **Partial Migration**: FigureManager uses config objects internally but still primarily accepts individual parameters
- **Theme-First Design**: Theme system is mature and well-integrated
- **Faceting Infrastructure Ready**: SubplotFacetingConfig exists but unused - ready for Phase 3
- **Missing Parameter Organization**: Several parameter groups still need config object homes

### Strategic Implications for Phase 1b
- **Build on Existing**: Strong config infrastructure exists - extend rather than replace
- **Complete Migration**: Move FigureManager to config-first approach with legacy bridges
- **Leverage Faceting Config**: SubplotFacetingConfig provides foundation for Phase 3 faceted plotting
- **Address Missing Configs**: Create MatplotlibConfig, LayoutMarginConfig for remaining ungrouped parameters
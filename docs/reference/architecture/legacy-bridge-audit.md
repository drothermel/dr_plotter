# Legacy Bridge Code Audit: Comprehensive Removal Analysis

## FigureManager Individual Parameters

### Constructor Signature Analysis
**Current Parameters** (Complete list with types and defaults):
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
    legend_position: Optional[str] = None,
    legend_ncol: Optional[int] = None,
    legend_spacing: Optional[float] = None,
    plot_margin_bottom: Optional[float] = None,
    plot_margin_top: Optional[float] = None,
    legend_y_offset: Optional[float] = None,
    theme: Optional[Any] = None,
    shared_styling: Optional[bool] = None,
    **fig_kwargs: Any,
)
```

**Parameter Categories**:
- **Layout Parameters**: `rows`, `cols`, `layout_rect`, `layout_pad` 
- **Legend Individual Parameters**: `legend_strategy`, `legend_position`, `legend_ncol`, `legend_spacing`, `plot_margin_bottom`, `plot_margin_top`, `legend_y_offset`
- **Config Objects**: `legend_config` (hybrid - both individual params and config object accepted)
- **Coordination Parameters**: `external_ax`, `theme`, `shared_styling`
- **Matplotlib Pass-through**: `**fig_kwargs` (figsize, dpi, facecolor, etc.)

**Complex Parameters**:
- `legend_strategy`: Requires string-to-enum conversion (`"figure_below"` → `LegendStrategy.FIGURE_BELOW`)
- `layout_pad`: Has special default handling (`layout_pad if layout_pad is not None else 0.5`)
- `**fig_kwargs`: Pass-through dictionary requiring special handling
- `theme`: Integrates with both coordination config and legend config resolution

### Parameter Processing Logic
**Validation**: 
- Config object validation via `layout.validate()`, `coordination.validate()` methods
- No validation of individual parameters before config conversion
- Parameter validation happens at config object construction time

**Transformation**:
- `layout_pad` special default processing: `layout_pad_final = layout_pad if layout_pad is not None else 0.5`
- Legend strategy string mapping: `"figure_below"` → `LegendStrategy.FIGURE_BELOW` via `strategy_map` dictionary
- Theme integration in both coordination config and legend config building

**Defaults**:
- Most individual parameters use `None` defaults with config object providing actual defaults
- Layout pad uses explicit default fallback pattern
- Config objects provide structured default values

## Legacy Bridge Methods Found

### _convert_legacy_legend_params()
- **Location**: src/dr_plotter/figure.py:71
- **Input Parameters**: `legend_config`, `legend_strategy`, `legend_position`, `legend_ncol`, `legend_spacing`, `plot_margin_bottom`, `plot_margin_top`, `legend_y_offset`, `theme`
- **Output**: `Optional[LegendConfig]`
- **Logic**: 
  - Short-circuits if no individual parameters provided (returns existing `legend_config`)
  - Calls `_build_legend_config()` with theme resolution logic
  - Handles theme.legend_config extraction via `hasattr()` check
- **Dependencies**: `_build_legend_config()`, theme object with potential `legend_config` attribute

### _build_legend_config()
- **Location**: src/dr_plotter/figure.py:209  
- **Input Parameters**: `base_config`, `legend_strategy`, `legend_position`, `legend_ncol`, `legend_spacing`, `plot_margin_bottom`, `plot_margin_top`, `legend_y_offset`
- **Output**: `LegendConfig`
- **Logic**:
  - Creates new `LegendConfig` copying from base_config if provided, else default config
  - Applies individual parameter overrides via field-by-field assignment
  - Performs string-to-enum conversion for `legend_strategy` via `strategy_map`
  - Maps individual parameters to config fields: `plot_margin_bottom` → `layout_bottom_margin`, etc.
- **Dependencies**: `LegendConfig`, `LegendStrategy` enum, string mapping dictionary

### Config Object Creation Patterns (Internal)
**SubplotLayoutConfig Creation** (figure.py:43-48):
```python
layout = SubplotLayoutConfig(
    rows=rows,
    cols=cols,
    layout_rect=layout_rect,
    layout_pad=layout_pad_final,
)
```
- Direct parameter → config object constructor mapping
- Special handling for layout_pad default fallback

**FigureCoordinationConfig Creation** (figure.py:50-55):
```python
coordination = FigureCoordinationConfig(
    theme=theme,
    shared_styling=shared_styling,
    external_ax=external_ax,
    fig_kwargs=fig_kwargs,
)
```
- Direct parameter → config object constructor mapping
- Kwargs dictionary passed through directly

## Config Object Creation Analysis

### Internal Config Creation Patterns
**LegendConfig Creation**: 
- Via `_convert_legacy_legend_params()` → `_build_legend_config()` chain
- Handles existing config objects vs individual parameter conversion
- Theme integration via theme.legend_config extraction

**SubplotLayoutConfig Creation**: 
- Direct constructor call in `__init__()` with individual parameters
- Special layout_pad default handling before config creation
- No complex conversion logic needed

**FigureCoordinationConfig Creation**:
- Direct constructor call in `__init__()` with individual parameters
- Fig_kwargs dictionary passed through as-is
- No complex conversion logic needed

### Parameter → Config Mapping
**Legend Parameters**:
- `legend_strategy` → `config.strategy` (with enum conversion)
- `legend_position` → `config.position`
- `legend_ncol` → `config.ncol`
- `legend_spacing` → `config.spacing`
- `plot_margin_bottom` → `config.layout_bottom_margin`
- `plot_margin_top` → `config.layout_top_margin`
- `legend_y_offset` → `config.bbox_y_offset`

**Layout Parameters**:
- `rows` → `layout.rows`
- `cols` → `layout.cols`
- `layout_rect` → `layout.layout_rect`
- `layout_pad` → `layout.layout_pad`

**Coordination Parameters**:
- `theme` → `coordination.theme`
- `shared_styling` → `coordination.shared_styling`
- `external_ax` → `coordination.external_ax`
- `**fig_kwargs` → `coordination.fig_kwargs`

## Parameter Flow Analysis

### User Input → Internal Processing → Final Application
1. **User provides individual parameters** → FigureManager constructor
2. **Config object creation** → Direct constructor calls for layout and coordination configs
3. **Legacy parameter conversion** → `_convert_legacy_legend_params()` → `_build_legend_config()` for legend config
4. **Config application** → `_init_from_configs()` processes all config objects
5. **Final integration** → Config objects used by legend manager, matplotlib calls, theme system

### Integration Points
**Theme Integration**:
- Theme passed to both coordination config and legend config building
- Theme.legend_config extracted and used as base for legend config building
- Theme passed to `_coordinate_styling()` for style system integration

**Matplotlib Integration**:
- `fig_kwargs` passed through coordination config to `_create_figure_axes()`
- Layout parameters passed through layout config to matplotlib figure creation
- Legend config margins control matplotlib `tight_layout()` rect parameter

**Plotter Integration**:
- Config objects stored as instance attributes for plotter access
- Legend config accessible via `self.legend_config`
- Shared cycle config created based on theme and shared_styling setting

## Factory Function Analysis

### create_figure_manager() (figure_config.py:71)
**Current Interface**: Accepts only config objects
```python
def create_figure_manager(
    layout: Optional[SubplotLayoutConfig] = None,
    legend: Optional[LegendConfig] = None,
    coordination: Optional[FigureCoordinationConfig] = None,
    faceting: Optional[SubplotFacetingConfig] = None,
) -> "FigureManager":
```

**Processing**:
- Provides default config objects if None provided
- Calls validation on all config objects
- Uses `FigureManager._create_from_configs()` classmethod, bypassing legacy parameter handling entirely

**Key Difference**: 
- Factory function is already config-first, no individual parameters
- Uses private `_create_from_configs()` method that bypasses `__init__()`
- Represents the target API pattern for clean config-based construction

## Removal Impact Assessment

### Code Volume
**Lines to Remove**: ~100 lines
- `_convert_legacy_legend_params()` method: ~25 lines
- `_build_legend_config()` method: ~50 lines  
- Constructor parameter processing: ~15 lines
- Strategy mapping dictionary: ~8 lines
- Parameter conversion calls: ~10 lines

**Methods to Delete**: 2 major methods
- `_convert_legacy_legend_params()`
- `_build_legend_config()`

**Parameters to Eliminate**: 13 individual parameters
- Layout: `rows`, `cols`, `layout_rect`, `layout_pad`
- Legend: `legend_strategy`, `legend_position`, `legend_ncol`, `legend_spacing`, `plot_margin_bottom`, `plot_margin_top`, `legend_y_offset`  
- Coordination: `external_ax`, `theme`, `shared_styling`
- Special: `**fig_kwargs` handling

### Breaking Changes
**Constructor Changes**:
- Remove all individual parameters from `__init__()` signature
- Replace with config object parameters only: `layout`, `legend`, `coordination`, `faceting`
- Remove `**fig_kwargs` parameter entirely

**Method Removals**:
- `_convert_legacy_legend_params()` - private method, no external impact
- `_build_legend_config()` - private method, no external impact

**Behavior Changes**:
- No automatic parameter → config conversion
- No theme.legend_config extraction during construction
- No string-to-enum conversion for legend strategy
- No default fallback handling for individual parameters

### Dependencies

**Internal Dependencies**: 
- `_convert_legacy_legend_params()` called only from `__init__()`
- `_build_legend_config()` called only from `_convert_legacy_legend_params()`
- No other internal code calls these legacy methods

**External Dependencies** (Examples using individual parameters):
- `examples/06_faceted_training_curves.py`: `legend_strategy="figure_below"`, `legend_ncol`, `plot_margin_bottom`, `plot_margin_top`, `legend_y_offset`
- `examples/06b_faceted_training_curves_themed.py`: Same individual parameters
- `examples/10_legend_positioning.py`: `legend_strategy="figure_below"`, `legend_ncol`, `plot_margin_bottom`, `legend_y_offset`
- `src/dr_plotter/api.py`: `FigureManager(external_ax=ax)` - simple case
- **20+ example files**: Extensive usage of individual parameters throughout example codebase

**Migration Requirements**:
- All examples need conversion to config objects
- API module needs update for external_ax handling
- Documentation needs updates for new constructor interface

## Key Findings

### Legacy Code Scope
**Well-Isolated**: Legacy handling is concentrated in 2 private methods in FigureManager
**Systematic Pattern**: Clear parameter → config object conversion pattern for all parameter types
**Complete Coverage**: All individual parameters have config object homes

### Breaking Change Impact
**High External Impact**: 20+ example files using individual parameters
**Zero Internal Impact**: No other library code calls legacy methods
**Clean Separation**: Legacy bridge methods are self-contained and removable

### Config Infrastructure Readiness  
**Mature Architecture**: All config objects exist and have validation
**Factory Pattern Ready**: `create_figure_manager()` already implements target pattern
**Theme Integration**: Theme system ready for config-based construction

### Strategic Assessment
**Removal Feasibility**: High - all legacy code is isolated and identified
**Migration Path**: Clear - examples can be systematically converted to config objects  
**Architecture Benefit**: Significant - eliminates dual parameter/config complexity

The legacy bridge audit reveals that dr_plotter's parameter organization is 90% complete with config infrastructure. Legacy code is well-isolated in 2 methods and fully removable, but will require systematic migration of all example code to config objects.
# Axes & Plotter Parameter Routing Audit: Current Implementation Analysis

## Executive Summary

**Key Finding**: Dr_plotter has a sophisticated but incomplete parameter routing system. Current architecture handles most common parameters well, but several stranded parameters exist that should be accessible to users.

**Major Gap**: Heatmap-specific parameters (`format='int'`, `xlabel_pos`) exist in code but cannot be passed through user APIs.

## Current Axes Configuration Patterns

### ax.set_xlabel()/set_ylabel() Usage
- **Locations**: 
  - `src/dr_plotter/plotters/base.py:449` (xlabel via theme/style system)
  - `src/dr_plotter/plotters/base.py:466` (ylabel via theme/style system)
  - Examples: Manual overrides in `examples/06*.py:127,130`
- **Parameter source**: Two routes - theme system (`style_applicator.get_style_with_fallback()`) and direct example code access
- **User control**: Limited - examples show users manually calling `ax.set_xlabel()` after plotting

### ax.set_xlim()/set_ylim() Usage
- **Locations**: Only in example files (`examples/06*.py:141,144`)
- **Parameter source**: Direct user code after getting axes via `fm.get_axes()`
- **User control**: Manual post-plotting configuration only - no API integration

### ax.set_xscale()/set_yscale() Usage  
- **Locations**: Only in example files (`examples/06*.py:133,138`)
- **Parameter source**: Direct user access to axes
- **User control**: Manual configuration after plotting

### ax.grid() Usage
- **Locations**: `src/dr_plotter/plotters/base.py:480,489` (via theme system)
- **Parameter source**: Theme system integration via `style_applicator`
- **User control**: ✅ Well integrated - theme controls grid visibility, styling

### ax.tick_params() Usage
- **Locations**: `src/dr_plotter/plotters/heatmap.py:145,150` (heatmap-specific positioning)
- **Parameter source**: Hardcoded logic based on `xlabel_pos` theme parameter
- **User control**: ❌ Limited - only via theme, not direct parameter access

### Other axes functions
- **ax.set_xticks()/set_yticks()**: Used in multiple plotters for category positioning
- **ax.ticklabel_format()**: Only in examples - no theme/API integration
- **ax.set_title()**: Integrated via theme system in base.py:435

## Plotter-Specific Parameter Handling

### HeatmapPlotter Parameters
- **Parameters discovered**:
  - `values` (str): Column name for heatmap cell values - ✅ accessible
  - `annot` (bool): Enable cell annotations - ✅ accessible  
  - `format` (str): Cell text format (`.2f`, `int`) - ❌ stranded in `_style_cell_text()`, line 165
  - `xlabel_pos` (str): `"top"` or `"bottom"` positioning - ❌ theme-only access
  - `cmap`, `vmin`, `vmax`: Colormap parameters - ✅ accessible via kwargs
- **User access**: Direct parameters work, but `format` and `xlabel_pos` blocked
- **Blocked parameters**: `format='int'` exists in code but no API route

### LinePlotter Parameters  
- **Parameters discovered**: All standard matplotlib line parameters via component schema
- **Current routing**: ✅ Excellent - `color`, `linestyle`, `linewidth`, `marker`, etc. all accessible
- **User control**: Full access through kwargs and theme system

### BarPlotter Parameters
- **Parameters discovered**: Standard matplotlib bar parameters - `color`, `alpha`, `width`, etc.
- **Current routing**: ✅ Good integration via component schema and theme
- **User control**: Accessible through kwargs

### ViolinPlotter Parameters
- **Parameters discovered**: Complex plotter with custom positioning logic
- **Current routing**: Category positioning hardcoded in `_draw()` method
- **User control**: Limited customization of positioning logic

### ScatterPlotter Parameters  
- **Parameters discovered**: Standard scatter parameters + size channel integration
- **Current routing**: ✅ Excellent - includes continuous size mapping
- **User control**: Full access including multi-dimensional parameter mapping

## Parameter Flow Architecture

### From FigureManager.plot() to Plotters
1. **User calls**: `fm.plot("line", row, col, data, **kwargs)`
2. **Parameter routing**: `figure.py:246` → `_add_plot()` → Plotter constructor
3. **Plotter integration**: 
   - All `**kwargs` passed directly to plotter constructor (`base.py:90`)
   - `GroupingConfig` automatically created and set (`figure.py:236-237`)
   - `figure_manager` reference passed for coordination

### From Theme System to Axes/Plotters
1. **Theme parameter storage**: Component schemas define available parameters per plotter
2. **Application mechanism**: `StyleApplicator` resolves theme → explicit parameter precedence
3. **Conflict resolution**: ✅ Well designed - explicit parameters override theme defaults

### From Top-level API to Plotters
1. **API entry**: `dr_plotter.heatmap(data, x, y, values, **kwargs)`
2. **FigureManager creation**: `api.py:19` creates FigureManager with `external_ax`
3. **Parameter passing**: All `**kwargs` flow directly through to plotter

## Missing Parameter Routes

### Stranded Plotter Parameters

**HeatmapPlotter format parameter**:
- **Location**: `heatmap.py:165` - `format_str = styles.get("format", ".2f")`
- **Current status**: Exists in `_style_cell_text()` but only accessible via theme
- **Routing needed**: Should be passable as `fm.plot("heatmap", ..., format="int")`

**HeatmapPlotter xlabel_pos parameter**:
- **Location**: `heatmap.py:143` - `xlabel_pos = self.style_applicator.get_style_with_fallback("xlabel_pos")`
- **Current status**: Theme-only parameter, not in component schema for direct access
- **Routing needed**: Should be accessible as plot parameter

### Missing Axes Configuration

**Hardcoded axes settings**:
- **Tick formatting**: Examples show manual `ax.ticklabel_format()` calls - should be theme/parameter controlled
- **Axis limits**: Only manual setting in examples - could have theme defaults
- **Scale types**: Manual `ax.set_xscale('log')` - could be plotter parameters

**Theme gaps**:
- No theme support for axis limits, scales, tick formatting
- Missing integration between theme system and axes positioning

**API gaps**:
- No built-in support for common axes customization (limits, scales, tick formatting)
- Users forced to manually access axes for basic configuration

## Integration Assessment  

### Current Architecture Strengths
- **✅ Excellent kwargs flow**: User parameters reach plotters cleanly
- **✅ Theme integration**: Well-designed precedence and fallback system
- **✅ Component schemas**: Clear organization of what parameters belong where
- **✅ Style applicator**: Sophisticated parameter resolution with theme inheritance

### Architecture Weaknesses
- **❌ Stranded parameters**: Heatmap `format` and `xlabel_pos` parameters exist but not user-accessible
- **❌ Manual axes access**: Users manually call `fm.get_axes()` then `ax.set_*()` for basic needs
- **❌ Inconsistent axes integration**: Some axes functions theme-controlled, others manual only
- **❌ Missing axes parameter routing**: No systematic way to pass axes configuration through API

## Recommendations for FigureManager Architecture

### Required Parameter Routes

**axes_kwargs evidence: ❌ NOT needed**
- **Rationale**: Current examples show users prefer direct axes access for customization
- **Evidence**: Examples consistently use `ax = fm.get_axes(row, col)` then `ax.set_*()` 
- **Alternative**: Better theme integration for common axes parameters

**plotter_kwargs evidence: ❌ NOT needed**
- **Rationale**: Current kwargs flow to plotters works excellently
- **Evidence**: All common plotter parameters (color, linewidth, etc.) work through existing system
- **Current system**: FigureConfig `plotter_kwargs` would be redundant with existing flow

**Missing theme parameter access: ✅ NEEDED**
- **Problem**: Heatmap `format` and `xlabel_pos` parameters exist but no API route
- **Solution**: Extend component schemas to include these parameters for direct access

### Integration with Existing Systems

**Theme system compatibility**:
- **Strength**: Current precedence system (explicit > theme) works well
- **Gap**: Some theme parameters not exposed to user API (heatmap format, xlabel_pos)
- **Recommendation**: Audit component schemas to ensure all theme parameters are accessible

**Backward compatibility**: 
- **Impact**: Adding stranded parameters to APIs is purely additive
- **Risk**: Very low - won't break existing code
- **Benefit**: Eliminates need for users to access private theme system

**API consistency**:
- **Current**: Some parameters accessible via kwargs, others theme-only
- **Goal**: All plotter-specific parameters should be accessible via both routes
- **Implementation**: Extend component schemas for missing parameters

## Conclusion

**FigureConfig axes_kwargs and plotter_kwargs are NOT needed**. The current parameter flow architecture is sophisticated and handles the vast majority of use cases well. 

**Key improvements needed**:
1. **Fix stranded parameters**: Make heatmap `format` and `xlabel_pos` accessible via kwargs
2. **Extend component schemas**: Ensure all theme parameters have API routes  
3. **Improve axes theme integration**: Add theme support for axis limits, scales, tick formatting

**Current FigureConfig is optimal**: The existing `figure_kwargs`, `subplot_kwargs` structure handles matplotlib integration correctly. Additional kwargs dictionaries would create redundant/confusing routes.
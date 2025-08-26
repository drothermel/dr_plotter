# Axes & Plotter Parameter Routing Audit: Current Implementation Analysis

## Your Mission
You are conducting a comprehensive audit of how dr_plotter currently handles axes-level and plotter-level parameter routing. We need to understand the existing parameter passing mechanisms before finalizing our FigureManager parameter routing architecture.

## Context
We've designed FigureManager parameter routing for figure-level functions (`plt.figure()`, `plt.subplots()`, `plt.tight_layout()`), but need to understand how dr_plotter currently handles:
- **Axes-level functions**: `ax.set_xlabel()`, `ax.set_ylabel()`, `ax.set_xlim()`, `ax.grid()`, `ax.tick_params()`, etc.
- **Plotter-specific parameters**: Format strings, positioning, styling that doesn't come from themes

## Your Systematic Investigation

### 1. Axes-Level Parameter Discovery
**Find how dr_plotter currently configures individual axes:**

**Search for axes configuration patterns:**
- `ax.set_xlabel()`, `ax.set_ylabel()` - axis labels
- `ax.set_xlim()`, `ax.set_ylim()` - axis limits
- `ax.set_xscale()`, `ax.set_yscale()` - axis scaling (log, linear)
- `ax.grid()` - grid configuration
- `ax.tick_params()` - tick formatting and styling
- `ax.ticklabel_format()` - tick label formatting (scientific notation, etc.)
- `ax.legend()` - individual axes legends
- Any other `ax.set_*()` or `ax.*()` calls

**For each pattern found, document:**
- Where in the codebase it's called
- How parameters reach these function calls
- Whether parameters come from themes, individual plotters, or direct user input

### 2. Plotter-Level Parameter Discovery
**Find how individual plotters handle their specific parameters:**

**Examine plotter classes for parameter handling:**
- `HeatmapPlotter` - format strings (`format='int'`), positioning (`xlabel_pos='bottom'`)
- `LinePlotter` - line styling, markers, error bars
- `BarPlotter` - bar styling, positioning, stacking vs grouping
- `ScatterPlotter` - marker styling, sizing
- Other plotters - any specific parameter patterns

**For each plotter, document:**
- What plotter-specific parameters it accepts
- How these parameters are passed from user input to plotter
- Whether parameters come through plot() method, theme system, or other routes

### 3. Current Parameter Flow Analysis
**Trace parameter flow from user input to final application:**

**User Input Routes:**
- `fm.plot("line", row, col, data, **kwargs)` - how kwargs reach LinePlotter
- `drp.line(data, **kwargs)` - how API kwargs reach plotters
- Theme system parameter application
- FigureManager parameter passing to plotters

**Parameter Processing Pipeline:**
- Where parameter validation happens
- How parameters are routed to appropriate destinations (axes vs plotter)
- How conflicts between theme and explicit parameters are resolved

### 4. Theme System Integration with Axes/Plotters
**Analyze how theme system handles axes and plotter parameters:**

**Theme-to-axes integration:**
- How AxesStyles parameters reach `ax.set_*()` functions
- Which axes parameters can be controlled by themes
- How theme inheritance affects axes configuration

**Theme-to-plotter integration:**
- How PlotStyles parameters reach individual plotters
- Which plotter parameters can be controlled by themes
- How themes handle plotter-specific styling

### 5. Missing Parameter Routes Discovery
**Identify parameters that currently have no clear routing:**

**From heatmap issues we know:**
- `format='int'` parameter exists in HeatmapPlotter but can't be passed through API
- `xlabel_pos='bottom'` parameter exists but not accessible from user code

**Search for other "stranded" parameters:**
- Parameters that exist in plotter code but have no API route
- Axes configuration that's hardcoded but should be user-configurable
- Theme parameters that don't have corresponding user configuration options

## Required Output Structure

Create `/docs/axes-plotter-parameter-routing-audit.md` with these sections:

### Current Axes Configuration Patterns
```markdown
## Current Axes Configuration Patterns

### ax.set_xlabel()/set_ylabel() Usage
- **Locations**: [file:line references where axis labels are set]
- **Parameter source**: [how label text and styling reach these calls]
- **User control**: [how users currently control axis labels]

### ax.set_xlim()/set_ylim() Usage
- **Locations**: [file:line references where axis limits are set]
- **Parameter source**: [how limit values reach these calls]
- **User control**: [how users currently control axis limits]

### [Other axes functions]
[Same analysis for each axes configuration function found]
```

### Plotter-Specific Parameter Handling
```markdown
## Plotter-Specific Parameter Handling

### HeatmapPlotter Parameters
- **Parameters discovered**: [list all parameters with types and defaults]
- **User access**: [which parameters are accessible from user code]
- **Blocked parameters**: [parameters that exist but can't be passed through API]

### LinePlotter Parameters
- **Parameters discovered**: [list all parameters]
- **Current routing**: [how parameters reach LinePlotter]
- **User control**: [API for controlling line plotter parameters]

### [Other plotters]
[Same analysis for each plotter class]
```

### Parameter Flow Architecture
```markdown
## Parameter Flow Architecture

### From FigureManager.plot() to Plotters
1. **User calls**: `fm.plot("line", row, col, data, **kwargs)`
2. **Parameter routing**: [how kwargs are processed and routed]
3. **Plotter integration**: [how parameters reach specific plotter classes]

### From Theme System to Axes/Plotters
1. **Theme parameter storage**: [how theme stores axes/plotter parameters]
2. **Application mechanism**: [how theme parameters are applied to axes/plotters]
3. **Conflict resolution**: [how explicit parameters override theme defaults]
```

### Missing Parameter Routes
```markdown
## Missing Parameter Routes

### Stranded Plotter Parameters
- **[Parameter name]**: 
  - **Location**: [where parameter exists in code]
  - **Current status**: [why it's not user-accessible]
  - **Routing needed**: [how it should be made accessible]

### Missing Axes Configuration
- **Hardcoded axes settings**: [axes configuration that should be user-controllable]
- **Theme gaps**: [axes styling not covered by theme system]
- **API gaps**: [axes configuration missing from user API]
```

### Integration Assessment
```markdown
## Integration Assessment

### Current Architecture Strengths
- **What works well**: [existing parameter routing that works effectively]
- **Clean integrations**: [well-designed parameter passing patterns]

### Architecture Weaknesses  
- **Parameter routing failures**: [where parameters can't reach their destinations]
- **Integration gaps**: [missing connections between systems]
- **User experience issues**: [parameter access problems for users]
```

### Recommendations for FigureManager Architecture
```markdown
## Recommendations for FigureManager Architecture

### Required Parameter Routes
- **axes_kwargs needed**: [evidence for/against axes_kwargs in FigureManager]
- **plotter_kwargs needed**: [evidence for/against plotter_kwargs in FigureManager]
- **Other routing needed**: [additional parameter routing requirements]

### Integration with Existing Systems
- **Theme system compatibility**: [how new routing should integrate with themes]
- **Backward compatibility**: [impact on existing parameter passing patterns]
- **API consistency**: [ensuring consistent parameter access across all APIs]
```

## Success Criteria
- ✅ Complete inventory of current axes-level parameter handling
- ✅ Complete inventory of current plotter-level parameter handling  
- ✅ Clear documentation of existing parameter flow architecture
- ✅ Identification of missing/blocked parameter routes
- ✅ Evidence-based recommendations for FigureManager parameter routing design

## Critical Importance
This audit will determine whether our proposed `axes_kwargs` and `plotter_kwargs` are actually needed, or if dr_plotter has other mechanisms for parameter routing that we should build on instead. Missing this analysis could lead to duplicate or conflicting parameter routing systems.
# Phase 2 Step 1 Agent Prompt: Legacy Bridge Code Audit

## Your Mission
You are conducting a comprehensive audit of ALL legacy parameter handling code in dr_plotter's FigureManager and related components. Your task is to identify every piece of code that converts individual parameters to config objects, maintains backwards compatibility, or handles legacy parameter patterns.

## Context
This is Step 1 of Phase 2 in our FigureManager parameter organization project. We discovered that dr_plotter has rich config infrastructure (6 config classes) but FigureManager still accepts individual parameters and converts them internally via legacy bridge methods. We're planning to remove ALL backwards compatibility and create a clean config-first API.

**Critical**: We need to find EVERYTHING that needs removal - missing any legacy code will break the clean slate implementation.

## Your Systematic Investigation

### 1. FigureManager Legacy Parameter Handling
**Find all individual parameter handling in FigureManager:**
- Document every individual parameter in `__init__()` method signature
- Identify parameter validation, processing, and conversion logic
- Look for parameter grouping or transformation code
- Find any parameter defaults or fallback handling

### 2. Legacy Bridge Methods Discovery
**Find all methods that convert individual parameters to config objects:**
- Search for methods named `_convert_legacy_*`
- Search for methods named `_build_*_config`
- Look for any other parameter conversion/transformation methods
- Document what parameters each method handles and what config object it creates

### 3. Config Object Creation Patterns
**Identify how config objects are currently created internally:**
- Find where `LegendConfig`, `SubplotLayoutConfig`, etc. are instantiated
- Document parameter → config object mapping logic
- Identify any complex parameter processing before config creation
- Look for parameter validation that happens during conversion

### 4. Factory Function Investigation  
**Analyze the existing `create_figure_manager()` function:**
- Document its current parameter interface
- Identify how it differs from direct FigureManager construction
- Find any config-first patterns already implemented
- Look for parameter handling differences between factory and constructor

### 5. Parameter Routing and Integration Points
**Find where individual parameters are processed and routed:**
- Look for parameter passing to matplotlib functions
- Find theme integration points with individual parameters
- Identify any parameter preprocessing or transformation
- Document parameter flow from user input to final application

### 6. Backwards Compatibility Code
**Search for any other backwards compatibility patterns:**
- Deprecated parameter warnings
- Alternative parameter names or aliases
- Legacy parameter format support
- Version compatibility code

## Required Output Structure

Create `/docs/legacy-bridge-audit.md` with these sections:

### FigureManager Individual Parameters
```markdown
## FigureManager Individual Parameters

### Constructor Signature Analysis
- **Current Parameters**: [complete list with types and defaults]
- **Parameter Categories**: [group by function - legend, layout, theme, etc.]
- **Complex Parameters**: [parameters requiring special processing]

### Parameter Processing Logic
- **Validation**: [where/how parameters are validated]
- **Transformation**: [any parameter modification before use]
- **Defaults**: [default value handling patterns]
```

### Legacy Bridge Methods Found
```markdown
## Legacy Bridge Methods Found

### _convert_legacy_legend_params()
- **Location**: file:line
- **Input Parameters**: [list parameters it processes]
- **Output**: [config object type created]
- **Logic**: [brief description of conversion logic]
- **Dependencies**: [other methods or data it relies on]

### [Other Bridge Methods]
[Same format for each discovered method]
```

### Config Object Creation Analysis
```markdown
## Config Object Creation Analysis

### Internal Config Creation Patterns
- **LegendConfig Creation**: [where and how it's created internally]
- **SubplotLayoutConfig Creation**: [where and how it's created]
- **[Other Configs]**: [creation patterns for each config type]

### Parameter → Config Mapping
- **Legend Parameters**: [which individual params map to LegendConfig]
- **Layout Parameters**: [which individual params map to SubplotLayoutConfig]
- **[Other Categories]**: [parameter groupings and their config homes]
```

### Parameter Flow Analysis
```markdown
## Parameter Flow Analysis

### User Input → Internal Processing → Final Application
1. **User provides individual parameters** → FigureManager constructor
2. **Parameter conversion** → Legacy bridge methods
3. **Config object creation** → Internal config instantiation
4. **Config application** → Theme system, matplotlib calls, etc.

### Integration Points
- **Theme Integration**: [how individual parameters interact with theme system]
- **Matplotlib Integration**: [how parameters reach matplotlib functions]
- **Plotter Integration**: [how parameters reach specific plotters]
```

### Removal Impact Assessment
```markdown
## Removal Impact Assessment

### Code Volume
- **Lines to Remove**: [estimated lines of legacy code]
- **Methods to Delete**: [count of bridge methods]
- **Parameters to Eliminate**: [count of individual parameters]

### Breaking Changes
- **Constructor Changes**: [how constructor signature will change]
- **Method Removals**: [public methods that will be removed]
- **Behavior Changes**: [any behavior that will change]

### Dependencies
- **Internal Dependencies**: [other code that calls legacy methods]
- **External Dependencies**: [examples/user code that uses individual parameters]
```

## Code Requirements

**Follow Project Standards**:
1. **No comments or docstrings** in any code you create
2. **All imports at the very top** of files
3. **Use assertions for validation**: `assert condition, "message"`

## Search Strategy

**Use comprehensive search patterns:**
```bash
# Example searches (you choose appropriate tools):
rg -t py "_convert_legacy" src/
rg -t py "_build.*config" src/
rg -t py "def __init__" src/dr_plotter/figure.py
rg -t py "create_figure_manager" src/
```

## Success Criteria
- ✅ Complete inventory of ALL legacy parameter handling code
- ✅ Clear documentation of what needs removal vs what needs modification
- ✅ Impact assessment for removal planning
- ✅ Evidence-based foundation for Step 2 (Legacy Bridge Removal)

## Critical Importance
Missing ANY legacy code in this audit will cause failures in Step 2 removal. Be comprehensive and systematic - we need to find EVERYTHING that handles individual parameters before we can safely remove it all.

Your audit will directly determine the scope and complexity of the legacy bridge removal step.
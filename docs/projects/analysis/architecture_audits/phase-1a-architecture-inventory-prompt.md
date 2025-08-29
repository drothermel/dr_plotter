# Phase 1a Agent Prompt: Existing Architecture Inventory

## Your Mission
You are conducting the first phase of a systematic FigureManager parameter organization project. Your task is to create a comprehensive inventory of ALL existing configuration classes, dataclasses, and parameter grouping objects in the dr_plotter library to understand what architectural building blocks already exist.

## Context
This is Phase 1a of a 4-phase infrastructure cleanup project. We discovered during faceted plotting implementation that FigureManager has grown organically with unorganized parameters (15+ separate parameters like `plot_margin_bottom`, `legend_y_offset`, `legend_strategy`, etc.). Before designing new parameter organization, we need to understand what configuration infrastructure already exists.

## Your Systematic Investigation

### 1. Configuration Classes Discovery
**Search for existing configuration/config classes:**
- Look for classes named `*Config`, `*Configuration`, `*Settings`
- Examples to find: `LegendConfig`, `LayoutConfig`, `PlotConfig`, `AxesConfig`
- Document class locations, parameters, and purposes

### 2. Dataclass Inventory  
**Find all dataclasses used for parameter grouping:**
- Search for `@dataclass` decorators throughout the codebase
- Focus on parameter/configuration-related dataclasses
- Document fields, default values, and usage patterns

### 3. Style System Architecture
**Analyze the theme/style system structure:**
- `PlotStyles`, `AxesStyles`, `FigureStyles` classes already discovered
- Find any other style-related configuration objects
- Document how these relate to parameter organization

### 4. Parameter Container Objects
**Look for any other parameter grouping patterns:**
- Classes that group related parameters together
- Configuration objects passed to plotting functions
- Any existing parameter validation or processing objects

### 5. FigureManager Integration Points
**Analyze how existing config classes integrate with FigureManager:**
- Which config objects does FigureManager already accept?
- How are config objects currently processed/applied?
- Are there unused config integration points?

## Required Output Structure

Create `/docs/architecture-inventory.md` with these sections:

### Configuration Classes Found
```markdown
## Configuration Classes Found

### LegendConfig (if found)
- **Location**: src/dr_plotter/path/to/file.py:line
- **Parameters**: [list all parameters with types]
- **Purpose**: [what it configures]
- **Current Usage**: [how it's used in FigureManager or elsewhere]

### [Other Config Classes]
[Same format for each discovered class]
```

### Dataclasses Discovered
```markdown  
## Dataclasses Discovered

### [Dataclass Name]
- **Location**: file:line
- **Fields**: [field names and types]  
- **Usage**: [where/how it's used]
- **Parameter Grouping**: [what logical group of parameters it represents]
```

### Style System Components
```markdown
## Style System Components
- **Theme Class**: Location and responsibilities
- **Style Classes**: PlotStyles, AxesStyles, etc. with parameter inventories
- **Integration**: How styles integrate with parameter handling
```

### FigureManager Integration Analysis
```markdown
## FigureManager Integration Analysis
- **Current Config Parameters**: Which config objects FigureManager accepts
- **Parameter Processing**: How config objects are currently handled
- **Missing Integrations**: Config classes that exist but aren't used by FigureManager
```

### Architectural Patterns Identified
```markdown
## Architectural Patterns Identified
- **Parameter Grouping Strategy**: What patterns already exist for organizing parameters
- **Integration Approach**: How config objects connect to plotting system
- **Design Principles**: What organizational principles are already established
```

### Gap Analysis
```markdown
## Gap Analysis
- **Ungrouped Parameters**: FigureManager parameters that don't have config class homes
- **Missing Config Classes**: Logical parameter groups that need config classes
- **Integration Opportunities**: Where existing config classes could be better utilized
```

## Code Requirements

**Follow Project Standards**:
1. **No comments or docstrings** in any code you create
2. **Comprehensive type hints** on any functions you write
3. **All imports at the very top** of files
4. **Use assertions for validation**: `assert condition, "message"`

## Search Strategy

**Use systematic search patterns:**
```bash
# Example search approaches (you choose appropriate search tools):
# Find config classes
rg -t py "class.*Config" src/
# Find dataclasses  
rg -t py "@dataclass" src/
# Find style classes
rg -t py "class.*Style" src/
```

## Success Criteria
- ✅ Complete inventory of ALL existing configuration infrastructure
- ✅ Clear documentation of what parameter organization already exists
- ✅ Analysis of FigureManager's current config integration capabilities
- ✅ Gap analysis showing which parameters need new organization vs can use existing classes
- ✅ Evidence-based foundation for Phase 1b parameter mapping

## Strategic Importance
This inventory prevents reinventing existing solutions and reveals the library's intended design patterns. Your findings will directly inform whether we build on existing config classes or need to create new parameter organization approaches.

The output should be comprehensive enough that Phase 1b can immediately map FigureManager parameters to existing config classes vs identify parameters needing new homes.
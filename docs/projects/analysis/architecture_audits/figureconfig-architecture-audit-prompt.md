# FigureConfig Architecture Audit: Parameter Classification & Side Effects Analysis

## Your Mission
You are conducting a comprehensive audit of our proposed FigureConfig architecture to validate parameter classification decisions and identify potential side effects. We need to ensure our architectural principle is sound and complete before implementation.

## Context & Architectural Principle

### **Our Parameter Classification Rule**:
- **Explicit parameters**: Only for parameters that DON'T map directly to a single matplotlib function call
- **Kwargs dictionaries**: Only for direct matplotlib function parameters

### **Current Proposed FigureConfig**:
```python
@dataclass
class FigureConfig:
    # Explicit parameters (NOT direct function params - separate function calls)
    tight_layout_pad: float = 0.5                     # → plt.tight_layout(pad=tight_layout_pad)
    
    # Integration parameters  
    external_ax: Optional[plt.Axes] = None
    shared_styling: Optional[bool] = None
    
    # Direct function parameters (kwargs only)  
    figure_kwargs: Dict[str, Any] = field(default_factory=dict)    # → plt.figure(**figure_kwargs)
    subplot_kwargs: Dict[str, Any] = field(default_factory=dict)   # → plt.subplots(**subplot_kwargs)
```

### **Usage Pattern**:
```python
FigureConfig(
    tight_layout_pad=0.3,  # Explicit - goes to separate plt.tight_layout() call
    subplot_kwargs={
        'nrows': 2,         # Direct plt.subplots() parameter
        'ncols': 4,         # Direct plt.subplots() parameter  
        'figsize': (16, 9), # Direct plt.subplots() parameter
        'sharey': 'row'     # Direct plt.subplots() parameter
    }
)

# When FigureManager needs grid info:
nrows = config.subplot_kwargs.get('nrows', 1)
ncols = config.subplot_kwargs.get('ncols', 1)
```

## Your Systematic Investigation

### 1. Matplotlib Function Call Analysis
**Analyze how dr_plotter currently creates figures and identify ALL matplotlib function calls:**
- `plt.figure()` calls and their parameters
- `plt.subplots()` calls and their parameters  
- `plt.tight_layout()` calls and their parameters
- `plt.subplots_adjust()` calls and their parameters
- Any other figure/layout matplotlib functions called

**Document each function's parameter requirements and current dr_plotter usage patterns.**

### 2. Missing Explicit Parameters Discovery
**Find parameters that should be explicit but aren't in our current proposal:**

**Search for these patterns:**
- Parameters used in separate matplotlib function calls (like `tight_layout_pad`)
- Parameters that require special processing before being passed to matplotlib
- Parameters that control multiple matplotlib function calls
- Dr_plotter-specific parameters that don't map directly to matplotlib

**Potential candidates to investigate:**
- `subplots_adjust` parameters (hspace, wspace, left, right, top, bottom)
- `constrained_layout` parameters  
- `gridspec` parameters that might be processed separately
- Any figure positioning/layout parameters that aren't direct matplotlib function params

### 3. Parameter Extraction Side Effects Analysis
**Analyze potential issues with our kwargs extraction approach:**

**FigureManager Implementation Impact:**
- How often does FigureManager need to extract `nrows`, `ncols` from `subplot_kwargs`?
- Are there places where grid dimensions are needed for validation or processing?
- Does extracting from kwargs create performance or complexity issues?

**Default Value Handling:**
- How are defaults handled when parameters are in kwargs vs explicit?
- Are there validation requirements for grid dimensions or other parameters?
- Do any parameters have complex default logic that breaks with kwargs approach?

### 4. Integration Points Analysis
**Examine how our architecture affects dr_plotter integration points:**

**Theme System Integration:**
- Do themes need access to figure dimensions or layout parameters?
- Are there theme defaults that depend on explicit parameter access?

**Legend System Integration:**
- Does legend positioning require knowledge of figure dimensions?
- Are there legend calculations that need grid information?

**Plotter Integration:**
- Do individual plotters need access to figure layout information?
- Are there plotter-specific requirements for figure parameters?

### 5. Backwards Compatibility & Migration Analysis
**Assess impact on config object creation and usage patterns:**

**Config Object Construction:**
- Is it intuitive for users to put `nrows`/`ncols` in `subplot_kwargs`?
- Are there usability issues with the kwargs approach?

**Validation Impact:**
- How does parameter validation work with kwargs vs explicit parameters?
- Are there type checking or IDE autocomplete implications?

## Required Output Structure

Create `/docs/figureconfig-architecture-audit.md` with these sections:

### Matplotlib Function Call Inventory
```markdown
## Matplotlib Function Call Inventory

### plt.figure() Usage in dr_plotter
- **Current parameters used**: [list with file:line references]
- **Our figure_kwargs coverage**: [analysis of whether our approach handles all cases]

### plt.subplots() Usage in dr_plotter  
- **Current parameters used**: [list with file:line references]
- **Our subplot_kwargs coverage**: [analysis of whether our approach handles all cases]

### Other Layout Functions Used
- **plt.tight_layout()**: [parameters used, file locations]
- **plt.subplots_adjust()**: [parameters used, file locations]
- **[Other functions]**: [analysis of each function found]
```

### Missing Explicit Parameters Analysis
```markdown
## Missing Explicit Parameters Analysis

### Parameters That Should Be Explicit
- **[Parameter name]**: 
  - **Why explicit**: [reason it doesn't map to single matplotlib function]
  - **Current usage**: [how dr_plotter currently handles it]
  - **Proposed explicit parameter**: [suggested name and type]

### Parameters Correctly Classified
- **Confirmed kwargs parameters**: [list of parameters that belong in kwargs]
- **Confirmed explicit parameters**: [list of parameters that should be explicit]
```

### Side Effects Assessment
```markdown
## Side Effects Assessment

### Parameter Extraction Complexity
- **Grid dimension extraction**: [analysis of nrows/ncols extraction impact]
- **Performance implications**: [any performance concerns with kwargs approach]
- **Code complexity**: [impact on FigureManager implementation complexity]

### Integration Impact
- **Theme system**: [how our architecture affects theme integration]
- **Legend system**: [how our architecture affects legend positioning/sizing]
- **Plotter system**: [how our architecture affects individual plotters]

### Validation & Usability
- **User experience**: [assessment of kwargs vs explicit parameter usability]
- **Type checking**: [impact on IDE support and type validation]
- **Default handling**: [complexity of default value management]
```

### Recommendations
```markdown
## Recommendations

### Architecture Validation
- **✅ Approve current architecture** OR **❌ Significant issues identified**
- **Missing explicit parameters to add**: [specific recommendations]
- **Implementation concerns to address**: [specific issues requiring attention]

### Alternative Approaches (if current has issues)
- **Alternative architecture suggestions**: [if significant problems identified]
- **Hybrid approaches**: [if pure kwargs approach has issues]
```

## Success Criteria
- ✅ Complete inventory of all matplotlib function calls in dr_plotter
- ✅ Identification of any missing explicit parameters following our classification rule
- ✅ Assessment of side effects from kwargs extraction approach
- ✅ Clear recommendation on architecture validation or needed modifications

## Critical Importance
This audit will validate or invalidate our foundational architectural decision. Missing any matplotlib integration patterns or side effects could cause implementation failures or poor user experience. Be comprehensive and systematic in your analysis.
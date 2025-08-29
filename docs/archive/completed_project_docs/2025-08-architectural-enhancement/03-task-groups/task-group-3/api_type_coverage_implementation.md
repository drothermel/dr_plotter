# API Type Coverage Implementation
## Task Group 3: Complete Type Coverage for Public API Functions

### Mission Statement
Implement comprehensive type annotations for all 8 public API functions in `src/dr_plotter/api.py` plus the `_fm_plot` helper function. This provides complete static analysis support and excellent IDE experience for the entire DR_PLOTTER public API while maintaining full backward compatibility and kwargs flexibility.

### Current Status Context
- **Phase 1 Complete**: Foundation work (fail-fast principles, constructor standardization)
- **Task Group 1 Complete**: Explicit capability architecture (`supports_legend`, `supports_grouped`)  
- **Decision 3 Complete**: 100% StyleApplicator bypass elimination with `_get_style()` method removal
- **Next Challenge**: Public API type coverage enabling comprehensive static analysis

### Implementation Objectives

#### Primary Objective
Add complete type annotations to all public API functions using the agreed design pattern:
- **Parameter types**: Explicit typing for `data`, `x`, `y`, `ax` parameters
- **kwargs typing**: `Dict[str, Any]` for matplotlib passthrough flexibility
- **Return types**: Inline `Tuple[plt.Figure, plt.Axes]` for clarity
- **Import strategy**: Minimal imports, only what's needed

#### Secondary Objectives
1. Maintain 100% backward compatibility - zero breaking changes
2. Follow established code patterns and DR methodology principles
3. Ensure consistent typing patterns across all 8 functions
4. Validate type coverage through import and basic functionality testing

### Design Specifications

#### **Agreed Type Pattern**
```python
from typing import Any, Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
import pandas as pd

def function_name(
    data: pd.DataFrame, 
    x: ColName, 
    y: ColName, 
    ax: Optional[plt.Axes] = None, 
    **kwargs: Dict[str, Any]
) -> Tuple[plt.Figure, plt.Axes]:
```

#### **Import Requirements**
```python
from typing import Any, Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
import pandas as pd
from dr_plotter.types import ColName
```

**Rationale**: Minimal imports with only necessary typing constructs, preserving existing import structure.

#### **Parameter Type Standards**
- **`data`**: `pd.DataFrame` (explicit pandas DataFrame)
- **Column parameters**: `ColName` (existing type alias)
- **`ax` parameter**: `Optional[plt.Axes]` (matplotlib Axes or None)
- **`**kwargs`**: `Dict[str, Any]` (maintains flexibility for matplotlib passthrough)

#### **Return Type Standard**
- **All functions**: `Tuple[plt.Figure, plt.Axes]` (inline, no type alias)
- **Rationale**: Explicit and clear, consistent with `_fm_plot` return pattern

### Functions to Type (9 total)

#### **Standard x,y Pattern Functions (6)**
```python
def scatter(
    data: pd.DataFrame, 
    x: ColName, 
    y: ColName, 
    ax: Optional[plt.Axes] = None, 
    **kwargs: Dict[str, Any]
) -> Tuple[plt.Figure, plt.Axes]:

def line(
    data: pd.DataFrame, 
    x: ColName, 
    y: ColName, 
    ax: Optional[plt.Axes] = None, 
    **kwargs: Dict[str, Any]
) -> Tuple[plt.Figure, plt.Axes]:

def bar(
    data: pd.DataFrame, 
    x: ColName, 
    y: ColName, 
    ax: Optional[plt.Axes] = None, 
    **kwargs: Dict[str, Any]
) -> Tuple[plt.Figure, plt.Axes]:

def violin(
    data: pd.DataFrame, 
    x: ColName, 
    y: ColName, 
    ax: Optional[plt.Axes] = None, 
    **kwargs: Dict[str, Any]
) -> Tuple[plt.Figure, plt.Axes]:

def gmm_level_set(
    data: pd.DataFrame, 
    x: ColName, 
    y: ColName, 
    ax: Optional[plt.Axes] = None, 
    **kwargs: Dict[str, Any]
) -> Tuple[plt.Figure, plt.Axes]:
```

#### **Single x Pattern Function (1)**
```python
def hist(
    data: pd.DataFrame, 
    x: ColName, 
    ax: Optional[plt.Axes] = None, 
    **kwargs: Dict[str, Any]
) -> Tuple[plt.Figure, plt.Axes]:
```

#### **x,y,values Pattern Function (1)**
```python
def heatmap(
    data: pd.DataFrame, 
    x: ColName, 
    y: ColName, 
    values: ColName, 
    ax: Optional[plt.Axes] = None, 
    **kwargs: Dict[str, Any]
) -> Tuple[plt.Figure, plt.Axes]:
```

#### **Special Pattern Function (1)**
```python
def bump_plot(
    data: pd.DataFrame,
    time_col: ColName,
    category_col: ColName,
    value_col: ColName,
    ax: Optional[plt.Axes] = None,
    **kwargs: Dict[str, Any]
) -> Tuple[plt.Figure, plt.Axes]:
```

#### **Helper Function (1)**
```python
def _fm_plot(
    plot_type: str,
    data: pd.DataFrame,
    x: Optional[ColName] = None,
    y: Optional[ColName | List[ColName]] = None,
    ax: Optional[plt.Axes] = None,
    **kwargs: Dict[str, Any],
) -> Tuple[plt.Figure, plt.Axes]:
```

### Implementation Requirements

#### **Code Quality Standards**
- **No comments policy**: Code must be self-documenting through clear type annotations
- **Comprehensive typing**: Every parameter and return value must have type hints
- **Import organization**: All imports at the very top, organized by standard/third-party/local
- **Consistency**: Identical patterns across all similar function signatures

#### **Backward Compatibility Requirements**
- **Zero breaking changes**: All existing usage patterns must continue working identically
- **Parameter order preserved**: No changes to parameter order or defaults
- **Function behavior identical**: No changes to function logic or behavior
- **kwargs flexibility maintained**: Full matplotlib parameter passthrough preserved

#### **Type Safety Requirements**
- **Meaningful IDE support**: Parameter types should provide useful autocompletion
- **Static analysis support**: Type annotations should work with mypy and similar tools
- **Clear error messages**: Type mismatches should provide helpful feedback
- **Optional parameter handling**: Proper Optional typing for nullable parameters

### Validation Requirements

#### **Import Validation**
```python
# Must import without errors
from dr_plotter.api import scatter, line, bar, hist, violin, heatmap, bump_plot, gmm_level_set
```

#### **Basic Functionality Validation**
```python
# All functions must work with simple data
import pandas as pd
test_data = pd.DataFrame({'x': [1,2,3], 'y': [1,2,3], 'values': [1,2,3]})

# Standard patterns should work
scatter(test_data, 'x', 'y')
line(test_data, 'x', 'y')
bar(test_data, 'x', 'y')
hist(test_data, 'x')
violin(test_data, 'x', 'y')
heatmap(test_data, 'x', 'y', 'values')
bump_plot(test_data, 'x', 'y', 'values')
gmm_level_set(test_data, 'x', 'y')
```

#### **Type Checking Validation**
If `mypy` is available, run type checking to ensure annotations are valid:
```bash
# Optional validation if mypy available
mypy src/dr_plotter/api.py
```

### Implementation Steps

#### **Phase 1: Import Enhancement (5 minutes)**
1. **Update imports** in `src/dr_plotter/api.py`
2. **Add necessary typing imports**: `Any, Dict, List, Optional, Tuple`
3. **Verify existing imports** are preserved: `matplotlib.pyplot as plt`, `pandas as pd`, `ColName`

#### **Phase 2: Helper Function Typing (5 minutes)**  
1. **Type `_fm_plot` function** with comprehensive parameter and return annotations
2. **Validate parameter handling** for Optional[ColName | List[ColName]] pattern
3. **Test helper function** maintains existing behavior

#### **Phase 3: Standard Pattern Functions (10 minutes)**
1. **Type 6 standard x,y functions**: scatter, line, bar, violin, gmm_level_set
2. **Apply consistent signature pattern** across all functions
3. **Validate parameter order and defaults** are preserved

#### **Phase 4: Special Pattern Functions (5 minutes)**
1. **Type hist function** (single x parameter pattern)
2. **Type heatmap function** (x,y,values pattern)  
3. **Type bump_plot function** (time_col, category_col, value_col pattern)

#### **Phase 5: Validation and Testing (5 minutes)**
1. **Import validation**: Ensure all functions import successfully
2. **Basic functionality testing**: Verify simple usage patterns work
3. **Type consistency check**: Ensure all signatures follow agreed patterns

**Total estimated time**: 30 minutes

### Success Criteria

#### **Implementation Success**
- **Complete type coverage**: All 9 functions have comprehensive type annotations
- **Consistent patterns**: All similar functions use identical type patterns
- **Import compatibility**: Clean imports with proper typing support
- **Zero regressions**: All existing functionality preserved exactly

#### **Type Quality Success**
- **IDE support**: Parameter autocompletion and type hints work properly
- **Static analysis ready**: Annotations work with type checkers
- **Clear return types**: Return values have explicit, inline type annotations
- **Flexible kwargs**: kwargs typing maintains full matplotlib compatibility

#### **Architectural Success**
- **Pattern consistency**: All functions follow established DR methodology principles
- **No breaking changes**: Complete backward compatibility maintained
- **Clean implementation**: No comments, self-documenting through type annotations
- **Future-ready**: Type system foundation supports future API enhancements

### Quality Gates

#### **Before Implementation**
- [ ] Understand current function signatures and behavior
- [ ] Confirm agreed type patterns and import strategy
- [ ] Verify access to test data for validation

#### **During Implementation**
- [ ] Each function typed consistently with agreed patterns
- [ ] Import organization follows standards (top of file, organized sections)
- [ ] No changes to function behavior or parameter handling

#### **After Implementation**
- [ ] All functions import successfully without errors
- [ ] Basic functionality validation passes for all 8 API functions
- [ ] Type annotations provide meaningful IDE support
- [ ] No breaking changes to existing usage patterns

### Risk Mitigation

#### **Type Annotation Risks**
- **Complex type patterns**: Use agreed simple patterns, avoid over-engineering
- **Import conflicts**: Follow minimal import strategy, test import compatibility
- **Breaking changes**: Preserve all existing parameter patterns exactly

#### **Implementation Risks**
- **Inconsistent patterns**: Apply systematic approach, validate consistency across functions
- **Functionality regression**: Test basic usage after each function typing
- **Type checker conflicts**: Use standard typing patterns, avoid complex constructs

### Expected Outcomes

#### **Immediate Benefits**
- **Enhanced IDE experience**: Autocompletion and type hints for all API functions
- **Static analysis support**: Full type checking capability for public API
- **Developer experience**: Clear parameter types and return value expectations
- **Documentation improvement**: Self-documenting code through type annotations

#### **Strategic Benefits**
- **Complete API type coverage**: Foundation for comprehensive static analysis
- **Architectural consistency**: Systematic typing patterns across entire public API
- **Future enhancement ready**: Type system supports API evolution and tooling
- **Quality assurance**: Type safety prevents common parameter misuse errors

---

## Implementation Guidelines

### **Coding Standards**
- **No comments**: Type annotations provide all necessary documentation
- **Consistent formatting**: Follow established patterns throughout file
- **Import organization**: Standard library → Third party → Local imports at top
- **Parameter alignment**: Consistent indentation and spacing for multi-line signatures

### **Testing Approach**
- **Import testing**: Verify all typed functions import successfully
- **Basic functionality**: Test simple usage patterns work identically
- **Type validation**: Confirm IDE support and type hints work properly
- **Regression prevention**: Ensure no changes to existing behavior

### **Success Validation**
The implementation succeeds when all 8 public API functions plus the `_fm_plot` helper have comprehensive type annotations that provide excellent IDE support, enable static analysis, and maintain complete backward compatibility with zero breaking changes.

This task completes the foundational type system work for DR_PLOTTER, establishing systematic typing patterns that support the high-quality architectural foundation achieved through previous systematic enhancements.

**Ready for implementation**: All design decisions resolved, clear requirements established, systematic approach defined.
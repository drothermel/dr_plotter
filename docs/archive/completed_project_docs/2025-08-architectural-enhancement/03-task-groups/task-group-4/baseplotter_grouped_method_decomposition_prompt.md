# BasePlotter Grouped Method Decomposition Implementation
## Task Group 4 - Critical Function Complexity Reduction

### Mission Statement
Decompose the complex `BasePlotter._render_with_grouped_method` function (58 lines, 7+ branches) into focused, single-responsibility methods following the proven StyleApplicator decomposition pattern. This completes the critical complexity reduction phase of Task Group 4.

### Strategic Context
- **Current Problem**: `_render_with_grouped_method` is the second most complex function in the codebase after StyleApplicator (which was successfully decomposed)
- **Pattern Applied**: Method decomposition within existing class (maintaining intuitive lookup for debugging)
- **Success Template**: Follow the StyleApplicator decomposition approach - create focused methods within BasePlotter
- **Architectural Goal**: Reduce complexity while preserving the "grouped rendering" logic discoverability

### Implementation Standards (Critical Requirements)
- **Zero comments policy**: No docstrings, no inline comments, no block comments
- **Comprehensive typing**: All parameters and return values must have complete type hints
- **Method complexity**: Each method <50 lines, <8 branches
- **Self-documenting**: Clear method names that explain functionality
- **Preserve behavior**: Identical functionality, zero breaking changes

### Current Function Analysis

#### **Target Function: `_render_with_grouped_method`**
**File**: `src/dr_plotter/plotters/base.py:254-312`  
**Current Complexity**: 58 lines, 7+ branches  
**Current Responsibilities**:
1. **Group Data Processing** (lines 255-266): Categorical column identification, groupby logic
2. **Group Iteration Setup** (lines 268-278): X-categories extraction, group iteration management  
3. **Style Context Management** (lines 280-285): Group context setting, component style resolution
4. **Special Case Handling** (lines 287-305): Scatter size calculation with continuous style mapping
5. **Position Calculation & Rendering** (lines 307-310): Group positioning and final draw call

### Required Decomposition Strategy

#### **Main Coordinator Function** (Target: ~12 lines)
```python
def _render_with_grouped_method(self, ax: Any) -> None:
    grouped_data = self._process_grouped_data()
    x_categories = self._extract_x_categories()
    
    for group_index, group_info in enumerate(grouped_data):
        group_context = self._setup_group_context(group_info, group_index, len(grouped_data))
        plot_kwargs = self._resolve_group_plot_kwargs(group_context)
        group_position = self._calculate_group_position(group_index, len(grouped_data), x_categories)
        
        self._draw_grouped(ax, group_context['data'], group_position, **plot_kwargs)
```

#### **Required Focused Methods**

##### **Method 1: `_process_grouped_data`** 
```python
def _process_grouped_data(self) -> List[Tuple[Any, pd.DataFrame]]:
    """Process categorical columns and create grouped data iterator"""
```
- **Responsibility**: Handle categorical column identification and groupby logic
- **Target**: ~15 lines
- **Extract**: Lines 255-266 logic

##### **Method 2: `_extract_x_categories`**
```python
def _extract_x_categories(self) -> Optional[Any]:
    """Extract x-axis categories if available"""
```
- **Responsibility**: X-categories extraction for positioning
- **Target**: ~5 lines  
- **Extract**: Lines 268-270 logic

##### **Method 3: `_setup_group_context`**
```python
def _setup_group_context(self, group_info: Tuple[Any, pd.DataFrame], group_index: int, n_groups: int) -> Dict[str, Any]:
    """Setup group context with values and style applicator context"""
```
- **Responsibility**: Group values processing and style context management
- **Target**: ~15 lines
- **Extract**: Lines 272-285 logic

##### **Method 4: `_resolve_group_plot_kwargs`**
```python
def _resolve_group_plot_kwargs(self, group_context: Dict[str, Any]) -> Dict[str, Any]:
    """Resolve plot kwargs including special size handling for scatter plots"""
```
- **Responsibility**: Component style resolution + scatter size special case handling
- **Target**: ~25 lines
- **Extract**: Lines 280-305 logic (style resolution + size calculation)

##### **Method 5: `_calculate_group_position`** (Already exists - verify quality)
```python
def _calculate_group_position(self, group_index: int, n_groups: int, x_categories: Optional[Any] = None) -> Dict[str, Any]:
```
- **Responsibility**: Group positioning calculation
- **Update**: Add x_categories parameter and integration

### Implementation Requirements

#### **Type Definitions Needed**
```python
# Add these type hints at top of file after existing imports
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

type GroupInfo = Tuple[Any, pd.DataFrame]
type GroupContext = Dict[str, Any]
```

#### **Behavioral Preservation Requirements**
- **Identical visual output**: All plots must render identically
- **Performance neutral**: No performance degradation
- **Error handling**: Preserve existing error handling patterns (assertions, not try-catch)
- **Group processing**: Exact same groupby logic and iteration order

#### **Integration Points to Maintain**
- **StyleApplicator integration**: `self.style_applicator.set_group_context(group_values)`
- **StyleEngine integration**: Size calculation for scatter plots via `self.style_engine._get_continuous_style`
- **Plotter subclass integration**: `self._draw_grouped()` method calls must remain identical

### Validation Requirements

#### **Functional Testing**
1. **Run all existing tests**: Ensure zero test failures
2. **Visual validation**: Compare plot outputs before/after decomposition
3. **Grouped plot functionality**: Test all plotter types with `supports_grouped = True`
4. **Size handling**: Validate scatter size calculations with continuous size mapping

#### **Code Quality Verification**
1. **Complexity metrics**: All methods <50 lines, <8 branches
2. **Type coverage**: Complete type hints on all parameters and return values  
3. **Standards compliance**: Zero comments, self-documenting method names
4. **Pattern consistency**: Follows StyleApplicator decomposition template

#### **Performance Validation**
1. **No regression**: Benchmark grouped rendering performance
2. **Memory usage**: Verify no increase in memory consumption
3. **Function call overhead**: Minimal impact from method decomposition

### Success Criteria
- **✅ Original function reduced**: 58 lines → ~12 line coordinator
- **✅ Method complexity**: All methods <50 lines, <8 branches  
- **✅ Standards compliance**: Zero comments, complete typing, self-documenting names
- **✅ Behavioral preservation**: Identical functionality, zero breaking changes
- **✅ Pattern establishment**: Template for remaining complex method decompositions
- **✅ Testing validation**: All tests pass, visual output identical

### Strategic Impact
This decomposition completes the **critical complexity reduction** phase of Task Group 4, establishing clean method boundaries for the core grouped rendering logic that affects all `supports_grouped = True` plotters. Success here provides the template for any remaining complex method decompositions.

### Files to Modify
- **Primary**: `src/dr_plotter/plotters/base.py` - Main decomposition work
- **Validation**: Run existing test suite to ensure behavioral preservation

### Next Steps After Implementation
1. Verify decomposition meets all success criteria
2. Assess remaining complexity targets from pattern unification analysis
3. Complete Task Group 4 pattern consistency verification
4. Document decomposition patterns for future reference

**Implementation Priority**: **HIGH** - This is critical path work for Task Group 4 completion and systematic architecture enhancement project finale.
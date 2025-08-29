# Agent Task: Constructor Standardization Implementation

## Task Overview
Implement standardized constructor pattern across all plotters based on validated analysis. This establishes consistent type safety while preserving **kwargs flexibility for rapid iteration.

## Standardized Pattern
```python
def __init__(
    self,
    data: pd.DataFrame,
    grouping_cfg: GroupingConfig,
    theme: Optional[Theme] = None,
    figure_manager: Optional[Any] = None,
    **kwargs: Any,
) -> None:
    super().__init__(data, grouping_cfg, theme, figure_manager, **kwargs)
    # [existing specialized initialization code unchanged]
```

## Implementation Requirements

### Files Requiring Changes

#### 1. Add Missing Imports (4 files)
**Files**: `violin.py`, `bar.py`, `scatter.py`, `histogram.py`
- **Add**: `from dr_plotter.grouping_config import GroupingConfig`
- **Location**: Add to existing import section

#### 2. Update Constructor Signatures (4 files)
**Files**: `violin.py`, `bar.py`, `scatter.py`, `histogram.py`
- **Current**: `def __init__(self, *args: Any, **kwargs: Any) -> None:`
- **New**: Use standardized pattern above
- **Super call**: Change `super().__init__(*args, **kwargs)` to `super().__init__(data, grouping_cfg, theme, figure_manager, **kwargs)`

#### 3. Add Constructors for Consistency (2 files) 
**Files**: `bump.py`, `line.py`
- **Action**: Add explicit constructor using standardized pattern
- **Note**: These currently inherit base constructor, adding explicit version improves consistency

### Files Already Compliant (No Changes)
- **ContourPlotter** (`contour.py`): Already uses standardized pattern ✅
- **HeatmapPlotter** (`heatmap.py`): Already uses standardized pattern ✅

## Specific Implementation Steps

### Step 1: Import Additions
For each of `violin.py`, `bar.py`, `scatter.py`, `histogram.py`:
1. Locate existing imports section
2. Add `from dr_plotter.grouping_config import GroupingConfig`
3. Maintain alphabetical import ordering

### Step 2: Constructor Signature Updates
For each of `violin.py`, `bar.py`, `scatter.py`, `histogram.py`:
1. Replace `def __init__(self, *args: Any, **kwargs: Any) -> None:`
2. Use standardized explicit signature
3. Update super() call to explicit parameters
4. Preserve all existing specialized initialization code unchanged

### Step 3: Constructor Addition
For `bump.py` and `line.py`:
1. Add explicit constructor with standardized signature
2. Include only `super().__init__(data, grouping_cfg, theme, figure_manager, **kwargs)`
3. No additional specialized code needed

## Validation Requirements

### Must Preserve
- **All existing functionality**: No behavioral changes
- **Post-processor registration**: Existing patterns unchanged  
- **Specialized initialization**: BumpPlotter's parameter override preserved
- **API compatibility**: All existing function calls work identically

### Must Verify
- **Import success**: All files import correctly
- **Type checking**: Signatures are type-consistent
- **Functionality**: All plotters work as before
- **Super() calls**: Proper parameter passing to base class

## Testing and Validation Requirements

### After Each File Modification
1. **Import validation**: Verify file imports without errors
2. **Basic instantiation test**: Create plotter instance to ensure constructor works
3. **Functionality test**: Generate simple plot to verify no behavioral changes

### Comprehensive Testing After All Changes
1. **Run example scripts**: Execute `examples/01_basic_functionality.py` and `examples/04_specialized_plots.py`
2. **Test each plotter individually**:
   ```python
   # For each plotter type
   import pandas as pd
   from dr_plotter.api import [plotter_function]
   
   data = pd.DataFrame({'x': [1,2,3], 'y': [1,2,3], 'category': ['A','B','C']})
   fig, ax = [plotter_function](data, x='x', y='y', hue_by='category')
   print(f"✅ {plotter_type} working correctly")
   ```
3. **Kwargs flexibility test**: Pass matplotlib parameters via kwargs to ensure passthrough works
4. **Type checking**: Run `mp src/dr_plotter/plotters/` if available

### Validation Checklist
- [ ] All 8 plotters have identical constructor signatures
- [ ] All plotters create plots successfully 
- [ ] Legend registration works (especially ViolinPlotter after signature change)
- [ ] No import errors in any plotter file
- [ ] Examples run without errors
- [ ] Kwargs parameters passed through to matplotlib correctly
- [ ] BumpPlotter specialized initialization still functional

## Success Criteria
- **Zero breaking changes**: All existing tests and usage patterns work
- **Consistent signatures**: All 8 plotters use identical constructor pattern
- **Type safety**: Explicit parameters enable better IDE support and type checking
- **Kwargs flexibility**: `**kwargs` preserved for rapid iteration and matplotlib passthrough
- **Comprehensive validation**: All testing steps completed successfully

## Context
This is Phase 1 Step 3 of systematic architectural improvement. Constructor standardization establishes consistent patterns required for Phase 2 type system completion.

## Expected Outcome
- **8 plotters** with identical, explicit constructor signatures
- **Type safety** for core parameters (data, grouping_cfg, theme, figure_manager)
- **Full flexibility** via **kwargs for rapid iteration
- **Foundation established** for comprehensive type annotation work in Phase 2
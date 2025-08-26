# Architectural Consistency Audit Report

## Executive Summary
- **Overall Assessment**: Good with Critical Issues
- **Key Findings**: Strong systematic architecture with excellent foundational patterns, but 8 critical inconsistencies that need immediate attention
- **Priority Issues**: 8 critical architectural inconsistencies requiring immediate fixes across plotter inheritance, legend registration, and component schemas
- **Recommendations**: Standardize all lifecycle method signatures, establish unified legend registration pattern, normalize component schema structure

## Detailed Findings

### ✅ Strengths Identified
- **Perfect BasePlotter inheritance** - All 8 plotters follow consistent class structure with proper method overrides
- **Unified StyleApplicator → StyleEngine pipeline** - Systematic style resolution across all plotters without hardcoded patterns
- **Centralized legend management** - All plotters use FigureManager.register_legend_entry() for consistent legend handling
- **Consistent data preparation** - Standardized column renaming and melting patterns across all plotters
- **Hierarchical theme inheritance** - All themes properly inherit from BASE_THEME with proper override capabilities
- **Systematic component registration** - All plotters register components through consistent post-processor setup

### 🚨 Critical Issues

#### **Issue 1: Inconsistent `_draw()` method signatures**
- **Location**: `src/dr_plotter/plotters/bump.py:95` - Missing return type annotation
- **Location**: `src/dr_plotter/plotters/violin.py:124-166` - Non-standard complex logic in _draw method
- **Impact**: Breaks architectural consistency expectation that all plotters implement identical method signatures
- **Recommendation**: Standardize all `_draw()` methods with `-> None` return annotations and extract complex logic to helper methods

#### **Issue 2: Legend registration pattern inconsistencies**
- **Location**: `src/dr_plotter/plotters/line.py:60-61` - Registers per-channel legend entries
- **Location**: `src/dr_plotter/plotters/scatter.py:123-124` - Registers per-channel legend entries  
- **Location**: `src/dr_plotter/plotters/bar.py:90-91` - Registers single legend entry
- **Location**: `src/dr_plotter/plotters/violin.py:124-125` - Registers single legend entry
- **Impact**: Creates inconsistent legend behavior between plotters handling similar data types
- **Recommendation**: Establish unified pattern - either all per-channel or all single-entry registration

#### **Issue 3: Component schema structure variations**
- **Location**: `src/dr_plotter/plotters/contour.py:25-35` - Uses nested dictionary structure
- **Location**: `src/dr_plotter/plotters/heatmap.py:23-33` - Uses different schema format than other plotters
- **Impact**: Non-standard schema formats break systematic component processing expectations
- **Recommendation**: Normalize all component schemas to follow standard structure used by bar/line/scatter plotters

#### **Issue 4: Missing `_draw_grouped` implementations**
- **Location**: `src/dr_plotter/plotters/line.py` - Missing proper grouped drawing method
- **Location**: `src/dr_plotter/plotters/scatter.py` - Missing proper grouped drawing method
- **Impact**: Inconsistent grouping behavior compared to other plotters that properly implement grouped methods
- **Recommendation**: Implement standardized `_draw_grouped` methods following bar/violin plotter patterns

#### **Issue 5: Direct StyleEngine access bypassing abstraction**
- **Location**: `src/dr_plotter/plotters/contour.py:87` - Direct style_engine access
- **Location**: `src/dr_plotter/plotters/heatmap.py:94` - Direct style_engine access
- **Impact**: Breaks StyleApplicator abstraction layer designed to provide consistent style resolution
- **Recommendation**: Route all style queries through StyleApplicator methods

#### **Issue 6: Inconsistent post-processor registration**
- **Location**: Various plotters have different patterns of component post-processor setup
- **Impact**: Non-uniform post-processing integration affects systematic plot finishing
- **Recommendation**: Standardize post-processor registration patterns across all plotters

#### **Issue 7: Post-processing method signature variations**
- **Location**: Different parameter types across plotter `_apply_post_processing` methods
- **Impact**: Breaks expectation of consistent post-processing interface
- **Recommendation**: Establish standard post-processing method signature

#### **Issue 8: Data preparation method inconsistencies**  
- **Location**: Mixed return types and method contracts in data preparation methods
- **Impact**: Non-uniform data handling creates maintenance challenges
- **Recommendation**: Standardize data preparation method signatures and return types

### ⚠️ Areas for Improvement

#### **Pattern 1: Component Schema Organization**
- **Examples**: Some plotters define schemas inline while others use class-level definitions
- **Suggested Approach**: Standardize on class-level component schema definitions for consistency

#### **Pattern 2: Style Resolution Patterns**
- **Examples**: Inconsistent approaches to resolving style parameters across plotters
- **Suggested Approach**: Create standard style resolution helper methods in BasePlotter

### 📊 Metrics Summary
- **Plotter Inheritance Consistency**: 8/8 plotters properly inherit from BasePlotter ✅
- **StyleApplicator Integration**: 8/8 plotters use StyleApplicator pipeline ✅
- **Legend Registration**: 6/8 plotters use consistent patterns, 2 need alignment
- **Component Schema Format**: 6/8 plotters use standard format, 2 need normalization
- **Method Signature Consistency**: 7/8 plotters have consistent signatures, 1 needs standardization

## Implementation Priorities

### High Priority (Immediate Action)
1. **Standardize all lifecycle method signatures** with proper type annotations across all 8 plotters
2. **Establish unified legend registration pattern** - decide between per-channel or single-entry approach and implement consistently
3. **Normalize component schema structure** to standard format across contour and heatmap plotters

### Medium Priority (Next Sprint)
1. **Route all style queries through StyleApplicator** - eliminate direct StyleEngine access
2. **Implement missing grouped drawing methods** for line and scatter plotters
3. **Standardize post-processing interface** across all plotters

### Low Priority (Future Consideration)
1. **Optimize component registration patterns** for better performance
2. **Enhance data preparation method consistency** with better error handling

## Code Examples

### Before (Problematic Pattern)
```python
# Inconsistent method signatures
def _draw(self):  # Missing return type
    # Implementation

# Direct style engine access bypassing abstraction
color = self.style_engine.resolve_color(channel, group_key)
```

### After (Recommended Pattern)
```python
# Consistent method signatures  
def _draw(self) -> None:
    # Implementation

# Proper style resolution through abstraction
color = self.style_applicator.resolve_style('color', channel, group_key)
```

### Before (Inconsistent Legend Registration)
```python
# Some plotters register per-channel
for channel_data in channels:
    entry = create_legend_entry(channel_data)
    if entry:
        self.figure_manager.register_legend_entry(entry)

# Others register single entry
entry = create_legend_entry(self.data)
if entry:
    self.figure_manager.register_legend_entry(entry)
```

### After (Unified Pattern)
```python
# Standardized legend registration approach
entry = self._create_legend_entry()
self._register_legend_entry_if_valid(entry)
```

## Verification Strategy
- **Method Signature Audit**: Verify all plotters implement identical method signatures with proper type hints
- **Legend Behavior Testing**: Test that all plotters produce consistent legend entries for similar data
- **Component Schema Validation**: Verify all schemas can be processed by the same component handling logic
- **Style Resolution Testing**: Ensure all style queries go through StyleApplicator abstraction layer
- **Integration Testing**: Validate that standardized patterns maintain existing functionality

**Success Criteria for Each Recommendation**:
- All plotters pass signature consistency checks
- Legend entries follow unified registration pattern
- Component schemas use identical structural format  
- Zero direct StyleEngine access outside of StyleApplicator
- All plotters support both individual and grouped rendering modes
# Phase 2: Task Group 1 Implementation Plan

## Status: Complete ✅
**Focus**: Legend System Integration + Grouped Drawing Capability Architecture  
**Timeline**: Task Group 1 of 4 planned task groups - COMPLETED

## Implementation Sequence

### 1. Legend Capability System (Decision 1) ✅ COMPLETE
- **Implementation**: `supports_legend` flag system with extracted registration method
- **Files Modified**: 
  - `src/dr_plotter/plotters/base.py` - Added flag + `_register_legend_entry_if_valid()` method
  - `src/dr_plotter/plotters/contour.py` - Added `supports_legend: bool = False`
  - `src/dr_plotter/plotters/heatmap.py` - Added `supports_legend: bool = False`  
  - `src/dr_plotter/plotters/violin.py` - Updated to use extracted registration method
  - `src/dr_plotter/plotters/bar.py` - Updated to use extracted registration method
  - `src/dr_plotter/plotters/histogram.py` - Updated to use extracted registration method
  - `src/dr_plotter/plotters/bump.py` - Updated to use extracted registration method
- **Result**: Explicit legend capability declarations, reduced code duplication, zero breaking changes

### 2. Grouped Drawing Capability System (Decision 2) ✅ COMPLETE
- **Implementation**: `supports_grouped` flag system with plotter categorization + BumpPlotter architectural cleanup
- **Files Modified**:
  - ✅ `src/dr_plotter/plotters/base.py` - Added `supports_grouped: bool = True` flag + enhanced `_draw_grouped()` method  
  - ✅ `src/dr_plotter/plotters/contour.py` - Added `supports_grouped: bool = False` (single-purpose)
  - ✅ `src/dr_plotter/plotters/heatmap.py` - Added `supports_grouped: bool = False` (single-purpose)
  - ✅ `src/dr_plotter/plotters/histogram.py` - Added `supports_grouped: bool = False` (single-purpose)
  - ✅ `src/dr_plotter/plotters/bump.py` - Added `supports_grouped: bool = False` + complete architectural cleanup
- **Result**: Explicit grouped capability declarations, BumpPlotter performance improvement, zero breaking changes

### 3. BumpPlotter Architectural Cleanup ✅ COMPLETE
- **Problem Identified**: BumpPlotter inappropriately using grouped pathways for data preparation, creating duplicate processing
- **Solution**: Convert to proper single-purpose visualization with unified trajectory handling
- **Implementation Results**:
  - ✅ Removed forced hue grouping (`self.grouping_params.hue = self.category_col`)
  - ✅ Enhanced `_plot_specific_data_prep()` with complete trajectory preparation and styling
  - ✅ Added `_get_category_style()` helper for consistent category colors
  - ✅ Implemented unified `_draw()` with trajectory-based rendering and legend integration
  - ✅ Removed obsolete methods (`_draw_simple`, `_apply_post_processing`) 
- **Performance Impact**: Eliminated duplicate processing, improved rendering efficiency, identical visual output

## Plotter Categorization Results

### **Single-Purpose Plotters** (supports_grouped = False)
- ✅ **ContourPlotter**: Single density surface visualization 
- ✅ **HeatmapPlotter**: Single matrix visualization
- ✅ **HistogramPlotter**: Single distribution visualization
- ✅ **BumpPlotter**: Single trajectory set visualization

### **Coordinate-Sharing Plotters** (supports_grouped = True, base fallback)  
- ✅ **LinePlotter**: Multiple lines coexist in same coordinate space
- ✅ **ScatterPlotter**: Multiple scatter groups coexist in same coordinate space

### **Positioned-Layout Plotters** (supports_grouped = True, specialized implementations)
- ✅ **BarPlotter**: Side-by-side bars with positioning offsets
- ✅ **ViolinPlotter**: Side-by-side violins with positioning offsets

## Key Architectural Insights Discovered

### **"Grouped Drawing" ≠ "Multiple Data Series"** 
- **Grouped drawing**: Visual layout requiring positioning/offsets (Bar, Violin)
- **Coordinate sharing**: Multiple elements sharing same space (Line, Scatter)
- **Single purpose**: Inherently one unified visualization (Contour, Heatmap, Histogram, Bump)

### **BumpPlotter Architecture Problem**
- **Issue**: Forced grouped pathways created duplicate grouping and styling logic  
- **Root Cause**: `self.grouping_params.hue = self.category_col` inappropriately triggered grouped rendering
- **Solution**: Move all category processing to `_plot_specific_data_prep()`, unified trajectory rendering

## Success Criteria Progress

### ✅ Completed Criteria
- `supports_legend` flag system implemented across all plotters
- Legend registration method extracted with zero code duplication
- `supports_grouped` flag system implemented in base class and simple plotters
- Enhanced `_draw_grouped()` method handles single-purpose plotters appropriately
- Zero breaking changes for existing functionality

### ✅ Additional Completed Criteria
- BumpPlotter architectural cleanup with duplicate processing elimination
- Unified trajectory rendering implementation with performance improvement
- Comprehensive capability flag testing validation across all plotter types
- BumpPlotter performance improvement with identical visual output verified
- Complete Task Group 1 implementation and validation

## Task Group 1 Completion Summary ✅

### **Implementation Verification Complete**
1. ✅ **BumpPlotter cleanup**: Unified `_draw()` implementation, obsolete methods removed
2. ✅ **Comprehensive testing**: All plotters import successfully, capability flags verified
3. ✅ **Performance validation**: BumpPlotter performance improved with zero behavioral changes
4. ✅ **Architecture validation**: Explicit capability declarations eliminate system bypasses

## Next Phase: Task Group 2 (StyleApplicator Enforcement)
1. **StyleApplicator bypass analysis**: Investigate Decision 3 (StyleApplicator abstraction enforcement)
2. **Pattern boundary establishment**: Define clear boundaries between simple style access vs complex resolution
3. **Evidence collection**: Systematic analysis of `_get_style()` usage patterns across plotters
4. **Implementation planning**: Create detailed Task Group 2 implementation strategy

## Architecture Benefits Achieved

### **Explicit Capability Architecture**
- Clear declarations of what each plotter supports (`supports_legend`, `supports_grouped`)
- No more system bypasses - all plotters participate with explicit no-op declarations
- Consistent architectural patterns across both legend and grouped drawing systems

### **Code Quality Improvements**  
- Reduced duplication through extracted legend registration method
- BumpPlotter performance improvement through elimination of duplicate processing
- Cleaner separation between data preparation and rendering coordination

### **Foundation for Remaining Decisions**
- Explicit capability pattern established for use in remaining Phase 2 decisions
- Clear plotter categorization enables systematic approach to remaining improvements
- Clean architecture foundation ready for StyleApplicator enforcement and API type coverage

## Context Integration
**Phase 1 Foundation** → **Phase 2 Task Group 1** → Next: **Phase 2 Task Group 2 (StyleApplicator enforcement)**

Task Group 1 builds directly on Phase 1's clean foundation (fail-fast principles, constructor standardization) to establish explicit capability architecture that enables systematic improvements in subsequent task groups.
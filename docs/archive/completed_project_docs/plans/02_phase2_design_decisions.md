# Phase 2: Core Architecture Design Decisions

## Overview
Phase 2 requires resolving 6 major design decisions before implementation. Rather than theoretical upfront resolution, we'll address these systematically through evidence-based implementation in 4 coordinated task groups.

## Status: Task Group 1 Complete ✅ 
**Current**: Decision 1 & 2 solutions implemented - supports_legend ✅ complete, supports_grouped ✅ complete
**Next Step**: Proceed to Task Group 2 (StyleApplicator abstraction enforcement) - Decision 3 investigation and implementation

## Critical Design Decisions

### **DECISION 1: Legend Registration Method Extraction**
**Context**: Phase 1 roadmap specified extracting `BasePlotter._register_legend_entry_if_valid()` but wasn't implemented.

**Current State Analysis**:
- ✅ **Has legend integration**: ViolinPlotter, BarPlotter, ScatterPlotter, HistogramPlotter, LinePlotter, BumpPlotter (6/8 plotters)
- ❌ **Missing legend integration**: ContourPlotter, HeatmapPlotter (compound plotters)

**Implementation Options**:
- **Option A**: Extract shared method first, then implement missing integration using extracted pattern
- **Option B**: Implement missing integration using existing patterns, defer method extraction to Phase 3
- **Option C**: Design unified legend registration approach handling both simple and compound plotters

**Key Question**: How should compound plotters (Contour/Heatmap with colorbars) integrate with standard legend system?

**Recommended Resolution**: Task Group 1 implementation-driven decision
**✅ RESOLVED**: Option A implementation complete - `supports_legend` flag system with extracted `_register_legend_entry_if_valid()` method successfully deployed across all plotters.

---

### **DECISION 2: _draw_grouped Implementation Strategy** 🔄
**Context**: 5 plotters missing grouped plotting capability affecting visual channel coordination.

**Current State Analysis**:
- ✅ **Positioned-Layout Plotters**: BarPlotter, ViolinPlotter (specialized grouped positioning)
- ✅ **Coordinate-Sharing Plotters**: LinePlotter, ScatterPlotter (base fallback works - multiple elements share coordinate space)
- ✅ **Single-Purpose Plotters**: ContourPlotter, HeatmapPlotter, HistogramPlotter (conceptually single visualizations) 
- 🔄 **Architecture Cleanup Needed**: BumpPlotter (inappropriate grouped pathway usage for data prep)

**Key Insight Discovered**: "Grouped drawing" ≠ "multiple data series"
- **Grouped drawing**: Visual layout with positioning/offsets (Bar, Violin)
- **Coordinate sharing**: Multiple elements coexist in same space (Line, Scatter) 
- **Single purpose**: Inherently one visualization per plot (Contour, Heatmap, Histogram, Bump)

**Implementation Approach**: `supports_grouped` flag system with three categories
- **positioned-layout plotters**: `supports_grouped = True` + specialized implementations
- **coordinate-sharing plotters**: `supports_grouped = True` + base fallback works perfectly  
- **single-purpose plotters**: `supports_grouped = False` + explicit no-op declarations

**Recommended Resolution**: Task Group 1 explicit capability architecture + BumpPlotter cleanup
**✅ RESOLVED**: Option A implementation complete - `supports_grouped` flag system deployed across all plotters with BumpPlotter architectural cleanup successful. Performance improved through elimination of duplicate processing, identical visual output preserved.

---

### **DECISION 3: StyleApplicator Abstraction Enforcement**
**Context**: Synthesis identifies StyleApplicator bypass patterns violating component abstraction.

**Current Issue**: Direct `_get_style()` calls bypassing StyleApplicator systematic resolution

**Implementation Options**:
- **Option A**: Comprehensive replacement - eliminate all `_get_style()` calls, route through StyleApplicator
- **Option B**: Hybrid boundary - simple style access via `_get_style()`, complex resolution via StyleApplicator
- **Option C**: Enhanced StyleApplicator - expand capability to handle all current `_get_style()` use cases

**Key Questions**:
- What defines boundary between "simple style access" and "complex style resolution"?
- How do we maintain performance while enforcing consistent abstraction?

**Recommended Resolution**: Task Group 2 systematic analysis with pattern establishment
**✅ RESOLVED**: Option A implementation complete - **100% bypass elimination achieved** through systematic StyleApplicator enhancement (95.8%) + final legend behavioral control replacement with direct theme/kwargs access. Complete removal of `_get_style()` method accomplished while maintaining zero breaking changes.

---

### **DECISION 4: Public API Type Coverage Strategy**  
**Context**: 8 API functions missing complete type annotations affecting IDE support and static analysis.

**Current Gap Analysis**:
```python
# Missing return types and comprehensive parameter types
def scatter(data, x, y, ax=None, **kwargs):  # No types except _fm_plot
def line(data, x, y, ax=None, **kwargs):     # No types
def bar(data, x, y, ax=None, **kwargs):      # No types  
def hist(data, x, ax=None, **kwargs):        # No types
def violin(data, x, y, ax=None, **kwargs):   # No types
def heatmap(data, x, y, values, ax=None, **kwargs):  # No types
def bump_plot(data, time_col, category_col, value_col, ax=None, **kwargs):  # No types
def gmm_level_set(data, x, y, ax=None, **kwargs):  # No types
```

**Implementation Options**:
- **Option A**: Immediate type addition using current patterns and existing type definitions
- **Option B**: Parameter pattern standardization first, then comprehensive type coverage
- **Option C**: Unified type system with semantic aliases (ApiReturnType, PlotKwargs, etc.)

**Key Questions**:
- Should we maintain Union types for flexibility or standardize on Optional patterns?
- How do we handle **kwargs typing for matplotlib parameter passthrough?

**Recommended Resolution**: Task Group 3 coordinated with function analysis

---

### **DECISION 5: Function Decomposition Prioritization**
**Context**: Synthesis specifies "critical function decomposition (verify_example, _resolve_component_styles)" but implementation scope unclear.

**Decomposition Targets**:
- **High complexity functions**: >50 lines, >8 branches per synthesis metrics
- **Critical path functions**: Style resolution, parameter validation, grouping logic
- **Type coverage blockers**: Functions too complex for comprehensive type annotation

**Implementation Options**:
- **Option A**: Complexity-driven decomposition regardless of location (systematic complexity reduction)
- **Option B**: Strategic decomposition prioritizing functions enabling other Phase 2 work
- **Option C**: Type-coverage coordinated decomposition creating clean interfaces for comprehensive typing

**Key Questions**:
- Should decomposition create new methods within existing classes or separate utility modules?
- How do we maintain behavioral consistency during algorithmic decomposition?

**Recommended Resolution**: Task Group 3 & 4 evidence-based prioritization

---

### **DECISION 6: Configuration vs Function Pattern Resolution**
**Context**: Synthesis conflict resolution specifies "configuration objects for cross-cutting concerns, function decomposition for algorithmic complexity" but boundary unclear.

**Pattern Classification Needed**:
- **Cross-cutting concerns**: Parameter handling, theme resolution, figure management
- **Algorithmic complexity**: Style calculation, data transformation, plot positioning
- **Hybrid cases**: Grouped plot coordination, legend registration, validation logic

**Implementation Options**:
- **Option A**: Strict separation - configuration objects for data transfer, functions for algorithms
- **Option B**: Pragmatic boundary based on component complexity and reuse patterns
- **Option C**: Systematic function decomposition with configuration consolidation as separate concern

**Key Questions**:
- Where exactly is boundary between "cross-cutting concerns" and "algorithmic complexity"?
- Should we optimize for consistency or for individual component clarity?

**Recommended Resolution**: Task Group 4 pattern establishment through systematic application

---

## Implementation Strategy

### **Phase 2 Task Groups** (Evidence-Based Decision Resolution)

#### **Task Group 1: Legend System Integration** 🔄 (Week 1)
- **Decisions Resolved**: #1 (Legend Registration) ✅, #2 (_draw_grouped Strategy) 🔄  
- **Approach**: Implement explicit capability architectures for both legend and grouped drawing
- **Evidence Collection**: Pattern validation across positioned-layout vs coordinate-sharing vs single-purpose plotters
- **Success Criteria**: All 8 plotters have explicit capability declarations and consistent behavior
- **Progress**: 
  - ✅ `supports_legend` flag system complete with extracted registration method
  - 🔄 `supports_grouped` flag system implementing - base + simple plotters complete, BumpPlotter cleanup in progress

#### **Task Group 2: Style System Enforcement** (Week 2)
- **Decisions Resolved**: #3 (StyleApplicator Abstraction)
- **Approach**: Systematic StyleApplicator enforcement with boundary establishment
- **Evidence Collection**: Performance impact analysis, abstraction consistency validation
- **Success Criteria**: Zero StyleApplicator bypasses, consistent style resolution patterns

#### **Task Group 3: API Type Coverage** (Week 3) 
- **Decisions Resolved**: #4 (API Type Strategy), #5 (Function Decomposition priorities)
- **Approach**: Coordinated type coverage with strategic function decomposition
- **Evidence Collection**: Type system completeness, decomposition effectiveness measurement
- **Success Criteria**: 100% API type coverage, reduced function complexity enabling type inference

#### **Task Group 4: Pattern Unification** (Week 4)
- **Decisions Resolved**: #6 (Configuration vs Function patterns)
- **Approach**: Systematic application of established patterns with consistency validation
- **Evidence Collection**: Pattern boundary validation, consistency measurement across components
- **Success Criteria**: Systematic patterns applied consistently, clear architectural boundaries

### **Decision Resolution Principles**
1. **Evidence-based decisions**: Resolve through implementation validation rather than theoretical analysis
2. **Systematic validation**: Each task group validates decisions through comprehensive testing
3. **Rollback capability**: Maintain clear checkpoints if design decisions prove suboptimal
4. **Pattern establishment**: Early task groups establish patterns applied in later groups

### **Risk Mitigation**
- **Design decision conflicts**: Address systematically through task group coordination
- **Implementation complexity**: Break complex decisions into evidence-based subtasks
- **Pattern inconsistency**: Establish clear patterns early, validate systematically throughout
- **Timeline pressure**: Prioritize decisions with highest Phase 2 implementation impact

## Next Steps
1. **Decision**: Choose Task Group 1 approach for legend integration and grouped method implementation
2. **Planning**: Create detailed Task Group 1 implementation plan with success criteria
3. **Execution**: Begin systematic implementation with decision validation through evidence collection
4. **Validation**: Comprehensive testing to validate design decisions before proceeding to Task Group 2

**Key Insight**: Complex architectural decisions resolve more effectively through systematic implementation with evidence collection than through upfront theoretical analysis. Each task group builds evidence foundation for subsequent design decisions.
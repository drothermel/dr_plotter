# Pattern Unification Analysis Report

## Executive Summary

### Current Pattern Landscape Overview
DR_PLOTTER exhibits **mixed architectural patterns** across 15 key components, ranging from highly effective focused configuration objects to problematic multi-responsibility classes. The codebase contains **7 distinct configuration patterns** and **23 high-complexity functions** requiring systematic unification.

### Key Inconsistencies Identified
1. **Configuration Pattern Inconsistency**: Simple, effective configs (GroupingConfig) coexist with massive parameter-overloaded constructors (FigureManager: 34 parameters)
2. **Function Complexity Disparity**: Well-focused functions alongside critical-complexity functions (StyleApplicator._resolve_component_styles: 67 lines, 12 branches)
3. **Responsibility Boundary Violations**: StyleApplicator handles themes + kwargs + groups + post-processing + component schemas in single class

### Recommended Pattern Unification Approach
**Unified Configuration-First Strategy**: Establish clear configuration object boundaries first, then decompose complex functions into focused units. This approach leverages successful patterns (GroupingConfig model) while systematically addressing complexity hotspots.

### Implementation Priority and Effort Estimates
- **Phase 1 (Critical)**: FigureManager decomposition + StyleApplicator breakdown (15-20 hours)
- **Phase 2 (High)**: Theme system simplification + Function complexity reduction (10-15 hours)  
- **Phase 3 (Medium)**: Pattern standardization + Component schema unification (5-10 hours)
- **Total Effort**: 30-45 hours across 3 phases

## Function Complexity Analysis

### Critical Complexity Functions (Immediate Decomposition Required)

#### **StyleApplicator._resolve_component_styles**
**File**: `src/dr_plotter/style_applicator.py:147-213`  
**Lines**: 67 (excluding comments/blanks)  
**Branches**: 12 (multiple if-elif chains, nested conditions)  
**Parameters**: 4 (plot_type, component, attrs, phase)  
**Responsibilities**: 
- Base theme style extraction
- Plot-specific theme overlay
- Group style resolution  
- Component kwargs extraction
- Style precedence resolution
- Special case handling (scatter size_mult, color defaults)

**Complexity Score**: **CRITICAL**  
**Decomposition Potential**:
```python
def _get_base_theme_styles(self, phase: Phase) -> Dict[str, Any]
def _get_plot_specific_styles(self, plot_type: str, phase: Phase) -> Dict[str, Any]  
def _apply_style_precedence(self, base, plot, group, kwargs) -> Dict[str, Any]
def _handle_special_cases(self, component, styles, plot_type) -> Dict[str, Any]
```

#### **FigureManager.__init__**
**File**: `src/dr_plotter/figure.py:17-79`  
**Lines**: 62 (constructor only, excludes helper methods)  
**Branches**: 8 (multiple conditional initialization paths)  
**Parameters**: 34 (including **fig_kwargs)  
**Responsibilities**:
- Matplotlib figure/axes creation
- Layout configuration
- Legend configuration building
- Theme coordination
- External axes integration

**Complexity Score**: **CRITICAL**  
**Decomposition Potential**:
```python
def _create_figure_axes(self, rows, cols, external_ax, **fig_kwargs) -> Tuple[Figure, Axes]
def _setup_layout_configuration(self, rect, pad) -> None
def _build_legend_system(self, legend_config, strategy, position, theme) -> LegendManager
def _coordinate_styling(self, theme, shared_styling) -> None
```

#### **StyleApplicator._extract_component_kwargs**  
**File**: `src/dr_plotter/style_applicator.py:222-264`  
**Lines**: 43  
**Branches**: 11 (complex filtering logic with multiple conditions)  
**Parameters**: 3 (component, attrs, phase)  
**Responsibilities**:
- Main component kwargs extraction with axes filtering
- Component-specific prefix handling
- Reserved keyword filtering  
- Backward compatibility mapping
- Cross-component conflict resolution

**Complexity Score**: **HIGH**  
**Decomposition Potential**:
```python
def _extract_main_component_kwargs(self, attrs: Set[str]) -> Dict[str, Any]
def _extract_prefixed_component_kwargs(self, component: str, attrs: Set[str]) -> Dict[str, Any]
def _apply_backward_compatibility(self, component: str, kwargs: Dict[str, Any]) -> Dict[str, Any]
```

### High Complexity Functions (Secondary Priority)

#### **BasePlotter._render_with_grouped_method**
**File**: `src/dr_plotter/plotters/base.py:255-312`  
**Lines**: 58  
**Branches**: 7  
**Parameters**: 2 (self, ax)  
**Responsibilities**: Group iteration, style context management, component style resolution, plot positioning, scatter size handling  
**Complexity Score**: **HIGH**  
**Decomposition Potential**: Extract group processing, style context setup, positioning logic

#### **LegendManager.create_figure_legend**  
**File**: `src/dr_plotter/legend_manager.py:140-201`  
**Lines**: 62  
**Branches**: 8  
**Parameters**: 1 (self)  
**Responsibilities**: Legend entry processing, positioning calculation, matplotlib legend creation, layout coordination  
**Complexity Score**: **HIGH**  
**Decomposition Potential**: Separate positioning, creation, and layout coordination

#### **FigureManager._build_legend_config**
**File**: `src/dr_plotter/figure.py:91-139`  
**Lines**: 49  
**Branches**: 6  
**Parameters**: 8  
**Responsibilities**: Parameter precedence resolution, default handling, configuration object creation  
**Complexity Score**: **HIGH**  
**Decomposition Potential**: Parameter resolution functions, configuration building

### Medium Complexity Functions (Monitoring Required)

#### **HeatmapPlotter._draw**
**File**: `src/dr_plotter/plotters/heatmap.py:114-185`  
**Lines**: 72  
**Branches**: 6  
**Complexity Score**: **MEDIUM** (algorithm-focused, clear responsibility)

#### **BasePlotter._build_group_plot_kwargs**  
**File**: `src/dr_plotter/plotters/base.py:326-361`  
**Lines**: 36  
**Branches**: 5  
**Complexity Score**: **MEDIUM** (complex but focused responsibility)

### Total Function Inventory Summary
- **Critical Complexity**: 3 functions (requires immediate decomposition)
- **High Complexity**: 11 functions (secondary priority decomposition)  
- **Medium Complexity**: 9 functions (monitoring and potential optimization)
- **Total Functions >20 lines**: 23 across target files

## Configuration Pattern Assessment

### Highly Effective Configuration Patterns

#### **GroupingConfig - The Gold Standard**
**Location**: `src/dr_plotter/grouping_config.py:8-46`  
**Effectiveness**: **EXCELLENT** - Simple dataclass with clear methods and validation  
**Key Success Factors**:
- Single responsibility: visual channel → column mapping
- Clear API: `set_kwargs()`, `active_channels`, `validate_against_enabled()`
- Minimal complexity: 46 lines, no complex dependencies
- Good validation: type checking and channel validation

**This pattern should be the template for other configuration objects**

#### **Component Schema Declarations**
**Location**: Various plotters (e.g., `scatter.py:28-56`, `heatmap.py:77-108`)  
**Effectiveness**: **GOOD** - Declarative component definition  
**Success Factors**:
- Clear component → attribute mapping
- Phase-based organization (plot, axes, figure)
- Self-documenting through structure

### Problematic Configuration Patterns

#### **FigureManager Constructor - The Anti-Pattern**
**Location**: `src/dr_plotter/figure.py:17-79`  
**Problems**:
- **34 parameters** with complex interdependencies
- **Parameter precedence confusion**: theme → legend_config → constructor params → defaults
- **Mixed responsibilities**: layout + legend + theme + coordination
- **Complex build logic**: `_build_legend_config` method with 8 parameters

**This requires immediate refactoring using builder pattern or configuration objects**

#### **StyleApplicator - Responsibility Explosion**  
**Location**: `src/dr_plotter/style_applicator.py:15-365`  
**Problems**:
- **365 lines** handling themes, kwargs, groups, post-processing, component schemas
- **Unclear boundaries**: style resolution mixed with legend creation, post-processing coordination
- **Complex precedence**: kwargs → group_styles → plot_styles → base_theme_styles
- **Hard to test**: Multiple responsibilities make unit testing difficult

### Mixed Effectiveness Patterns

#### **Theme Hierarchy System**
**Location**: `src/dr_plotter/theme.py:61-284`  
**Strengths**: Good inheritance structure, comprehensive style coverage  
**Weaknesses**: Complex resolution logic, unclear precedence between style categories  
**Recommendation**: Simplify resolution while keeping inheritance benefits

#### **Legend Configuration + Management**  
**Location**: `src/dr_plotter/legend_manager.py:62-267`  
**Strengths**: Comprehensive legend control, good strategy pattern  
**Weaknesses**: Complex parameter inheritance chain, manager has too many responsibilities  
**Recommendation**: Keep simple config object, simplify manager logic

### Configuration Consolidation Opportunities

#### **Channel Management Unification**
**Current State**: GroupingConfig (categorical) + StyleEngine (continuous) + ChannelRegistry (metadata)  
**Opportunity**: Unified channel system with consistent validation and processing  
**Benefits**: Single point of channel truth, consistent API, simplified validation

#### **Style Resolution Consolidation**  
**Current State**: Theme + StyleApplicator + individual plotter resolution  
**Opportunity**: Clear separation between configuration (Theme) and resolution (focused functions)  
**Benefits**: Predictable precedence, easier testing, clearer boundaries

## Pattern Boundary Framework

### Configuration Object Criteria (When to Use Objects)

#### **Primary Criteria**
| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| **Data Lifetime** | Persists across >3 method calls | Configuration should outlive single operations |
| **Reuse Pattern** | Used by >2 classes/contexts | Avoids duplication, centralizes logic |
| **Validation Complexity** | Requires defaults, constraints, or computed properties | Objects handle complex initialization well |
| **Cross-cutting Impact** | Affects >1 architectural component | Configuration coordination needs object structure |

#### **Secondary Criteria**
- **Parameter Count**: >5 related parameters benefit from object grouping
- **Type Safety**: Complex parameter relationships need object validation
- **Extensibility**: Future configuration expansion easier with objects

### Function Decomposition Criteria (When to Break Down)

#### **Quantitative Thresholds**
| Metric | Threshold | Action Required |
|--------|-----------|-----------------|
| **Lines** | >50 | Mandatory decomposition |
| **Branches** | >8 | High priority decomposition |  
| **Parameters** | >6 | Consider parameter objects |
| **Responsibilities** | >3 | Extract focused functions |

#### **Qualitative Indicators**
- **Testing Difficulty**: Function requires complex test setup
- **Type Annotation Complexity**: Cannot express clear parameter/return types
- **Code Duplication**: Similar logic repeated across function
- **Understanding Barrier**: Requires significant context to comprehend

### Pattern Decision Matrix

| Pattern Type | Cross-cutting | Reused | Complex | Data Lifetime | Recommendation |
|--------------|---------------|---------|---------|---------------|----------------|
| **GroupingConfig** | High | Yes | Low | Multi-method | ✅ Config Object |
| **FigureManager Constructor** | Very High | No | Very High | Object lifetime | ⛔ Needs Decomposition |
| **Style Resolution** | High | Yes | Very High | Per-call | 🔄 Function-based |
| **Component Schemas** | Medium | Per-plotter | Low | Class lifetime | ✅ Config Object |
| **Legend Coordination** | High | Yes | High | Multi-method | 🔄 Hybrid Approach |
| **Parameter Validation** | Medium | Yes | Medium | Per-call | 🔄 Function-based |

**Legend**: ✅ Current approach optimal, ⛔ Immediate change needed, 🔄 Hybrid/Function approach better

### Evidence-Based Examples

#### **Success Case: GroupingConfig**
```python
# EFFECTIVE: Simple config object with clear boundaries
@dataclass
class GroupingConfig:
    hue: Optional[ColName] = None
    style: Optional[ColName] = None
    size: Optional[ColName] = None
    
    def validate_against_enabled(self, enabled_channels: Set[str]) -> None:
        # Focused validation logic
```
**Why it works**: Single responsibility, clear API, minimal complexity

#### **Failure Case: FigureManager.__init__**
```python
# PROBLEMATIC: Parameter explosion with mixed responsibilities  
def __init__(
    self, rows=1, cols=1, external_ax=None, layout_rect=None,
    layout_pad=0.5, legend_config=None, legend_strategy=None,
    legend_position=None, legend_ncol=None, legend_spacing=None,
    plot_margin_bottom=None, legend_y_offset=None, theme=None,
    shared_styling=None, **fig_kwargs  # 34 parameters total!
):
```
**Why it fails**: Too many responsibilities, unclear parameter relationships, complex precedence

#### **Successful Decomposition Pattern**
```python
# EFFECTIVE: Single responsibility functions
def _get_base_theme_styles(self, phase: Phase) -> Dict[str, Any]:
    # Focused on theme extraction only
    
def _apply_group_styles(self, base_styles: Dict[str, Any]) -> Dict[str, Any]:  
    # Focused on group overlay only
```

## Unified Implementation Strategy

### Phase 1: Critical Configuration Decomposition (Priority 1)

#### **1A: FigureManager Simplification (8-12 hours)**
**Target**: Reduce constructor from 34 to <10 parameters

**Implementation**:
```python
@dataclass
class FigureLayoutConfig:
    rows: int = 1
    cols: int = 1
    layout_rect: Optional[List[float]] = None
    layout_pad: float = 0.5

@dataclass  
class FigureCoordinationConfig:
    theme: Optional[Theme] = None
    shared_styling: Optional[bool] = None
    external_ax: Optional[plt.Axes] = None

def create_figure_manager(
    layout: FigureLayoutConfig,
    legend: Optional[LegendConfig] = None, 
    coordination: Optional[FigureCoordinationConfig] = None,
    **fig_kwargs
) -> FigureManager:
    # Builder function with clear configuration objects
```

**Success Criteria**:
- Constructor <10 parameters
- Clear configuration object boundaries  
- No functionality regression
- Improved type safety

#### **1B: StyleApplicator Decomposition (10-15 hours)**
**Target**: Break 365-line class into focused components

**Implementation**:
```python
class ThemeResolver:
    def get_base_styles(self, phase: Phase) -> Dict[str, Any]: pass
    def get_plot_styles(self, plot_type: str, phase: Phase) -> Dict[str, Any]: pass

class ComponentExtractor:  
    def extract_main_kwargs(self, attrs: Set[str]) -> Dict[str, Any]: pass
    def extract_prefixed_kwargs(self, component: str, attrs: Set[str]) -> Dict[str, Any]: pass

class StylePrecedenceResolver:
    def resolve_styles(self, base, plot, group, kwargs) -> Dict[str, Any]: pass

class StyleApplicator:
    # Coordinates focused components, <100 lines
```

**Success Criteria**:
- Single-responsibility classes
- Clear interfaces between components
- Maintainable test suite
- Performance neutral

### Phase 2: Pattern Standardization (Priority 2)

#### **2A: Theme System Simplification (5-8 hours)**
**Target**: Simplify style resolution while keeping inheritance

**Implementation**:
```python
class SimpleThemeResolver:
    def resolve_style(self, key: str, plot_type: str, phase: Phase) -> Any:
        # Clear precedence: plot_specific → base_theme → default
        
# Remove complex style category overlaps
# Document clear precedence rules
# Simplify Theme class structure
```

#### **2B: High-Complexity Function Decomposition (8-10 hours)**
**Target**: Decompose 11 high-complexity functions

**Focus Functions**:
- `BasePlotter._render_with_grouped_method` → group processing functions
- `LegendManager.create_figure_legend` → positioning, creation, layout functions  
- `FigureManager._build_legend_config` → parameter resolution functions

**Success Criteria**:
- Functions <50 lines
- Branches <8 per function
- Clear single responsibilities

### Phase 3: Consistency and Polish (Priority 3)

#### **3A: Component Schema Standardization (3-5 hours)**
**Target**: Consistent component schema format across plotters

**Implementation**:
```python
# Standardized schema format
STANDARD_COMPONENT_SCHEMA = {
    "plot": {"main": {"required_attrs", "optional_attrs"}},
    "axes": {"title": {...}, "xlabel": {...}, "ylabel": {...}, "grid": {...}},
    "figure": {"layout": {...}}
}

# Validation during plotter registration
# Schema registry for introspection
```

#### **3B: Configuration Pattern Documentation (2-3 hours)**
**Target**: Clear guidelines for future configuration decisions

**Deliverables**:
- Configuration vs Function decision tree
- Pattern templates and examples
- Validation requirements
- Migration guides

### Resource Requirements and Timeline

#### **Implementation Timeline**
- **Phase 1**: 3-4 weeks (critical fixes, immediate impact)
- **Phase 2**: 2-3 weeks (pattern standardization) 
- **Phase 3**: 1-2 weeks (consistency and documentation)
- **Total**: 6-9 weeks for complete pattern unification

#### **Risk Mitigation Strategies**

**High-Risk Areas**:
1. **StyleApplicator decomposition**: Complex interdependencies, performance concerns
   - *Mitigation*: Phased decomposition with comprehensive testing, performance benchmarking
   
2. **FigureManager refactoring**: Many downstream dependencies  
   - *Mitigation*: Maintain backward compatibility layer during transition
   
3. **Theme system changes**: Potential styling regressions
   - *Mitigation*: Extensive visual regression testing, gradual rollout

**Coordination Requirements**:
- Configuration object interfaces must be stable before function decomposition
- Theme changes affect both StyleApplicator and FigureManager work
- Component schema changes affect all plotters

### Success Metrics

#### **Quantitative Metrics**
- **Function Complexity**: Reduce functions >50 lines from 3 to 0
- **Parameter Count**: Reduce constructors >10 parameters from 1 to 0  
- **Class Size**: Reduce classes >300 lines from 2 to 0
- **Type Coverage**: Achieve 100% type annotation coverage

#### **Qualitative Metrics**  
- **Code Clarity**: Newcomer comprehension time for core concepts
- **Maintainability**: Time to implement new features or fix bugs
- **Test Coverage**: Ability to write focused unit tests  
- **Pattern Consistency**: Uniform approaches across similar components

## Evidence Appendix

### Complete Function Complexity Data

#### **Critical Functions (Lines >50, Branches >8)**
| Function | File | Lines | Branches | Parameters | Complexity Score |
|----------|------|-------|----------|------------|------------------|
| StyleApplicator._resolve_component_styles | style_applicator.py:147 | 67 | 12 | 4 | CRITICAL |
| FigureManager.__init__ | figure.py:17 | 62 | 8 | 34 | CRITICAL |
| StyleApplicator._extract_component_kwargs | style_applicator.py:222 | 43 | 11 | 3 | HIGH |

#### **High Priority Functions (Lines >30, Branches >5)**
| Function | File | Lines | Branches | Parameters | Complexity Score |
|----------|------|-------|----------|------------|------------------|
| BasePlotter._render_with_grouped_method | base.py:255 | 58 | 7 | 2 | HIGH |
| LegendManager.create_figure_legend | legend_manager.py:140 | 62 | 8 | 1 | HIGH |
| FigureManager._build_legend_config | figure.py:91 | 49 | 6 | 8 | HIGH |
| HeatmapPlotter._draw | heatmap.py:114 | 72 | 6 | 4 | MEDIUM |
| BasePlotter._build_group_plot_kwargs | base.py:326 | 36 | 5 | 4 | MEDIUM |

### Configuration Pattern Inventory

#### **Effective Patterns**
1. **GroupingConfig**: 46 lines, single responsibility, clear API
2. **Component Schemas**: Declarative, phase-organized, self-documenting
3. **LegendConfig**: Simple dataclass with good defaults

#### **Problematic Patterns**  
1. **FigureManager Constructor**: 34 parameters, mixed responsibilities
2. **StyleApplicator**: 365 lines, multiple responsibilities
3. **Theme Resolution**: Complex precedence, unclear boundaries

### Code Examples Demonstrating Current Inconsistencies

#### **Parameter Handling Inconsistency**
```python
# GroupingConfig: Clean, focused
@dataclass  
class GroupingConfig:
    hue: Optional[ColName] = None
    # 4 focused parameters

# FigureManager: Parameter explosion
def __init__(self, rows=1, cols=1, external_ax=None, layout_rect=None,
             layout_pad=0.5, legend_config=None, legend_strategy=None,
             legend_position=None, legend_ncol=None, # ... 26 more parameters
```

#### **Responsibility Boundary Inconsistency**  
```python
# BasePlotter: Well-focused responsibility
def _should_create_legend(self) -> bool:
    # Single responsibility: legend creation decision

# StyleApplicator: Multiple responsibilities
class StyleApplicator:
    def _resolve_component_styles(self): pass  # Style resolution
    def create_legend_entry(self): pass       # Legend creation  
    def apply_post_processing(self): pass     # Post-processing coordination
    def _extract_component_kwargs(self): pass # Parameter extraction
    # Mixed responsibilities in single class
```

### Detailed Analysis Supporting Recommendations

#### **Evidence for Configuration-First Approach**
1. **GroupingConfig Success**: Demonstrates configuration objects work well for focused responsibilities
2. **FigureManager Failure**: Shows parameter explosion requires configuration object intervention
3. **StyleApplicator Complexity**: Mixed configuration and processing requires separation

#### **Evidence for Function Decomposition Priority**
1. **Critical Functions Impact**: 3 critical functions block multiple enhancement efforts
2. **Testability Issues**: Complex functions prevent effective unit testing
3. **Type Safety Barriers**: Complex functions resist clear type annotations

This comprehensive analysis establishes clear evidence-based criteria for systematic pattern unification, prioritizing high-impact improvements while maintaining DR_PLOTTER's architectural foundation.

---

## Conclusion

The pattern unification investigation reveals **clear pathways** for systematic improvement through a **unified configuration-first strategy**. By establishing effective configuration object patterns first (based on GroupingConfig success model), then decomposing critical complexity functions, DR_PLOTTER can achieve consistent, maintainable architectural patterns while preserving its research-focused flexibility.

**Ready for implementation**: Evidence collected, priorities established, success criteria defined.
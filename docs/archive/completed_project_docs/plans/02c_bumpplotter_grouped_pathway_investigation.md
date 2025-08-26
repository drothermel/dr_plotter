# Agent Task: BumpPlotter Grouped Pathway Investigation and Cleanup

## Task Overview
Investigate whether BumpPlotter is incorrectly using grouped drawing pathways for data preparation that should be moved to `_plot_specific_data_prep()`, establishing it as a single-purpose visualization.

## Problem Context
**Design Philosophy**: BumpPlotter represents a single trajectory visualization showing ranking changes over time - conceptually a single-purpose plot that shouldn't support grouped drawing.

**Suspected Issue**: BumpPlotter may be relying on grouped drawing code pathways for data preparation (ranking calculation, category handling) rather than performing this work in the appropriate `_plot_specific_data_prep()` method.

## Investigation Requirements

### 1. Current BumpPlotter Architecture Analysis
**Files to Examine**:
- `src/dr_plotter/plotters/bump.py` - Complete implementation analysis
- `src/dr_plotter/plotters/base.py` - Base `_render_with_grouped_method()` and `_draw_grouped()` logic

**Key Questions**:
1. **Data Preparation Location**: Where does ranking calculation (`rank = data.groupby(time_col)[value_col].rank()`) happen?
2. **Category Processing**: How are categories (hue groups) processed - in grouped pathways or bump-specific logic?
3. **Rendering Flow**: Does BumpPlotter rely on `_render_with_grouped_method()` for essential functionality?

### 2. Grouped Pathway Usage Analysis
**Specific Investigation Points**:

#### **Check render() Flow**:
```python
# In BasePlotter.render()
if self._has_groups:
    self._render_with_grouped_method(ax)  # Does BumpPlotter need this?
else:
    self._draw(ax, self.plot_data, **style_kwargs)
```

#### **Check _render_with_grouped_method() Dependency**:
- Does BumpPlotter require the groupby logic in `_render_with_grouped_method()`?
- Is the category processing (lines 220-242 in base.py) essential for BumpPlotter functionality?
- Does BumpPlotter need `group_values` context setup for proper rendering?

#### **Check _draw_grouped() vs _draw() Usage**:
- Does BumpPlotter have any logic that depends on `group_position` parameter?
- Could BumpPlotter work identically through `_draw()` calls?

### 3. Data Preparation Cleanup Analysis
**Current BumpPlotter Data Prep Pattern**:
```python
def _plot_specific_data_prep(self) -> pd.DataFrame:
    self.plot_data["rank"] = self.plot_data.groupby(self.time_col)[
        self.value_col
    ].rank(method="first", ascending=False)
    self.value_col = "rank"
    return self.plot_data
```

**Investigation Questions**:
1. **Sufficient Data Prep**: Is the current `_plot_specific_data_prep()` handling all necessary transformations?
2. **Missing Category Handling**: Should category processing be moved from grouped pathways to data prep?
3. **Ranking Logic**: Is the ranking calculation complete, or does it depend on grouped processing?

### 4. Category Management Analysis
**Current BumpPlotter Category Setup**:
```python
def _initialize_subplot_specific_params(self) -> None:
    # ... other setup ...
    self.grouping_params.hue = self.category_col  # Forces hue grouping
```

**Key Questions**:
1. **Forced Grouping**: Does setting `self.grouping_params.hue = self.category_col` inappropriately force grouped rendering?
2. **Category Processing**: Should categories be handled within BumpPlotter's own logic rather than through base grouping?
3. **Alternative Approach**: Could categories be processed in `_plot_specific_data_prep()` instead?

### 5. Rendering Independence Analysis
**Test Scenario**: Could BumpPlotter work with this simplified flow?
```python
# Hypothetical cleaned-up approach
def _plot_specific_data_prep(self) -> None:
    # Move ALL category and ranking logic here
    # Process categories explicitly without relying on grouped pathways
    # Prepare fully-ready data for simple _draw() calls

def _draw(self, ax, data, **kwargs):
    # Current implementation - should work with cleaned-up data prep
    # Draw all category trajectories without needing grouped coordination
```

## Investigation Methodology

### Step 1: Current Behavior Analysis
1. **Trace execution flow**: Follow BumpPlotter rendering through BasePlotter.render()
2. **Identify dependencies**: What grouped pathway features does BumpPlotter actually use?
3. **Data flow analysis**: Where does category processing actually happen?

### Step 2: Dependency Assessment
1. **Essential vs Incidental**: Which grouped pathway usage is necessary vs convenient?
2. **Data preparation gaps**: What would need to move to `_plot_specific_data_prep()`?
3. **Behavioral preservation**: How to maintain identical output with different architecture?

### Step 3: Cleanup Strategy Design
1. **Data preparation enhancement**: Design complete data prep that eliminates grouped dependency
2. **Category handling**: Move category processing from grouped pathways to bump-specific logic
3. **Rendering simplification**: Enable simple `_draw()` calls without grouped coordination

## Expected Output Format

```markdown
# BumpPlotter Grouped Pathway Investigation

## Current Architecture Analysis
- **Grouped Pathway Dependencies**: [List what BumpPlotter actually uses from grouped rendering]
- **Data Preparation Completeness**: [Assessment of current _plot_specific_data_prep() scope]
- **Category Processing Location**: [Where categories are currently handled]

## Problematic Dependencies Identified
### Dependency 1: [Specific grouped pathway usage]
- **Location**: [File:line references]
- **Current Behavior**: [What it does]
- **Problem**: [Why this should be in data prep instead]
- **Impact**: [Effect on rendering flow]

### Dependency 2: [Additional dependencies if found]
[Same format as Dependency 1]

## Cleanup Strategy Recommendation
### Approach: [Recommended cleanup approach]
- **Data Preparation Changes**: [Specific changes to _plot_specific_data_prep()]
- **Category Handling Changes**: [How to move category processing]
- **Rendering Simplification**: [How to enable simple _draw() usage]

### Implementation Steps:
1. [Step 1 with specific code changes]
2. [Step 2 with specific code changes]
3. [Step 3 with specific code changes]

## Risk Assessment
- **Behavioral Changes**: [Potential impact on output]
- **Breaking Changes**: [Impact on existing usage]
- **Testing Requirements**: [What needs validation]

## Integration with supports_grouped Flag
- **Flag Value**: BumpPlotter.supports_grouped = False
- **Justification**: [Why BumpPlotter is single-purpose]
- **Enhanced _draw_grouped()**: [How base class should handle no-grouped plotters]
```

## Success Criteria
- ✅ Clear identification of BumpPlotter's actual grouped pathway dependencies
- ✅ Specific cleanup strategy that moves inappropriate data prep from grouped pathways  
- ✅ Design that enables BumpPlotter to work as single-purpose visualization
- ✅ Preservation of all current functionality with cleaner architecture
- ✅ Integration plan with `supports_grouped = False` flag system

## Context
This investigation enables Decision 2 resolution by establishing BumpPlotter as a proper single-purpose visualization, completing the categorization of plotters into coordinate-sharing vs positioned-layout vs single-purpose types.

## Key Constraints
- **Zero breaking changes**: Existing BumpPlotter functionality must be preserved exactly
- **Architectural clarity**: Clear separation between data preparation and rendering coordination
- **Pattern consistency**: Align with Decision 1's explicit capability declaration approach
- **DR methodology**: Fail-fast, clear patterns, explicit behavior over hidden dependencies
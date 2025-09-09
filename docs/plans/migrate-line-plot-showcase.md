# Line Plot Showcase Migration & CLI Framework Testing

## Strategic Context

You are migrating the first plot type showcase as part of the dr_plotter CLI modernization initiative. This migration serves dual purposes: creating a modern line plot demonstration and **stress-testing the Click CLI framework** to inform improvements for subsequent migrations.

## Your Mission

**Migrate `examples/11_line_showcase.py` → `scripts/plot_line.py`** while preserving visual quality and adding comprehensive CLI parameter exploration capabilities.

## Required Reading

**FIRST**: Read `docs/processes/tactical_execution_guide.md` to understand your role as tactical executor.

**THEN**: Examine the existing `examples/11_line_showcase.py` to understand the visual parameters and styling that work well.

**ALSO**: Review `src/dr_plotter/scripting/cli_framework.py` to understand the Click framework components available.

## Strategic Objective

Create a **CLI-driven line plot showcase** that demonstrates the full range of line plotting capabilities while serving as a real-world test of our Click framework's effectiveness and identifying areas for improvement.

## Implementation Requirements

### 1. Data Generation Modernization

**Replace existing data generation** with new consolidated generators:

**From**: `ExampleData.time_series_grouped()` and related patterns
**To**: `experimental_data(pattern_type="time_series", ...)` with parameters that produce equivalent visual output

**Critical Requirements**:
- **Preserve visual characteristics**: Line plots must look as good or better
- **Maintain data scaling**: Appropriate y-axis ranges and trend visibility
- **Keep line density**: Sufficient data points for smooth line rendering
- **Consistent grouping**: Same number of series and categorical dimensions

**Test multiple pattern types** to showcase line plot versatility:
```python
# Time series with trends
time_data = experimental_data(pattern_type="time_series", groups=4, time_points=40, seed=301)

# ML training curves  
ml_data = experimental_data(pattern_type="ml_training", time_points=50, seed=302)

# A/B test results
ab_data = experimental_data(pattern_type="ab_test", experiments=2, conditions=2, time_points=30, seed=303)
```

### 2. Comprehensive CLI Integration

**Apply the full Click framework** using `dimensional_plotting_cli` decorator:

```python
from dr_plotter.scripting import dimensional_plotting_cli, CLIConfig, build_faceting_config, build_plot_config

@click.command()
@click.option('--data-type', 
    type=click.Choice(['time_series', 'ml_training', 'ab_test']),
    default='time_series',
    help="Type of line data to generate"
)
@click.option('--groups', type=int, default=4, help="Number of line groups")
@click.option('--time-points', type=int, default=40, help="Number of time points")
@dimensional_plotting_cli([])  # Test framework with line plot showcase
def main(data_type: str, groups: int, time_points: int, **kwargs):
```

**Parameter Exploration Goals**:
- **Data generation**: Control number of groups, time points, pattern type
- **Visual encoding**: Test --hue-by, --style-by, --alpha-by combinations  
- **Layout**: Experiment with --subplot-width, --subplot-height
- **Styling**: Try different --legend-strategy options
- **Output**: Test --save-dir, --pause functionality

### 3. Visual Quality Preservation

**Maintain the visual excellence** from the existing example:

**Layout Parameters**: Preserve figsize, subplot arrangements, and spacing that make lines readable
**Color Coordination**: Ensure consistent colors across subplots for same data series
**Styling Options**: Demonstrate line width, transparency, markers, and style patterns
**Legend Management**: Test different legend positioning and strategies

**Before/After Validation**:
1. Run original `examples/11_line_showcase.py` - capture visual reference
2. Run new `scripts/plot_line.py` with default parameters - compare output
3. Ensure visual quality is preserved or improved

### 4. CLI Framework Stress Testing

**Your critical secondary mission**: Evaluate the Click framework's effectiveness through real usage.

**Test These Framework Components**:

**Parameter Mapping**:
- Do CLI options naturally map to line plot variations?
- Are parameter names intuitive for users exploring line plots?
- What line-specific options are missing from the current framework?

**Config Integration**:
- Create a sample `line_presets.yaml` with different preset configurations
- Test that YAML config + CLI override works smoothly
- Identify any config patterns that would simplify line plot setup

**Validation & Errors**:
- What happens when users provide invalid parameter combinations?
- Are error messages helpful for line plot context?
- What validations would be valuable but are missing?

**User Experience**:
- What CLI commands would actually be useful for exploring line plots?
- Which parameter combinations create meaningful visual differences?
- How intuitive is the CLI for someone learning line plotting?

### 5. Framework Evaluation & Reporting

**Document your findings** on CLI framework effectiveness:

**What Works Well**:
- Which aspects of the Click framework are smooth and intuitive?
- What parameter combinations work naturally for line plots?
- Where does the abstraction feel appropriate?

**Areas for Improvement**:
- Missing CLI options that would be valuable for line plots
- Awkward parameter combinations or naming
- Integration pain points between CLI args and plotting functions
- Repetitive patterns that suggest better abstractions

**Recommended Enhancements**:
- Specific improvements to make showcase CLI patterns better
- New parameters that should be added to the framework
- Config patterns that would simplify setup for other plot types

## Implementation Pattern

### Phase 1: Basic Migration
1. **Copy visual parameters** from existing line showcase that work well
2. **Replace data generation** with `experimental_data()` calls that produce equivalent output
3. **Apply Click framework** with basic parameter set
4. **Validate visual output** matches or improves on original

### Phase 2: CLI Enhancement  
1. **Add line-specific parameters** (data patterns, styling options)
2. **Create preset configurations** for common line plot variations
3. **Test parameter combinations** to find meaningful exploration patterns
4. **Refine help text and validation** based on actual usage

### Phase 3: Framework Evaluation
1. **Document CLI usage patterns** that work well for line plots
2. **Identify framework limitations** encountered during implementation
3. **Recommend specific improvements** for subsequent plot type migrations
4. **Create reusable patterns** that other showcases can follow

## Success Criteria

### Functional Excellence
- **Visual quality preserved**: Line plots look as good or better than original
- **CLI integration complete**: Full parameter exploration capabilities
- **Framework testing thorough**: Real-world evaluation of Click components

### Framework Validation
- **Usage patterns documented**: What works well for line plot CLI exploration
- **Limitations identified**: Where current framework falls short
- **Improvements recommended**: Specific enhancements for better user experience

### Migration Pattern Established  
- **Reusable approach**: Other plot types can follow this pattern
- **Quality standards**: Visual preservation + CLI enhancement method
- **Evaluation framework**: How to assess framework effectiveness through usage

## Expected Deliverables

### 1. Migrated Line Plot Showcase (`scripts/plot_line.py`)
- **Comprehensive CLI integration** using dimensional_plotting_cli
- **Multiple data pattern support** (time_series, ml_training, ab_test)
- **Full parameter exploration** of line plot styling and layout options
- **Visual quality preserved** from original showcase

### 2. CLI Framework Evaluation Report
- **What works well**: Smooth aspects of current framework
- **Pain points identified**: Where framework needs improvement  
- **Usage patterns**: Effective CLI commands for line plot exploration
- **Recommendations**: Specific improvements for subsequent migrations

### 3. Preset Configuration Examples
- **YAML configs** demonstrating different line plot preset modes
- **Parameter combinations** that create meaningful visual variations
- **Documentation** of how presets simplify common use cases

## Strategic Impact

This migration establishes the foundation for all subsequent plot type migrations by:

- **Testing CLI framework** under real-world usage conditions
- **Creating reusable patterns** for CLI-driven plot exploration
- **Identifying improvements** needed for optimal user experience
- **Demonstrating** how consolidated data generators enhance CLI integration

Your findings will directly inform the CLI framework refinements that make subsequent migrations more effective and user-friendly.

## Implementation Notes

**Visual Quality Priority**: If CLI integration conflicts with visual quality, preserve visual quality and document the conflict for framework improvement.

**Real Usage Focus**: Test the CLI as an actual user would - what commands make sense? What parameters are actually useful?

**Framework Feedback**: Your evaluation is crucial for improving the CLI system - be thorough in documenting both successes and limitations.

**Pattern Documentation**: Create clear patterns that subsequent plot type migrations can follow while adapting for their specific needs.
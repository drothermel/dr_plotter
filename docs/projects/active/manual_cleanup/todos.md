# Manual Cleanup TODOs

## Small Additional Todos
- what is plotter_params used for if component schema seems to take its place?
- FacetingConfig rows -> rows_key cols -> cols_key lines -> lines_key
- It might make more sense for targetting to be functional not facet-config bound
- How many of the functions in BasePlotter are actually used?

## Digging Into Plotters Specifically
- Base
  - A bunch of the grouping functions have unused params which makes me think that they probably either aren't cleaned up or they aren't working correctly
  - _resolve_group_plot_kwargs calls self.style_engine._get_continuous_style directly which is a private member access that we almost certainly don't want.
- Scatter
  - Also calling _get_continuous_style which is private member function
  - More concerning: _create_channel_specific_proxy recieves the channel but doesn't use it??
- Bump Plot
  - for some reason we're setting ax._bump_configured directly if the ax doesn't have this attr but this seems like the wrong choice?  it also makes a lint for pirvate member accessed.  Did we add this or is this actually a matplotlib thing??
  - the _draw function takes data but then uses self.trajectory_data instead which creates a lint but is probably correct so whats the best way to handle this.
  - the category styling calls self.theme.get('base_colors') directly which shouldn't happen.  and the linestyle is hardcoded with a manual style = {} definition which is then accessed instead of a call to self.styler.get_style()
- Heatmap
  - _style_ticks gets passed styles but then doesn't use them

## Style Applicator & General Styling
- PositioningCalculator has a _calculate_figure_legend_position() that takes manual_overrides BUT THEN DOESNT USE THEM!!!
- Generally, PositioningCalculator isn't really fully implemented
- so many hardcoded things and confusing ensted ifs
- removed hint modifiers from positioning calculator because they weren't implemented and so lets just not do that.

## Figure Manager
- Still needs alot of manual stepthrough

## Theme-to-Matplotlib Parameter Flow Issue - COMPLETED ✅
*See `done__configuration_system_and_parameter_flow.md` for full details*

## Defensive Checks Hiding Parameter Flow Issues

### Problem Discovered
**Safety Checks Masking Bugs**: Found multiple instances where defensive checks were hiding real parameter flow and configuration issues instead of surfacing them for proper fixes.

### Specific Examples from Violin Plotter

**1. Legend-Gated Styling (Original Issue)**:
```python
# HIDING BUG: All styling skipped when no legend needed
if not self._should_create_legend():
    return  # Skipped all visual styling!
```
**Problem**: Visual styling was incorrectly coupled to legend creation, causing violin plots to lose all post-processing when `legend=False`.

**2. Missing Parts Defensive Checks**:
```python
# HIDING BUG: Theme values not reaching matplotlib  
if self.styler.get_style("showmeans") and "cmeans" in parts:
    stats_parts.append(parts["cmeans"])
```
**Problem**: Added `and "cmeans" in parts` check instead of investigating why `showmeans=True` theme setting wasn't creating `cmeans` in matplotlib output.

**3. Component Existence Checks**:
```python
# HIDING BUG: Expected components missing without explanation
for part_name in ("cbars", "cmins", "cmaxes", "cmeans"):
    if part_name in parts:  # Should these ever be missing?
        stats_parts.append(parts[part_name])
```
**Problem**: Defensive checks made it unclear which components should always exist vs. which are truly conditional.

### Root Cause Analysis

**Why Defensive Checks Hide Issues**:
1. **Mask configuration problems**: Parameter flow issues go undetected
2. **Unclear expectations**: Hard to distinguish between "always expected" vs "conditionally expected" components
3. **Silent failures**: Components get skipped without indicating why
4. **Debugging difficulty**: Real issues are buried under layers of defensive logic

**The Theme-Parameter Disconnect**:
The root cause of missing `cmeans` wasn't insufficient defensive checks - it was that `showmeans=True` in the theme never reached matplotlib's `violinplot()` function due to architectural gaps in parameter flow.

### Solution: Fail-Fast with Clear Expectations

**Replaced defensive checks with explicit expectations**:

**Before (hiding bugs)**:
```python
if not self._should_create_legend():
    return  # Skip all styling silently
    
if "cmeans" in parts:
    # Maybe handle cmeans, maybe not
```

**After (surfacing issues)**:
```python
# Styling always happens (separate from legend concern)
artists = self._collect_artists_to_style(parts)
self.styler.apply_post_processing("violin", artists)

# Clear expectation: if showmeans=True, cmeans MUST exist
if self.styler.get_style("showmeans"):
    stats_parts.append(parts["cmeans"])  # KeyError if missing = bug to fix
```

**Benefits of Fail-Fast Approach**:
- **Immediate feedback**: Bugs surface exactly where/when they occur
- **Clear expectations**: Code documents what should always vs. conditionally exist
- **Proper fixes**: Forces investigation of root causes instead of workarounds
- **Self-documenting**: Reading the code reveals expected matplotlib behavior

### Generalization Strategy

**Look for these anti-patterns across plotters**:

**1. Optional Component Handling**:
```python
# ANTI-PATTERN: Unclear when parts should exist
if "some_part" in parts:
    do_something(parts["some_part"])

# BETTER: Explicit about expectations  
if self.styler.get_style("should_show_part"):
    do_something(parts["some_part"])  # Assert it exists when expected
```

**2. Existence Checks on Required Components**:
```python
# ANTI-PATTERN: Required components treated as optional
if "bodies" in parts and parts["bodies"]:
    create_legend_proxy(parts["bodies"])

# BETTER: Assert required components exist
assert "bodies" in parts, "Required violin bodies missing"
create_legend_proxy(parts["bodies"])
```

**3. Error Fallbacks for Configuration Issues**:
```python
# ANTI-PATTERN: Hide parameter flow problems
try:
    color = extract_complex_color(artist)
except SomeError:
    color = fallback_color  # Hides real issue

# BETTER: Let configuration problems surface
color = extract_simple_color(artist)  # Fails clearly if misconfigured
```

### Investigation Approach
1. **Search for existence checks** on components that should always be present
2. **Identify conditional vs. required components** based on matplotlib API expectations  
3. **Replace defensive checks** with explicit parameter-based conditionals
4. **Add clear assertions** for truly required components
5. **Test that parameter flow works** end-to-end from theme → matplotlib → component existence

**The goal**: Code that clearly expresses expectations and fails fast when those expectations are violated, leading to proper architectural fixes rather than defensive workarounds.

## Parameter Filtering Investigation

### Problem Discovered
**Question about `_filtered_plot_kwargs` filtering logic**: During ScatterPlotter cleanup, discovered that `_filtered_plot_kwargs` removes parameters based on several filter key sets:

```python
filter_keys = set(
    DR_PLOTTER_STYLE_KEYS + 
    self.grouping_params.channel_strs + 
    BASE_PLOTTER_PARAMS + 
    self.__class__.plotter_params
)
```

**Concerns**:
- **Over-filtering**: Are valid matplotlib parameters being incorrectly filtered out?
- **Under-filtering**: Are invalid parameters making it through to matplotlib?
- **Inconsistent filtering**: Do different plotters filter different parameter sets?
- **Filter maintenance**: How do we ensure filter keys stay in sync with matplotlib API changes?

**Investigation Needed**:
1. **Audit each filter key set** to understand what parameters they remove and why
2. **Check matplotlib compatibility** - are we filtering parameters that matplotlib would accept?
3. **Verify plotter-specific filtering** - do `plotter_params` make sense for each plotter type?
4. **Test edge cases** - what happens when users pass valid matplotlib parameters that get filtered?

**Potential Issues**:
- Parameters like `s="invalid"` (non-numeric size) pass through filtering but break during use
- Valid matplotlib parameters might be getting filtered out unnecessarily
- Filter logic might be defensive programming hiding parameter flow problems

**Next Steps**:
- Map each filter category to actual parameter names for each plotter
- Test boundary cases where filtering might be too aggressive or too permissive
- Consider if filtering should happen at `_build_plot_args()` level instead

## Upfront Parameter Validation - REJECTED ✅
*See `done__configuration_system_and_parameter_flow.md` for full details*

## Final Configuration System Design - FULLY IMPLEMENTED ✅
*See `done__configuration_system_and_parameter_flow.md` for full details*
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

## Theme-to-Matplotlib Parameter Flow Issue

### Problem Discovered
**Root Issue**: Theme values for matplotlib-specific parameters were not being passed to matplotlib plotting functions, causing a disconnect between theme configuration and actual plot behavior.

**Specific Example**: 
- `VIOLIN_THEME` sets `showmeans=True` 
- `ViolinPlotter._collect_artists_to_style()` expected `cmeans` to exist in matplotlib's return dictionary
- But matplotlib's `violinplot()` never received `showmeans=True`, so it used default `showmeans=False`
- Result: `KeyError: 'cmeans'` when trying to style non-existent parts

**Architecture Gap**: 
- `_filtered_plot_kwargs` only includes user-provided kwargs, not theme values
- Theme values live in the styler system but never reach matplotlib
- Each plotter likely has this same bug for their matplotlib-specific parameters

### Solution Implemented

**1. Created `BasePlotter._build_plot_args()` method** (lines 223-233 in base.py):
```python
def _build_plot_args(self) -> Dict[str, Any]:
    main_plot_params = self.component_schema.get("plot", {}).get("main", set())
    plot_args = {}
    for key in main_plot_params:
        if key in self._filtered_plot_kwargs:
            plot_args[key] = self._filtered_plot_kwargs[key]  # User precedence
        else:
            style = self.styler.get_style(key)
            if style is not None:
                plot_args[key] = style  # Theme fallback
    return plot_args
```

**Key Design Principles**:
- Uses existing `component_schema["plot"]["main"]` to define matplotlib parameters
- Proper precedence: user kwargs > theme values > matplotlib defaults
- Generic solution that works for all plotters automatically

**2. Handled Parameter Conflicts in ViolinPlotter** (lines 170-175):
- Manual positioning parameters (`positions`, `widths`) can conflict with theme values
- Solution: Use theme/user values when available, fall back to calculated values
- Warn users when their settings override calculated positioning

### Generalization Needed

**Other plotters likely have the same issue** and should be updated to use `_build_plot_args()`:

**High Priority**:
- `ScatterPlotter`: Likely affected by `s`, `alpha`, `color`, `marker` theme values
- `BarPlotter`: Likely affected by `color`, `alpha`, `edgecolor`, `linewidth` theme values  
- `HistogramPlotter`: Likely affected by similar styling parameters

**Medium Priority**:
- `ContourPlotter`: Has complex parameter schema with `levels`, `cmap` parameters
- `HeatmapPlotter`: May have similar theme-to-matplotlib gaps
- `LinePlotter`, `BumpPlotter`: Simpler schemas but still worth checking

**Pattern to Apply**:
1. Replace `**self._filtered_plot_kwargs` with `**self._build_plot_args()` in matplotlib calls
2. Handle any manual parameter conflicts (like positioning) with explicit precedence logic
3. Test that theme values now reach matplotlib correctly

**Investigation Approach**:
- Check each plotter's `component_schema["plot"]["main"]` parameters
- Verify if any matplotlib calls use `_filtered_plot_kwargs` 
- Test that theme defaults for those parameters actually affect plot behavior

### Testing Strategy

**Verification Method**:
```python
# Before fix
plotter._filtered_plot_kwargs  # Empty or missing theme values
# After fix  
plotter._build_plot_args()     # Should include theme values
```

**Visual Test**: Create plots with theme defaults vs. explicit user overrides to verify precedence works correctly.

## Artist Property Extraction Utilities

### Problem Discovered
**Duplicate Logic**: Found that `ViolinPlotter._create_proxy_artist_from_bodies()` and `plot_data_extractor.extract_colors()` were doing very similar matplotlib artist property extraction, but with different approaches:

**Violin Plotter Approach** (original, 39 lines):
- Complex nested conditionals for color extraction
- Error fallbacks to `get_error_color()` that hide bugs
- Manual array/color handling with defensive programming
- Duplicated logic for facecolor and edgecolor extraction

**Plot Data Extractor Approach** (cleaner):
- Uses `mcolors.to_rgba()` for consistent conversion
- Clear assertions that fail fast when expectations violated
- Systematic handling of matplotlib artist types
- Much more concise and maintainable

### Solution Implemented

**1. Created `src/dr_plotter/artist_utils.py`** with atomic extraction functions:
```python
def extract_facecolor_from_polycollection(obj: PolyCollection) -> RGBA
def extract_edgecolor_from_polycollection(obj: PolyCollection) -> RGBA  
def extract_alpha_from_artist(obj) -> float
def extract_single_color_from_polycollection_list(bodies: List[PolyCollection]) -> RGBA
# ... etc
```

**Key Design Principles**:
- **Atomic responsibilities**: Each function does one specific extraction
- **Fail fast**: Use assertions instead of error fallbacks
- **Consistent conversion**: Always use `mcolors.to_rgba()` for color handling
- **Clear naming**: Function names explicitly describe what they extract and from what

**2. Updated existing code to use shared utilities**:
- **ViolinPlotter**: `_create_proxy_artist_from_bodies()` reduced from 39 to 8 lines
- **plot_data_extractor**: `extract_colors()` now uses shared `extract_colors_from_polycollection()`

### Generalization Opportunities

**Other plotters likely have similar extraction needs for legend creation**:

**Scatter Plotter**: Probably extracts colors/sizes from `PathCollection` for legend proxies
**Bar Plotter**: Likely extracts colors from `BarContainer.patches` for legend entries
**Line Plotter**: May extract line colors/styles for legend representation
**Histogram Plotter**: Could benefit from patch color extraction

**Common Patterns to Look For**:
- Manual `get_facecolor()`, `get_edgecolor()`, `get_alpha()` calls
- Complex color array handling and conversion logic
- Defensive fallbacks that hide matplotlib API issues
- Duplicated extraction logic across multiple plotters

**Expansion Strategy**:
1. **Add more artist types** to `artist_utils.py` as needed (PathCollection, BarContainer, Line2D)
2. **Create type-specific functions** like `extract_color_from_pathcollection()`, `extract_color_from_barcontainer()`
3. **Update plotters incrementally** as legend creation code is encountered
4. **Maintain consistency** with fail-fast assertions and `mcolors.to_rgba()` usage

### Success Criteria
- [ ] All plotters use `_build_plot_args()` instead of `_filtered_plot_kwargs`
- [ ] Theme values for matplotlib parameters reach matplotlib correctly
- [ ] User kwargs still take precedence over theme values
- [ ] Manual positioning/grouping logic handles conflicts gracefully
- [ ] No defensive checks hiding real parameter flow bugs
- [ ] Artist property extraction uses shared utilities from `artist_utils.py`
- [ ] Legend creation code is simplified and consistent across plotters
- [ ] All matplotlib color extraction uses `mcolors.to_rgba()` for consistency

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

### Success Criteria
- [ ] All plotters use `_build_plot_args()` instead of `_filtered_plot_kwargs`
- [ ] Theme values for matplotlib parameters reach matplotlib correctly
- [ ] User kwargs still take precedence over theme values
- [ ] Manual positioning/grouping logic handles conflicts gracefully
- [ ] No defensive checks hiding real parameter flow bugs
- [ ] Artist property extraction uses shared utilities from `artist_utils.py`
- [ ] Legend creation code is simplified and consistent across plotters
- [ ] All matplotlib color extraction uses `mcolors.to_rgba()` for consistency
- [ ] Component existence checks are explicit about expectations vs. defensive
- [ ] Failed assertions lead to investigation of root configuration issues
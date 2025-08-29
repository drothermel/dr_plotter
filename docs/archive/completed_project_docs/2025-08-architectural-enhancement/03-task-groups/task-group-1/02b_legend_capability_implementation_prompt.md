# Agent Task: Legend Capability Flag System and Registration Method Implementation

## Task Overview
Implement the `supports_legend` flag system and extract the `_register_legend_entry_if_valid()` method to establish explicit legend capability declarations while maintaining zero breaking changes.

## Implementation Requirements

### 1. Add Legend Capability Flag System
**File**: `src/dr_plotter/plotters/base.py`

**Changes Required**:
```python
# Add class attribute to BasePlotter
class BasePlotter:
    supports_legend: bool = True  # Default: plotters support legends
    
    # Enhanced _should_create_legend() method
    def _should_create_legend(self) -> bool:
        if not self.supports_legend:
            return False
        legend_param = self._get_style("legend")
        if legend_param is False:
            return False
        return True
```

**Validation**: Existing `_should_create_legend()` logic must be preserved - only add capability check at the beginning.

### 2. Override Flag in No-Legend Plotters
**Files**: `src/dr_plotter/plotters/contour.py`, `src/dr_plotter/plotters/heatmap.py`

**Changes Required**:
```python
# ContourPlotter class
class ContourPlotter(BasePlotter):
    supports_legend: bool = False  # Explicit no-legend declaration
    # ... existing class content unchanged ...

# HeatmapPlotter class  
class HeatmapPlotter(BasePlotter):
    supports_legend: bool = False  # Explicit no-legend declaration
    # ... existing class content unchanged ...
```

**Critical**: No other changes to these classes - they should continue not implementing `_apply_post_processing()`.

### 3. Extract Legend Registration Method
**File**: `src/dr_plotter/plotters/base.py`

**Method to Add**:
```python
def _register_legend_entry_if_valid(self, artist: Any, label: Optional[str]) -> None:
    if not self._should_create_legend():
        return
    if self.figure_manager and label and artist:
        entry = self.style_applicator.create_legend_entry(artist, label, self.current_axis)
        if entry:
            self.figure_manager.register_legend_entry(entry)
```

**Integration Requirements**: This method should handle the complete legend registration flow that's currently duplicated across plotters.

### 4. Update Existing Plotters to Use Extracted Method
**Files to Modify**: 
- `src/dr_plotter/plotters/violin.py`
- `src/dr_plotter/plotters/bar.py`
- `src/dr_plotter/plotters/scatter.py`
- `src/dr_plotter/plotters/histogram.py`
- `src/dr_plotter/plotters/line.py`
- `src/dr_plotter/plotters/bump.py`

**Pattern to Replace**:
```python
# BEFORE (existing pattern in each plotter):
if self.figure_manager and label and [artist]:
    entry = self.style_applicator.create_legend_entry([artist], label, self.current_axis)
    if entry:
        self.figure_manager.register_legend_entry(entry)

# AFTER (unified pattern):
self._register_legend_entry_if_valid([artist], label)
```

**Specific Transformations**:

#### ViolinPlotter (`_apply_post_processing`):
```python
# Replace existing registration logic
if label and "bodies" in parts and parts["bodies"]:
    proxy = self._create_proxy_artist_from_bodies(parts["bodies"])
    self._register_legend_entry_if_valid(proxy, label)
```

#### BarPlotter (`_apply_post_processing`):
```python
# Replace existing registration logic  
if patches:
    first_patch = patches[0]
    proxy = Patch(
        facecolor=first_patch.get_facecolor(),
        edgecolor=first_patch.get_edgecolor(),
        alpha=first_patch.get_alpha(),
    )
    self._register_legend_entry_if_valid(proxy, label)
```

#### ScatterPlotter (`_apply_post_processing`):
```python
# Replace existing registration logic in loop
for channel in self.grouping_params.active_channels_ordered:
    proxy = self._create_channel_specific_proxy(collection, channel)
    if proxy:
        # Note: ScatterPlotter may need special handling due to explicit_channel
        entry = self.style_applicator.create_legend_entry(
            proxy, label, self.current_axis, explicit_channel=channel
        )
        if entry:
            self.figure_manager.register_legend_entry(entry)
```

#### HistogramPlotter (`_apply_post_processing`):
```python
# Replace existing registration logic
if "patches" in parts and parts["patches"]:
    first_patch = parts["patches"][0]
    proxy = Patch(
        facecolor=first_patch.get_facecolor(),
        edgecolor=first_patch.get_edgecolor(),
        alpha=first_patch.get_alpha(),
    )
    self._register_legend_entry_if_valid(proxy, label)
```

#### LinePlotter (`_apply_post_processing`):
```python
# Replace existing registration logic in loop
line = lines[0] if isinstance(lines, list) else lines
for channel in self.grouping_params.active_channels_ordered:
    # Note: LinePlotter may need special handling due to explicit_channel
    entry = self.style_applicator.create_legend_entry(
        line, label, self.current_axis, explicit_channel=channel
    )
    if entry:
        self.figure_manager.register_legend_entry(entry)
```

#### BumpPlotter (`_apply_post_processing`):
```python
# Replace existing registration logic
line = lines[0] if isinstance(lines, list) else lines
entry = self.style_applicator.create_legend_entry(line, label, self.current_axis)
if entry:
    self.figure_manager.register_legend_entry(entry)
# Replace with:
line = lines[0] if isinstance(lines, list) else lines
self._register_legend_entry_if_valid(line, label)
```

## Implementation Steps

### Step 1: Add Flag System to Base Class
1. Add `supports_legend: bool = True` to BasePlotter class
2. Enhance `_should_create_legend()` method with capability check
3. Add `_register_legend_entry_if_valid()` method with complete registration logic

### Step 2: Declare No-Legend Plotters
1. Add `supports_legend: bool = False` to ContourPlotter class
2. Add `supports_legend: bool = False` to HeatmapPlotter class
3. Verify no other changes needed to these classes

### Step 3: Update Legend-Capable Plotters
1. **ScatterPlotter and LinePlotter**: Handle explicit_channel parameter carefully - may not fit standard extracted method
2. **ViolinPlotter, BarPlotter, HistogramPlotter, BumpPlotter**: Direct replacement with extracted method
3. **Preserve all existing logic**: Only replace registration calls, keep all proxy creation and validation logic

### Step 4: Comprehensive Testing
1. **Functionality test**: All existing legend-capable plotters work identically
2. **No-legend test**: ContourPlotter and HeatmapPlotter continue working without legends
3. **User override test**: `legend=False` parameter still works for all plotters
4. **Import test**: All plotter files import successfully

## Special Handling Requirements

### ScatterPlotter and LinePlotter Complexity
**Issue**: These plotters use `explicit_channel` parameter in `create_legend_entry()`
**Options**:
- **Option A**: Modify extracted method to accept optional explicit_channel parameter
- **Option B**: Keep these plotters' registration logic as-is, only update the simpler plotters
- **Option C**: Create specialized registration method for multi-channel plotters

**Recommendation**: Start with Option B (keep complex plotters as-is) to maintain zero breaking changes, address in future optimization.

### Validation Requirements
**Must verify**:
- All existing tests pass without modification
- Legend behavior identical for all currently legend-capable plotters
- ContourPlotter and HeatmapPlotter continue not showing legends
- User `legend=False` override continues working
- No import errors in any plotter file

## Success Criteria
- ✅ `supports_legend: bool` flag system implemented in BasePlotter
- ✅ ContourPlotter and HeatmapPlotter explicitly marked as no-legend
- ✅ `_register_legend_entry_if_valid()` method extracted and functional
- ✅ 4+ legend-capable plotters updated to use extracted method (ViolinPlotter, BarPlotter, HistogramPlotter, BumpPlotter minimum)
- ✅ Zero breaking changes - all existing functionality preserved
- ✅ Complex plotters (ScatterPlotter, LinePlotter) handled appropriately
- ✅ Comprehensive testing validates no behavioral changes

## Context
This implements Decision 1 resolution for Phase 2 Task Group 1, establishing explicit legend capability architecture that enables systematic legend integration while clearly marking no-op plotters.

## Expected Outcome
- Clear architectural separation between legend-capable and no-legend plotters
- Reduced code duplication through extracted registration method
- Foundation established for Decision 2 (_draw_grouped) using same explicit capability pattern
- Zero user-visible changes while improving internal architecture consistency
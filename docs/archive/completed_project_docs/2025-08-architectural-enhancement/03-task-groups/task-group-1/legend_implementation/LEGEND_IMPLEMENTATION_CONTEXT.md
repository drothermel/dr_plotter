# Legend Implementation Context - Memory Compaction Reference

## 🎯 Immediate Next Steps

You are implementing the Legend Management System as described in `/docs/plans/legend_management_implementation.md`. 

### Current Task: Implement Phase 1 & 2, then migrate HistogramPlotter

## 📍 Where We Are

1. **Completed**:
   - Designed hybrid legend management system (theme defaults + smart auto + manual builder)
   - Created comprehensive implementation plan
   - Researched approaches from matplotlib, seaborn, plotly, altair, ggplot2

2. **Current Work**:
   - Implement Phase 1: Core data structures (LegendEntry, LegendRegistry, LegendConfig)
   - Implement Phase 2: Integration hooks (FigureManager, StyleApplicator enhancements)
   - Migrate HistogramPlotter as proof of concept

## 🔨 Implementation Steps

### Step 1: Create Core Classes
Location: `/src/dr_plotter/legend_manager.py` (new file)

```python
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

@dataclass
class LegendEntry:
    artist: Any
    label: str
    visual_channel: Optional[str] = None
    channel_value: Any = None
    group_key: Dict[str, Any] = None
    plotter_type: str = 'unknown'
    artist_type: str = 'main'

class LegendRegistry:
    def __init__(self):
        self._entries: List[LegendEntry] = []
        self._seen_labels: Set[str] = set()
    
    def add_entry(self, entry: LegendEntry) -> None:
        # Deduplication logic here
        if entry.label not in self._seen_labels:
            self._entries.append(entry)
            self._seen_labels.add(entry.label)
    
    # Other methods...

@dataclass
class LegendConfig:
    mode: str = 'auto'
    collect_strategy: str = 'smart'
    position: str = 'best'
    deduplication: bool = True
    ncol: Optional[int] = None
    spacing: float = 0.1
    remove_axes_legends: bool = True
```

### Step 2: Add to Theme
Location: `/src/dr_plotter/theme.py`

Add legend_config parameter to Theme.__init__ and store it as attribute.

### Step 3: Enhance FigureManager
Location: `/src/dr_plotter/figure.py`

```python
from dr_plotter.legend_manager import LegendManager, LegendConfig

class FigureManager:
    def __init__(self, ..., legend_config: Optional[LegendConfig] = None):
        # Add legend management
        self.legend_config = legend_config or LegendConfig()
        self.legend_manager = LegendManager(self, self.legend_config)
    
    def register_legend_entry(self, entry: LegendEntry) -> None:
        self.legend_manager.registry.add_entry(entry)
    
    def finalize_legends(self) -> None:
        self.legend_manager.finalize()
```

### Step 4: Update StyleApplicator
Location: `/src/dr_plotter/style_applicator.py`

Add method to create legend entries with metadata:

```python
def create_legend_entry(self, artist: Any, label: str, 
                        artist_type: str = 'main') -> Optional[LegendEntry]:
    if not label:
        return None
    
    # Determine active visual channel from grouping config
    channel = None
    if self.grouping_cfg and self.grouping_cfg.active_channels:
        # Get first active channel (usually only one)
        channel = list(self.grouping_cfg.active_channels.keys())[0]
    
    channel_value = self.group_values.get(channel) if channel else None
    
    from dr_plotter.legend_manager import LegendEntry
    return LegendEntry(
        artist=artist,
        label=label,
        visual_channel=channel,
        channel_value=channel_value,
        group_key=self.group_values.copy(),
        plotter_type=self.plot_type,  # Need to add plot_type to __init__
        artist_type=artist_type
    )
```

### Step 5: Update BasePlotter
Location: `/src/dr_plotter/plotters/base.py`

Add `use_legend_manager = False` class attribute.
Update render() to pass figure_manager to Legend constructor.

### Step 6: Migrate HistogramPlotter
Location: `/src/dr_plotter/plotters/histogram.py`

```python
class HistogramPlotter(BasePlotter):
    use_style_applicator: bool = True
    use_legend_manager: bool = True  # Enable new system
    
    def _apply_post_processing(self, parts: Dict[str, Any], legend: Legend, 
                              label: str = None) -> None:
        if self.use_style_applicator:
            self.style_applicator.apply_post_processing("histogram", parts)
        
        # Register legend entry if using new system
        if self.use_legend_manager and self.figure_manager and label and "patches" in parts:
            # Create proxy artist from first patch
            if parts["patches"]:
                first_patch = parts["patches"][0]
                from matplotlib.patches import Patch
                proxy = Patch(
                    facecolor=first_patch.get_facecolor(),
                    edgecolor=first_patch.get_edgecolor(),
                    alpha=first_patch.get_alpha()
                )
                
                # Create entry with metadata
                entry = self.style_applicator.create_legend_entry(proxy, label)
                if entry:
                    self.figure_manager.register_legend_entry(entry)
        elif label:
            # Old system fallback
            legend.add_patch(label=label, ...)
```

## 🧪 Test Plan

Create test file: `/test_histogram_legend.py`

```python
# Test 1: Basic histogram with legend
# Test 2: Multi-subplot histogram with figure legend
# Test 3: Grouped histogram with channel-based legend
# Test 4: Backward compatibility with use_legend_manager=False
```

## 📝 Key Context

### Integration with Phased Styling
- Legend management happens AFTER post-processing phase
- Artists have their final properties when legend entries are created
- StyleApplicator provides metadata (visual channel, group values)

### Backward Compatibility Critical
- Existing Legend class becomes a facade
- use_legend_manager flag allows gradual migration
- Old plotters continue working unchanged

### Design Rationale
- **Hybrid approach**: Combines automatic (Plotly-like) with manual control (ggplot2-like)
- **Theme integration**: Legend config lives with other styling decisions
- **Figure-level coordination**: FigureManager is natural place for multi-subplot legends
- **Metadata tracking**: Each entry knows its visual channel for intelligent grouping

## ⚠️ Important Notes

1. **Don't break existing code** - All changes must be backward compatible
2. **Test incrementally** - Get HistogramPlotter working before moving to others
3. **StyleApplicator integration** - Legend entries created during post-processing
4. **FigureManager may be None** - Handle case where plotter used standalone

## 🎯 Success Criteria for HistogramPlotter Migration

1. ✅ Histogram with use_legend_manager=True creates legend entries
2. ✅ Multi-subplot histograms get unified figure legend
3. ✅ Old behavior preserved when use_legend_manager=False
4. ✅ Legend entries have correct metadata (channel, group_key, etc.)
5. ✅ No errors when figure_manager is None
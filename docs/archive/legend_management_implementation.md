# Legend Management System Implementation Plan

## Overview
A hybrid legend management system that combines automatic smart defaults with optional manual control, integrating seamlessly with the phased styling system.

## Architecture

### Core Components

```python
# Component relationships
FigureManager
    ├── LegendManager (new)
    │   ├── LegendConfig (from Theme or override)
    │   ├── LegendRegistry (tracks all entries)
    │   └── LegendBuilder (optional manual control)
    └── Axes Management (existing)

BasePlotter
    ├── StyleApplicator
    │   └── Registers with LegendRegistry during post phase
    └── Legend (deprecated, becomes facade)
```

### Integration with Phased Styling
Legend becomes the fourth phase in the styling lifecycle:
```
PHASES: plot → post → axes → legend
```

## Implementation Phases

### Phase 1: Foundation (Non-Breaking)

#### Core Data Structures

```python
class LegendEntry:
    """Single legend item with metadata."""
    artist: Any  # The matplotlib artist
    label: str
    visual_channel: Optional[str]  # 'hue', 'style', 'size'
    channel_value: Any  # Actual value for this channel
    group_key: Dict[str, Any]  # Full grouping context
    plotter_type: str  # Which plotter created this
    
class LegendRegistry:
    """Collects and deduplicates legend entries."""
    def add_entry(self, entry: LegendEntry) -> None
    def get_unique_entries(self) -> List[LegendEntry]
    def get_by_channel(self, channel: str) -> List[LegendEntry]
    def clear(self) -> None

class LegendConfig:
    """Legend configuration with smart defaults."""
    mode: str = 'auto'  # 'auto', 'manual', 'per_axes', 'none'
    collect_strategy: str = 'smart'  # 'all', 'by_channel', 'none'
    position: str = 'best'  # 'best', 'below', 'right', 'in_empty_facet'
    deduplication: bool = True
    ncol: Optional[int] = None
    spacing: float = 0.1  # For grouped legends
    remove_axes_legends: bool = True  # When using figure legend
```

### Phase 2: Integration Hooks

#### FigureManager Enhancement

```python
class FigureManager:
    def __init__(self, ..., legend_config: Optional[LegendConfig] = None):
        # Use provided config or get from theme
        if legend_config:
            self.legend_config = legend_config
        else:
            # Get from theme if available
            self.legend_config = getattr(theme, 'legend_config', LegendConfig())
        
        self.legend_manager = LegendManager(self, self.legend_config)
    
    def register_legend_entry(self, entry: LegendEntry) -> None:
        """Called by plotters during rendering."""
        self.legend_manager.registry.add_entry(entry)
    
    def finalize_legends(self) -> None:
        """Called after all plotting complete."""
        self.legend_manager.finalize()
```

#### StyleApplicator Legend Support

```python
class StyleApplicator:
    def create_legend_entry(self, artist: Any, label: str, 
                           artist_type: str = 'main') -> Optional[LegendEntry]:
        """Create legend entry with metadata during post-processing."""
        if not label:
            return None
            
        # Extract metadata from current context
        channel = self._get_active_channel()
        channel_value = self.group_values.get(channel) if channel else None
        
        # Create entry with rich metadata
        entry = LegendEntry(
            artist=artist,
            label=label,
            visual_channel=channel,
            channel_value=channel_value,
            group_key=self.group_values.copy(),
            plotter_type=self.plot_type,
            artist_type=artist_type
        )
        
        return entry
```

### Phase 3: Plotter Migration

#### BasePlotter Updates

```python
class BasePlotter:
    # Add new flag alongside use_style_applicator
    use_legend_manager: bool = False  # Opt-in per plotter
    
    def render(self, ax: Any) -> None:
        # Create legend object for backward compatibility
        legend = Legend(self.figure_manager)
        
        # Existing render logic...
        
        if self.use_legend_manager and self.figure_manager:
            # New path: legend entries registered during rendering
            # No need for explicit call here - happens in post-processing
            pass
        else:
            # Old path: use existing Legend class
            self._apply_styling(ax, legend)
```

#### Progressive Migration Example (HistogramPlotter)

```python
class HistogramPlotter(BasePlotter):
    use_style_applicator: bool = True
    use_legend_manager: bool = True  # Enable new system
    
    def _apply_post_processing(self, parts: Dict[str, Any], 
                              legend: Legend, label: str = None) -> None:
        # Existing post-processing
        if self.use_style_applicator:
            self.style_applicator.apply_post_processing("histogram", parts)
        
        # New: Register legend entry
        if self.use_legend_manager and self.figure_manager and label:
            # Create proxy artist from post-processed parts
            proxy = self._create_proxy_artist(parts)
            
            # Create entry through StyleApplicator for metadata
            entry = self.style_applicator.create_legend_entry(proxy, label)
            if entry:
                self.figure_manager.register_legend_entry(entry)
        elif label:
            # Fallback to old system
            legend.add_patch(label=label, ...)
    
    def _create_proxy_artist(self, parts: Dict[str, Any]) -> Any:
        """Create a proxy artist for legend from histogram parts."""
        if "patches" in parts and parts["patches"]:
            # Use first patch as template
            first_patch = parts["patches"][0]
            from matplotlib.patches import Patch
            return Patch(
                facecolor=first_patch.get_facecolor(),
                edgecolor=first_patch.get_edgecolor(),
                alpha=first_patch.get_alpha()
            )
        return None
```

## Rollout Strategy

### Migration Order
1. **HistogramPlotter** - Simplest, already uses StyleApplicator
2. **ScatterPlotter** - Has grouping, tests channel awareness
3. **ViolinPlotter** - Complex multi-component, proves flexibility
4. Other plotters as needed

### Backward Compatibility

```python
class Legend:
    """Backward compatible wrapper around new system."""
    
    def __init__(self, figure_manager: Optional[FigureManager] = None):
        self.handles = []  # For compatibility
        self.fm = figure_manager
        
    def add_patch(self, label: str, **kwargs) -> None:
        # Old API
        from matplotlib.patches import Patch
        patch = Patch(label=label, **kwargs)
        self.handles.append(patch)
        
        # New system integration if available
        if self.fm and hasattr(self.fm, 'legend_manager'):
            entry = LegendEntry(
                artist=patch,
                label=label,
                visual_channel=None,  # Unknown from old API
                channel_value=None,
                group_key={},
                plotter_type='unknown',
                artist_type='patch'
            )
            self.fm.register_legend_entry(entry)
```

## Key Implementation Details

### Smart Default Logic

```python
class LegendManager:
    def _determine_strategy(self) -> str:
        """Smart defaults based on plot structure."""
        if self.config.mode != 'auto':
            return self.config.mode
            
        if self.fm.rows > 1 or self.fm.cols > 1:
            # Multiple subplots → figure legend
            return 'figure_below'
        elif len(self._get_unique_channels()) > 1:
            # Multiple visual channels → grouped legends
            return 'grouped_by_channel'
        else:
            # Simple case → per-axes legend
            return 'per_axes'
```

### Proxy Artist Factory

```python
class ProxyArtistFactory:
    """Centralized proxy artist creation with channel awareness."""
    
    @staticmethod
    def create_for_channel(entry: LegendEntry) -> Artist:
        """Create standardized proxy artist based on visual channel."""
        from matplotlib.lines import Line2D
        from matplotlib.patches import Patch
        
        if entry.visual_channel == 'hue':
            # Solid line with color
            return Line2D([0], [0], 
                         color=entry.artist.get_color(),
                         linewidth=2, linestyle='-',
                         label=entry.label)
        elif entry.visual_channel == 'style':
            # Black line with style  
            return Line2D([0], [0],
                         color='black',
                         linestyle=entry.artist.get_linestyle(),
                         linewidth=2,
                         label=entry.label)
        elif entry.visual_channel == 'size':
            # Variable size markers
            return Line2D([0], [0],
                         marker='o',
                         markersize=entry.channel_value * 2,  # Scale appropriately
                         color='black',
                         linestyle='',
                         label=entry.label)
        else:
            # Default: use the artist as-is
            return entry.artist
```

### Theme Integration

```python
# Add legend_config to Theme
class Theme:
    def __init__(self, ..., legend_config: Optional[LegendConfig] = None):
        self.legend_config = legend_config or LegendConfig()

# Example theme with legend defaults
PUBLICATION_THEME = Theme(
    name="publication",
    legend_config=LegendConfig(
        mode='auto',
        position='below',
        collect_strategy='by_channel',
        ncol=4,
        remove_axes_legends=True
    )
)
```

## Testing Strategy

### Unit Tests
- LegendRegistry deduplication logic
- LegendConfig precedence (theme vs figure)
- ProxyArtistFactory for each visual channel
- LegendEntry metadata extraction

### Integration Tests
- HistogramPlotter with use_legend_manager=True
- Multi-subplot figure legend creation
- Grouped legends by visual channel
- Mixed migrated/unmigrated plotters

### Backward Compatibility Tests
- Old Legend class facade works
- Plotters with use_legend_manager=False unchanged
- Themes without legend_config don't break

## Success Metrics

- ✅ All StyleApplicator plotters support LegendManager
- ✅ Zero breaking changes to existing code
- ✅ Figure-level legends work automatically for multi-subplot
- ✅ Grouped legends by visual channel when multiple channels used
- ✅ Clean migration path with opt-in flag per plotter
- ✅ Theme-based configuration for consistent legend styling

## Future Enhancements

1. **Legend positioning in empty facets** - Detect empty subplot locations
2. **Hierarchical legends** - For complex multi-channel groupings
3. **Interactive legend toggle** - Hide/show data series
4. **Legend export** - Save legend separately for publications
5. **Custom proxy artists** - User-defined legend representations
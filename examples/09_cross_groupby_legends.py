from typing import Any
from dr_plotter.figure import FigureManager
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import verify_example, verify_plot_properties
from plot_data import ExampleData

EXPECTED_CHANNELS = {
    (0, 0): ["hue", "marker"],
    (0, 1): ["hue", "style"],
}

@verify_plot_properties(expected_channels=EXPECTED_CHANNELS)
@verify_example(
    expected_legends=3,
    expected_channels=EXPECTED_CHANNELS,
    expected_legend_entries={
        (0, 0): {"hue": 3, "marker": 3},
        (0, 1): {"hue": 3, "style": 2},
    },
)
def main(args: Any) -> Any:
    complex_data = ExampleData.get_cross_groupby_legends_data()
    
    assert "experiment" in complex_data.columns
    assert "condition" in complex_data.columns
    assert "algorithm" in complex_data.columns
    assert "performance" in complex_data.columns
    assert "accuracy" in complex_data.columns
    assert len(complex_data.groupby("experiment")) == 3
    assert len(complex_data.groupby("condition")) == 2
    assert len(complex_data.groupby("algorithm")) == 3
    
    with FigureManager(rows=1, cols=2, figsize=(16, 6), legend_strategy="split") as fm:
        fm.fig.suptitle("Example 9: Cross Group-By + Legend Types - Split Legend System", fontsize=16)
        
        fm.plot("scatter", 0, 0, complex_data,
            x="performance",               
            y="accuracy",                  
            hue_by="experiment",           
            marker_by="algorithm",         
            s=60,                          
            alpha=0.7,                     
            title="Split: Multi-Channel Encoding (Hue + Marker)"
        )
        
        fm.plot("line", 0, 1, complex_data,
            x="time_point",                
            y="performance",               
            hue_by="experiment",           
            style_by="condition",          
            linewidth=2,                   
            alpha=0.8,                     
            title="Split: Multi-Channel Encoding (Hue + Style)"
        )
        
    show_or_save_plot(fm.fig, args, "09_cross_groupby_legends")
    return fm.fig

if __name__ == "__main__":
    parser = setup_arg_parser(description="Cross Group-By + Legend Types - Multi-Channel Visual Encoding")
    args = parser.parse_args()
    main(args)
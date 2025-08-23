from dr_plotter.figure import FigureManager
from plot_data import ExampleData
import matplotlib.pyplot as plt

# Create the same plot as example 7 first subplot
with FigureManager(rows=1, cols=1, figsize=(8, 6)) as fm:
    simple_grouped = ExampleData.grouped_categories(n_groups=2)

    fm.plot(
        "bar",
        0,
        0,
        simple_grouped,
        x="category",
        y="value",
        hue_by="group",
        title="2-Group Bar Chart",
    )

    # Get the axis and legend
    ax = fm.fig.axes[0]
    legend = ax.get_legend()

    print("=== DEBUG LEGEND INFO ===")
    print(f"Legend exists: {legend is not None}")
    if legend:
        print(f"Legend visible: {legend.get_visible()}")

        # Check different ways to get handles
        print(f"hasattr legendHandles: {hasattr(legend, 'legendHandles')}")

        if hasattr(legend, "legendHandles"):
            handles = legend.legendHandles
            print(f"legend.legendHandles: {handles}")
            print(f"Number of legendHandles: {len(handles) if handles else 0}")

        # Try other methods
        handles_alt = legend.get_lines()
        print(f"legend.get_lines(): {handles_alt}")
        print(f"Number from get_lines: {len(handles_alt) if handles_alt else 0}")

        # Check texts
        texts = legend.get_texts()
        labels = [t.get_text() for t in texts]
        print(f"Legend texts: {texts}")
        print(f"Legend labels: {labels}")
        print(f"Non-empty labels: {[l for l in labels if l.strip()]}")

        # Try get_children
        children = legend.get_children()
        print(f"Legend children: {children}")
        print(f"Number of children: {len(children)}")

        # Try the matplotlib Legend API methods
        legend_elements = legend.legend_handles
        print(f"legend.legend_handles: {legend_elements}")
        print(
            f"Number of legend_handles: {len(legend_elements) if legend_elements else 0}"
        )

        # Save plot for visual inspection
        plt.savefig("../debug_bar_legend.png")
        print("Plot saved to debug_bar_legend.png")

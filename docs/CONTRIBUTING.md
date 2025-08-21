# Contributing to dr_plotter

First off, thank you for considering contributing to `dr_plotter`. This project is a labor of love, and we welcome all contributions, from simple bug fixes to new feature proposals.

To ensure that the library remains clean, consistent, and maintainable, we ask that you adhere to the following guidelines.

## The Declarative Plotter Pattern

The core of `dr_plotter` is the declarative plotter pattern. The goal of this pattern is to make the plotters themselves as simple as possible, with all the complex logic handled by the `BasePlotter`. A plotter is simply a declarative configuration of class attributes and a single `_draw` method.

### Plotter Attributes

Every plotter must declare the following class attributes:

*   `plotter_name`: The official name of the plotter (e.g., `"scatter"`).
*   `plotter_params`: A set of strings defining the plotter-specific parameters (e.g., `{"x", "y", "hue"}`).
*   `param_mapping`: A dictionary that maps the plotter-specific parameters to the standard `BasePlotter` parameters (e.g., `{"time_col": "x"}`).
*   `enabled_channels`: A set of strings defining the visual encoding channels that the plotter supports (e.g., `{"hue", "style"}`).
*   `default_theme`: The default theme for the plotter (e.g., `LINE_THEME`).
*   `data_validator`: The Pydantic model used to validate the plotter's data (e.g., `LinePlotData`).

### The `_draw` Method

The `_draw` method is the heart of the plotter. It is responsible for the actual `matplotlib` drawing commands. It should be as simple as possible and should not contain any logic for data preparation or styling.

For plotters that require special handling for grouped data, you can implement two methods instead of one:

*   `_draw_simple(self, ax, data, legend, **kwargs)`
*   `_draw_grouped(self, ax, data, group_position, legend, **kwargs)`

## The `BasePlotter`

The `BasePlotter` is the engine of the library. It is responsible for:

*   **Orchestrating the plotting lifecycle:** `prepare_data` -> `generate_styles` -> `_draw` -> `apply_styling`.
*   **Handling all the complex logic:** Multi-metric data handling, grouping, styling, etc.

When you are adding a new plotter, you should not need to modify the `BasePlotter`.

## The `Legend` Class

The `Legend` class is a builder for creating custom legend entries. It is passed to the `_draw` method, and it should be used to create legend entries for plotters that require them (e.g., `BarPlotter`, `ViolinPlotter`).

## Getting Started

1.  **Fork the repository** and create a new branch for your feature or bug fix.
2.  **Create a new plotter** by subclassing `BasePlotter` and implementing the declarative pattern.
3.  **Add a new example** to the `examples/` directory that showcases your new plotter.
4.  **Run the validation script** (`examples/validate_coverage.py`) to ensure that your new plotter is covered by the examples.
5.  **Open a pull request** and we will review it as soon as possible.

Thank you for your contribution!

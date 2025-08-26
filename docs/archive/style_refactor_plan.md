# Styling System Refactor Plan

## 1. The Problem: Inconsistent and Opaque Styling

The current styling system in `dr_plotter` is a mix of several different approaches, which leads to a number of issues:

*   **Inconsistent Application:** Styling rules are applied in different ways across different plotters. Some read from the `Theme`, some use `kwargs`, some modify the `Theme` object directly, and some have hardcoded styles.
*   **Lack of Clear Precedence:** It is not always clear how `kwargs` and `Theme` settings interact. This can lead to unexpected behavior where styles are overridden or ignored silently.
*   **Scattered Logic:** The logic for styling is spread across `BasePlotter`, individual plotters, `StyleEngine`, and `Theme` objects. This makes it difficult to understand and maintain the styling system as a whole.
*   **Limited Discoverability:** It is not easy for a user to discover what styling options are available for a given plot.

These issues are in direct conflict with our design principles of an "Intuitive and Consistent API" and "Clarity Through Structure."

## 2. The Solution: A Hybrid Approach

To address these issues, we will adopt a "Hybrid" approach that combines the strengths of a centralized `Theme`-based system with the flexibility of `kwargs`.

This approach is based on a few core ideas:

*   **Clear Precedence:** We will establish a strict and well-documented order of precedence for applying styles.
*   **Centralized Logic:** We will create a new `StyleApplicator` class that will be responsible for resolving and applying all styles.
*   **Explicit Style Consumption:** Plotters will no longer have to guess which `kwargs` are for styling and which are for other purposes. They will explicitly request the styles they need from the `StyleApplicator`.

### Justification

This approach was chosen because it:

*   **Balances Consistency and Flexibility:** It provides a consistent styling experience by default, while still allowing for easy one-off customizations via `kwargs`.
*   **Improves Maintainability:** By centralizing the styling logic, we make it easier to debug, modify, and extend the styling system in the future.
*   **Aligns with Design Principles:** It directly addresses the need for a more intuitive, consistent, and clearly structured API.
*   **Minimizes Disruption:** It is an evolution of the existing system, not a complete rewrite, which will make the transition smoother.

## 3. Implementation Guidance

The implementation will be broken down into the following steps:

1.  **Create the `StyleApplicator` class:**
    *   This class will be initialized with a `Theme` object and a dictionary of `kwargs`.
    *   It will have a method, `get_style_for(component: str) -> dict`, that returns a dictionary of `matplotlib`-compatible `kwargs` for a given plot component (e.g., "line", "axes", "grid").
    *   The `get_style_for` method will implement the precedence rules: `kwargs` > plot-specific theme > base theme.

2.  **Refactor `BasePlotter`:**
    *   The `BasePlotter` will be updated to use the `StyleApplicator`.
    *   The `_filtered_plot_kwargs` property will be removed.
    *   The `_apply_styling` method will be updated to use the `StyleApplicator` to get the styles for the axes, title, grid, and legend.

3.  **Refactor Individual Plotters:**
    *   Each plotter will be updated to use the `StyleApplicator` to get the styles for its specific plot elements.
    *   For example, `LinePlotter` will call `applicator.get_style_for("line")` and pass the result to `ax.plot()`.
    *   Any hardcoded styles or manual `Theme` manipulations will be removed and replaced with settings in the `Theme` objects.

4.  **Refine `Theme` Objects:**
    *   The `Theme` objects will be reviewed and updated to ensure they are well-structured and comprehensive.
    *   We may introduce more specific `Style` objects (e.g., `LineStyle`, `BarStyle`) within the `Theme` to improve organization, but this will be a secondary concern to the main refactoring effort.

## 4. Rollout and Verification

The rollout will be done on a plotter-by-plotter basis to ensure a smooth transition:

1.  **Start with a Single Plotter:** We will start by refactoring a single, simple plotter (e.g., `ScatterPlotter`) to use the new system.
2.  **Update Examples:** The examples for that plotter will be updated to reflect the new styling approach.
3.  **Verify:** We will run the examples and visually inspect the output to ensure that the new system is working as expected.
4.  **Repeat:** We will repeat this process for all other plotters.
5.  **Update Documentation:** Once all plotters have been refactored, we will update the documentation to explain the new styling system to users.

By following this plan, we can create a styling system that is more consistent, predictable, and maintainable, and that better aligns with our design principles.

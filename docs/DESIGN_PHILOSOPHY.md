# Design Philosophy

## Core Mission: Empowering Researchers to Visualize Data with Ease

The library's primary purpose is to accelerate the research process by making it easy to create a wide range of publication-quality plots. The focus should always be on the user's end goal: understanding their data.

## Guiding Principles

*   **Intuitive and Consistent API:** The library should have a "learn once, use everywhere" design. The API should be predictable, well-documented, and free of surprising behavior.
*   **Flexibility and Extensibility:** Researchers should be able to create any plot they need, from simple scatter plots to complex, multi-faceted figures. The library should be designed to be easily extended with custom plotters and styles.
*   **Sensible Defaults, Powerful Customization:** Plots should look great out of the box with minimal configuration. However, every aspect of a plot should be easily customizable for those who need more control.
*   **Robust and Developer-Friendly:** The library should be well-tested, provide clear error messages, and have a clean, maintainable codebase that is easy for new contributors to understand.

## How We Achieve Our Goals: The "DR" Method

To ensure the library lives up to its principles, we adhere to a specific development methodology:

1.  **Clarity Through Structure:**
    *   **Conceptual Mapping:** The codebase should be a direct reflection of our conceptual model. Classes, files, and directories should have clear, descriptive names that make the structure of the library immediately obvious.
    *   **Atomicity:** Every component (function, class, file) should have a single, well-defined purpose. This makes the code easier to understand, test, and refactor.

2.  **Succinct and Self-Documenting Code:**
    *   **No Duplication (DRY):** We strictly follow the "Don't Repeat Yourself" principle. Code duplication is a sign that a new abstraction is needed.
    *   **Minimalism:** We favor concise, compact code and avoid unnecessary comments. The code should speak for itself.

3.  **Pragmatic, Example-Driven Testing:**
    *   **End-to-End Examples:** Our primary testing strategy is a comprehensive suite of examples that demonstrate the library's functionality in a real-world context.
    *   **Targeted Unit Tests:** Unit tests are used sparingly, reserved for core, complex algorithms that are not easily covered by the examples.

4.  **Embrace Change, Demand Consistency:**
    *   **No Backward Compatibility:** This is a research library, and we will always prioritize a streamlined and intuitive design over backward compatibility. We are not afraid to make breaking changes to improve the library.
    *   **Leave No Trace:** When a change is made, all legacy code must be removed, and all affected parts of the library must be updated. The codebase should always be in a clean, consistent state.
    *   **Fail Fast, Fail Loudly:** We favor a coding style that surfaces errors immediately. This means using assertions and avoiding overly defensive programming (e.g., broad `try-except` blocks) that can hide bugs.

5.  **Focus on the Researcher's Workflow:**
    *   **Minimize Friction:** Every design choice should aim to reduce the friction between a researcher's idea and its visualization. If a feature is hard to use or explain, it's a candidate for simplification.
    *   **Clarity Over Cleverness:** We always prefer code that is simple and easy to understand over code that is "clever" but opaque. The goal is to make the library a tool that *disappears* into the background, allowing the researcher to focus on their work.

## Target Audience

Research engineers and scientists who value a high-level, declarative plotting library that doesn't sacrifice the power and flexibility of the underlying `matplotlib` backend.

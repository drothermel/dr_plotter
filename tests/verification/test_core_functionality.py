import sys
import time

sys.path.append("src")

from dr_plotter.scripting.verif_decorators import verify_plot
from data_generators import (
    create_synthetic_faceting_data,
    create_reference_dataset,
    create_single_dimension_data,
    create_plot_type_test_data,
)

from dr_plotter.figure_config import FigureConfig, create_figure_manager
from dr_plotter.faceting_config import FacetingConfig

test_results = []


def record_test_result(test_name: str, status: str, duration: float, details: str = ""):
    test_results.append(
        {"test": test_name, "status": status, "duration": duration, "details": details}
    )
    print(f"\n=== TEST RESULT: {test_name} - {status} ({duration:.2f}s) ===")
    if details:
        print(f"Details: {details}")


@verify_plot(
    expected_legends=0,  # Using figure legend, not subplot legends
    expected_channels={
        (0, 0): ["color"],
        (0, 1): ["color"],
        (0, 2): ["color"],
        (1, 0): ["color"],
        (1, 1): ["color"],
        (1, 2): ["color"],
    },
    verify_legend_consistency=False,
    min_unique_threshold=4,  # 4 models should produce 4 colors
    subplot_descriptions={
        0: "Loss metric across 3 datasets with 4 model colors",
        1: "Accuracy metric across 3 datasets with same 4 model colors",
    },
)
def test_basic_2d_faceting():
    # Create synthetic data: 2 metrics × 3 datasets × 4 models
    data = create_synthetic_faceting_data(
        n_points=100,
        metrics=["loss", "accuracy"],
        datasets=["train", "val", "test"],
        models=["A", "B", "C", "D"],
    )

    config = FacetingConfig(
        rows="metric",  # 2 metrics: loss, accuracy
        cols="dataset",  # 3 datasets: train, val, test
        lines="model",  # 4 models: A, B, C, D
        x="step",
        y="value",
    )

    with create_figure_manager(figure=FigureConfig(rows=2, cols=3)) as fm:
        fm.plot_faceted(data=data, plot_type="line", faceting=config)
        return fm.fig


@verify_plot(
    expected_legends=0,
    expected_channels={(r, 0): ["color"] for r in range(4)},  # 4 rows, 1 col
    min_unique_threshold=3,
)
def test_single_dimension_faceting_rows_only():
    single_dim_data = create_single_dimension_data()
    data = single_dim_data["rows_only"]

    config = FacetingConfig(rows="metric", lines="model", x="step", y="value")

    with create_figure_manager(figure=FigureConfig(rows=4, cols=1)) as fm:
        fm.plot_faceted(data=data, plot_type="line", faceting=config)
        return fm.fig


@verify_plot(
    expected_legends=0,
    expected_channels={(0, c): ["color"] for c in range(3)},  # 1 row, 3 cols
    min_unique_threshold=3,
)
def test_single_dimension_faceting_cols_only():
    single_dim_data = create_single_dimension_data()
    data = single_dim_data["cols_only"]

    config = FacetingConfig(cols="dataset", lines="model", x="step", y="value")

    with create_figure_manager(figure=FigureConfig(rows=1, cols=3)) as fm:
        fm.plot_faceted(data=data, plot_type="line", faceting=config)
        return fm.fig


def test_all_plot_types_integration():
    plot_data = create_plot_type_test_data()
    plot_types = ["line", "scatter", "bar"]  # Start with these core types

    results = []
    for plot_type in plot_types:
        print(f"\n=== Testing plot type: {plot_type} ===")

        data = plot_data[plot_type]

        if plot_type == "line":
            config = FacetingConfig(
                rows="metric", cols="dataset", lines="model", x="step", y="value"
            )
        elif plot_type == "scatter":
            config = FacetingConfig(
                rows="metric", cols="dataset", lines="model", x="x_pos", y="y_pos"
            )
        elif plot_type == "bar":
            config = FacetingConfig(
                rows="category", cols="group", lines="type", x="item", y="count"
            )

        try:
            with create_figure_manager(figure=FigureConfig(rows=2, cols=2)) as fm:
                fm.plot_faceted(data=data, plot_type=plot_type, faceting=config)
                fig = fm.fig

            # Basic verification - each plot type should create proper grid
            axes_count = len([ax for ax in fig.axes if ax.get_visible()])
            assert axes_count >= 4, (
                f"Expected at least 4 subplots for {plot_type}, got {axes_count}"
            )

            results.append(f"{plot_type}: SUCCESS")
            print(f"✓ {plot_type} faceting successful - {axes_count} subplots created")

        except Exception as e:
            results.append(f"{plot_type}: FAILED - {str(e)}")
            print(f"✗ {plot_type} faceting failed: {e}")

    return results


@verify_plot(
    expected_legends=0,
    expected_channels={(r, c): ["color"] for r in range(2) for c in range(3)},
    tolerance=0.0,  # Exact color matching required
    verify_legend_consistency=True,
)
def test_color_consistency_regression():
    # Use identical data to what would be used in reference
    data = create_reference_dataset()
    config = FacetingConfig(
        rows="metric", cols="dataset", lines="model", x="step", y="value"
    )

    with create_figure_manager(figure=FigureConfig(rows=2, cols=3)) as fm:
        fm.plot_faceted(data=data, plot_type="line", faceting=config)
        fig = fm.fig

    # Extract and verify color consistency across subplots
    line_colors = []
    for ax in fig.axes:
        if ax.lines:
            ax_colors = [line.get_color() for line in ax.lines]
            line_colors.append(ax_colors)

    if line_colors:
        # Check that same model gets same color across all subplots
        num_models = len(line_colors[0]) if line_colors else 0
        for model_idx in range(num_models):
            model_colors = [
                subplot_colors[model_idx]
                for subplot_colors in line_colors
                if len(subplot_colors) > model_idx
            ]
            unique_colors = set(model_colors)
            assert len(unique_colors) == 1, (
                f"Model {model_idx} has inconsistent colors: {unique_colors}"
            )

    return fig


def execute_priority_1_tests():
    print("=== PHASE 4B: PRIORITY 1 CORE FUNCTIONALITY TESTS ===\n")

    tests = [
        ("Basic 2D Faceting", test_basic_2d_faceting),
        (
            "Single Dimension Faceting - Rows Only",
            test_single_dimension_faceting_rows_only,
        ),
        (
            "Single Dimension Faceting - Cols Only",
            test_single_dimension_faceting_cols_only,
        ),
        ("All Plot Types Integration", test_all_plot_types_integration),
        ("Color Consistency Regression", test_color_consistency_regression),
    ]

    for test_name, test_func in tests:
        print(f"\n{'=' * 60}")
        print(f"EXECUTING TEST: {test_name}")
        print("=" * 60)

        start_time = time.time()
        try:
            result = test_func()
            duration = time.time() - start_time

            if test_name == "All Plot Types Integration":
                # Special handling for multi-result test
                if all("SUCCESS" in r for r in result):
                    record_test_result(
                        test_name,
                        "PASSED",
                        duration,
                        f"All plot types: {', '.join(result)}",
                    )
                else:
                    failures = [r for r in result if "FAILED" in r]
                    record_test_result(
                        test_name,
                        "FAILED",
                        duration,
                        f"Failures: {', '.join(failures)}",
                    )
            else:
                record_test_result(
                    test_name,
                    "PASSED",
                    duration,
                    "Verification decorator confirmed success",
                )

        except AssertionError as e:
            duration = time.time() - start_time
            record_test_result(
                test_name, "FAILED", duration, f"Assertion failed: {str(e)}"
            )
            print(f"❌ TEST FAILED: {test_name}")
            print(f"❌ ERROR: {str(e)}")
            print("❌ STOPPING - Fix this test before proceeding")
            break
        except Exception as e:
            duration = time.time() - start_time
            record_test_result(
                test_name, "ERROR", duration, f"Unexpected error: {str(e)}"
            )
            print(f"💥 UNEXPECTED ERROR in {test_name}: {str(e)}")
            print("💥 STOPPING - Debug and fix before proceeding")
            break

    print(f"\n{'=' * 60}")
    print("PRIORITY 1 TEST EXECUTION SUMMARY")
    print("=" * 60)

    passed = len([r for r in test_results if r["status"] == "PASSED"])
    failed = len([r for r in test_results if r["status"] in ["FAILED", "ERROR"]])
    total = len(test_results)

    print(f"Tests Passed: {passed}/{total}")
    print(f"Tests Failed: {failed}/{total}")
    print(f"Success Rate: {(passed / total) * 100:.1f}%")

    if failed == 0:
        print("✅ ALL PRIORITY 1 TESTS PASSED - Ready for Priority 2")
    else:
        print("❌ PRIORITY 1 TESTS INCOMPLETE - Must fix failures before proceeding")

    for result in test_results:
        status_emoji = (
            "✅"
            if result["status"] == "PASSED"
            else "❌"
            if result["status"] == "FAILED"
            else "💥"
        )
        print(
            f"{status_emoji} {result['test']}: {result['status']} ({result['duration']:.2f}s)"
        )
        if result["details"]:
            print(f"    {result['details']}")


if __name__ == "__main__":
    execute_priority_1_tests()

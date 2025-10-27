from bokeh.plotting import figure
from bokeh.io import output_file, show
from bokeh.models import HoverTool, ColumnDataSource
import pandas


def visualize_motion_intervals(motion_intervals_df) -> None:
    """
    Plot motion intervals.

    Args:
        motion_intervals_df (pandas.DataFrame): DataFrame containing motion intervals.
        Note: This function expects the path to a CSV file.
    """

    # Read CSV file into a pandas DataFrame
    motion_intervals_df = pandas.read_csv(motion_intervals_df)
    motion_intervals_df["Start"] = pandas.to_datetime(
        motion_intervals_df["Start"], format="mixed"
    )
    motion_intervals_df["End"] = pandas.to_datetime(
        motion_intervals_df["End"], format="mixed"
    )

    # Create a ColumnDataSource from the DataFrame for easier integration with Bokeh plots
    column_data_source = ColumnDataSource(motion_intervals_df)

    # Initialize a new Bokeh figure with datetime x-axis and defined dimensions
    motion_intervals_plot = figure(
        title="Motion Intervals",
        x_axis_label="Time",
        y_axis_label="Motion",
        x_axis_type="datetime",
        width=1200,
        height=400,
    )

    # Customize the y-axis appearance:
    # Remove minor tick lines for a cleaner look
    motion_intervals_plot.yaxis.minor_tick_line_color = None
    # Set the desired number of ticks on the y-axis to one (since we're representing a binary state)
    motion_intervals_plot.yaxis[0].ticker.desired_num_ticks = 1

    # Configure a HoverTool to display detailed Start and End times when hovering over the plot elements
    hover = HoverTool(
        tooltips=[("Start", "@Start{%F %T}"), ("End", "@End{%F %T}")],
        formatters={"@Start": "datetime", "@End": "datetime"},
    )

    motion_intervals_plot.add_tools(hover)

    # Plot the motion intervals as green rectangles
    motion_intervals_plot.quad(
        left="Start",
        right="End",
        top=1,
        bottom=0,
        color="green",
        source=column_data_source,
    )

    output_file("motion_intervals.html")

    show(motion_intervals_plot)

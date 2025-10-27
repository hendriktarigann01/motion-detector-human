import pandas


def compute_motion_intervals(timestamp_list) -> pandas.DataFrame:
    """
    Compute motion intervals from the timestamp list.

    Args:
        timestamp_list (list): List of timestamps.

    Returns:
        pandas.DataFrame: DataFrame containing motion intervals.
    """

    motion_intervals_df = pandas.DataFrame(columns=["Start", "End"])

    for i in range(0, len(timestamp_list), 2):
        try:
            motion_start_time = timestamp_list[i]
            motion_end_time = timestamp_list[i + 1]
            motion_intervals_df = motion_intervals_df.append(
                {"Start": motion_start_time, "End": motion_end_time}, ignore_index=True
            )
        except IndexError:
            pass

    return motion_intervals_df

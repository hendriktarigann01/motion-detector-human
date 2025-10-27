from datetime import datetime


def handle_state_change(status_list, timestamp_list, detection_status):
    """
    handle state change between 'motion detected' and 'no motion'.
    Saves the time when the state change occurs.

    Args:
        status_list (list): list of states (0 or 1).
        timestamp_list (list): list of times when the state change occurs.
        detection_status (int): current state (0 or 1).

    Returns:
        tuple: updated status_list and times.
    """
    if len(status_list) > 1:
        if detection_status == 1 and status_list[-2] == 0:
            timestamp_list.append(datetime.now())
        elif detection_status == 0 and status_list[-2] == 1:
            timestamp_list.append(datetime.now())

    status_list.append(detection_status)

    if len(status_list) > 2:
        status_list = status_list[-2:]

    return status_list, timestamp_list

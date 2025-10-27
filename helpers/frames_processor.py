import cv2


def process_frame(video_frame, initial_frame, min_contour_area=1000):
    """
    Process a video frame for motion detection.

    Args:
        video_frame (numpy.ndarray): The current frame from the video feed.
        initial_frame (numpy.ndarray, optional): The initial frame for comparison. Defaults to None.
        min_contour_area (int, optional): Minimum area for contours to be considered motion. Defaults to 1000.

    Returns:
        tuple: Processed frame, updated initial frame, motion status (1 if motion detected, 0 otherwise).
    """
    motion_detected_flag = 0

    # convert frame to grayscale
    processed_frame = cv2.cvtColor(video_frame, cv2.COLOR_BGR2GRAY)
    # apply Gaussian blur to reduce noise
    processed_frame = cv2.GaussianBlur(processed_frame, (21, 21), 0)

    if initial_frame is None:
        initial_frame = processed_frame
        return video_frame, processed_frame, motion_detected_flag

    # compute the absolute difference between the current frame and the first frame
    delta_frame = cv2.absdiff(initial_frame, processed_frame)
    # apply threshold to get binary image
    thresh_frame = cv2.threshold(delta_frame, 30, 255, cv2.THRESH_BINARY)[1]
    # dilate the threshold frame to fill in holes
    dilated_threshold_image = cv2.dilate(thresh_frame, None, iterations=2)

    # find contours in the threshold frame
    detected_contours, _ = cv2.findContours(
        dilated_threshold_image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    for contour in detected_contours:
        if cv2.contourArea(contour) < min_contour_area:
            continue
        motion_detected_flag = 1  # motion detected

        # draw bounding box around the motion
        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(video_frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

    return video_frame, initial_frame, motion_detected_flag

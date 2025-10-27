import time


class FPSCounter:
    """
    Class to calculate the frames per second (FPS) of a video stream.
    """

    def __init__(self, smoothing_interval=5):
        """Initialize the FPS calculator.

        Args:
            smoothing_interval (int, optional): The interval over which to smooth the FPS calculation. Defaults to 5.

        Attributes:
            _start_time: The time at which the FPS calculation started.
            _frame_count: The number of frames processed since the start time.
            _fps: The calculated FPS value.
            _smoothing_interval: The interval over which to smooth the FPS calculation.
        """

        self._start_time = time.time()
        self._frame_count = 0
        self._fps = 0
        self._smoothing_interval = smoothing_interval

    def update_frame_rate(self):
        """
        Update the frame count and calculate the FPS value.
        """
        self._frame_count += 1
        current_time = time.time()
        elapsed_time = current_time - self._start_time

        # Calculate FPS over the smoothing interval without resetting the frame count
        if elapsed_time >= self._smoothing_interval:
            self._fps = self._frame_count / elapsed_time
            self._start_time = current_time
            self._frame_count = 0

    def get_fps(self):
        """Get the calculated FPS value, averaged over the smoothing interval.

        Returns:
            float: The calculated FPS value.
        """
        return self._fps

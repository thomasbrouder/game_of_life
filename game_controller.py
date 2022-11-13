import time


class Controller:
    def __init__(self, matrix, interval):
        self._matrix = matrix
        self._interval = interval
        self._is_running = False
        self._cursor_coords = None

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, value):
        self._interval = value

    @property
    def cursor_coords(self):
        return self._cursor_coords

    @cursor_coords.setter
    def cursor_coords(self, value):
        self._cursor_coords = value

    @property
    def is_running(self):
        return self._is_running

    @is_running.setter
    def is_running(self, value):
        self._is_running = value

    @property
    def cells(self):
        return self._matrix.cells

    @property
    def shape(self):
        return self._matrix.nb_rows, self._matrix.nb_cols

    def run(self):
        while True:
            self.step_run()
            time.sleep(self._interval)

    def step_run(self):
        if self._is_running:
            self._matrix.update()

        elif self._cursor_coords is not None:
            x, y = self._cursor_coords
            self._matrix.change_cell(y, x)
            self._cursor_coords = None

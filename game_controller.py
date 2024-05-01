import time
import logging

logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel("INFO")

class Controller:
    def __init__(self, matrix, interval):
        """Controller of the matrix of cells.

        Args:
            matrix (matrix.Matrix): matrix of cells.
            interval (int): time between two generations.

        """
        self._matrix = matrix
        self._interval = interval
        self._is_running = False
        self._selected_cell = None

    @property
    def interval(self):
        """int: time between two generations."""
        return self._interval

    @interval.setter
    def interval(self, value):
        """int: time between two generations."""
        self._interval = value

    @property
    def selected_cell(self):
        """tuple[int]: cursor coordinates in the cells' matrix."""
        return self._selected_cell

    @selected_cell.setter
    def selected_cell(self, value):
        """tuple[int]: cursor coordinates in the cells' matrix."""
        self._selected_cell = value

    @property
    def is_running(self):
        """bool: whether the game is running."""
        return self._is_running

    @is_running.setter
    def is_running(self, value):
        """bool: whether the game is running."""
        self._is_running = value

    @property
    def cells(self):
        """np.ndarray: Matrix of cells of shape (m, n)."""
        return self._matrix.cells

    @property
    def shape(self):
        """tuple(int): Matrix of cells numbers of rows and columns."""
        return self._matrix.nb_rows, self._matrix.nb_cols

    def run(self):
        """Runs the game."""
        while True:
            self.step_run()

    def step_run(self):
        """Atomic step of the game.
        If the game is running, then the matrix of cells is updated to the next generations.
        If the game is stopped and a cell is selected, then this cell's state is changed.
        """
        if self._is_running:
            start_time = time.time()
            self._matrix.update()
            end_time = time.time()

            if self._matrix.iteration % 10 == 0:
                logger.info("Iterations: %s", self._matrix.iteration)

        elif self._selected_cell is not None:
            x, y = self._selected_cell
            self._matrix.change_cell(y, x)
            self._selected_cell = None

    def save_matrix(self):
        timestamp = time.time()
        name = str(timestamp)
        self._matrix.save(name + ".npy")
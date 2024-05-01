import numpy as np
import pathlib
from io import StringIO


data_folder = "./data/"


def load_pattern(filename):
    with open(filename, "r") as file_handler:
        lines = file_handler.readlines()
    formatted_data = "\n".join(
        [' '.join(['1' if c == 'O' else '0' for c in line])
         for line in lines]
    )
    data_stream = StringIO(formatted_data)
    return np.loadtxt(data_stream, dtype="i", delimiter=None)


class Matrix:
    """Matrix of cells.

    Args:
        params (list[int]): Parameters of the game.
        nb_rows (int): Number of rows. It is also the number of cells per column.
        nb_cols (int): Number of columns. It is also the number of cells per row.
        init_live_pct (float): percentage of live cells in the initial state.

    Notes:
        The parameters of the game are the number of live neighbors that a given cell must have
        in order to be alive at the next generation. These values depend on the current state of the considered cell.
        They are ordered as such [min_alive, max_alive, min_dead, max_dead] where:
        - min_alive and max_alive are the limits of living neighbors that a live cell must have in order to stay alive.
        - min_dead and max_dead are the limits of living neighbors that a dead cell must have in order to come to life.

    """
    def __init__(self, params, nb_rows, nb_cols, init_live_pct):
        self.nb_rows = nb_rows
        self.nb_cols = nb_cols
        if init_live_pct < 0 or 1 < init_live_pct:
            raise ValueError("initial_percentage should be between 0 and 1.")
        self.cells = np.random.choice(
            a=[False, True],
            size=(nb_rows, nb_cols),
            p=[1 - init_live_pct, init_live_pct]
        )
        self.iteration = 0
        self._params = params

    @classmethod
    def from_filename(cls, params, nb_rows, nb_cols, filename):
        matrix = cls(params, nb_rows, nb_cols, 0)
        path = pathlib.Path(data_folder) / filename
        with open(path, "rb") as file_handler:
            matrix.cells = np.load(file_handler)
        return matrix

    def add_pattern(self, pattern, pos):
        # TODO Handle case out of bounds
        x_origin, y_origin = pos
        width, height = pattern.shape
        self.cells[x_origin: x_origin + width, y_origin: y_origin + height] = pattern

    def change_cell(self, x, y):
        """Change cell state. It becomes dead if it was alive and the other way around.

        Args:
            x (int): cell row id.
            y (int): cell column id.q

        """
        self.cells[x][y] = not self.cells[x][y]

    def update(self):
        """Updates the cells' matrix according to Conway's Game of Life laws.

        Notes:
             The laws are the following:
                1. Any live cell with the right number of live neighbours (usually between two and three) survives.
                2. Any dead cell with the right number of live neighbours (usually three) becomes a live cell.
                3. Any other live cell dies in the next generation. Similarly, any other dead cell stays dead.
        """
        nb_live_neighbors = self._nb_alive_neighbors()
        being_born = ~self.cells & (self._params[2] <= nb_live_neighbors) & (nb_live_neighbors <= self._params[3])
        staying_alive = self.cells & (self._params[0] <= nb_live_neighbors) & (nb_live_neighbors <= self._params[1])
        self.cells = being_born | staying_alive
        self.iteration += 1

    def _nb_alive_neighbors(self):
        """Returns the matrix of size (nb_rows, nb_cols) giving the sum of alive neighbors.

        Raises:
            ValueError: Function internal value error. Values contained in rows_cols_to_add should be either 0, -1 or 1.

        Returns:
            np.ndarray: Matrix of size (nb_rows, nb_cols) giving the sum of alive neighbors.
        """
        new_col = np.zeros(self.nb_rows)
        new_row = np.zeros(self.nb_cols)
        rows_cols_to_add = [
            {"top": 1, "left": 0},
            {"top": -1, "left": 0},
            {"top": 0, "left": 1},
            {"top": 0, "left": -1},
            {"top": 1, "left": 1},
            {"top": -1, "left": -1},
            {"top": 1, "left": -1},
            {"top": -1, "left": 1},
        ]

        neighbors = np.tile(0, (self.nb_rows, self.nb_cols))

        for data in rows_cols_to_add:
            copy_cells = self.cells.copy()
            start_time = time.time()

            if data["top"] == 1:
                copy_cells = np.insert(copy_cells, 0, new_row, axis=0)[:-1, :]
            elif data["top"] == -1:
                copy_cells = np.insert(copy_cells, self.nb_rows, new_row, axis=0)[1:, :]
            elif data["top"] == 0:
                pass
            else:
                raise ValueError("Number of rows to add on top must be contained between -1 and 1.")

            if data["left"] == 1:
                copy_cells = np.insert(copy_cells, 0, new_col, axis=1)[:, :-1]
            elif data["left"] == -1:
                copy_cells = np.insert(copy_cells, self.nb_cols, new_col, axis=1)[:, 1:]
            elif data["left"] == 0:
                pass
            else:
                raise ValueError("Number of columns to add to the left must be contained between -1 and 1.")
            end_time = time.time()
            elapsed_time = end_time - start_time
            logger.info("elapsed_time: %s", elapsed_time)
            neighbors = neighbors + copy_cells

        return neighbors

    def save(self, filename):
        path = pathlib.Path(data_folder)
        if not path.exists():
            path.mkdir()
        path = path / filename
        with open(path, "wb") as file_handler:
            np.save(file_handler, self.cells)


if __name__ == '__main__':
    import time
    import logging

    logging.basicConfig(format='%(asctime)s %(message)s')
    logger = logging.getLogger(__name__)
    logger.setLevel("INFO")

    min_frequency = 10
    dimensions = [(8000 + 100*i, 8000+100*i) for i in range(90)]
    for nb_rows, nb_cols in dimensions:
        matrix = Matrix(
            params=[2, 3, 3, 3],
            nb_rows=nb_rows,
            nb_cols=nb_cols,
            init_live_pct=0.15
        )
        start_time = time.time()
        count = 0
        while count < 10:
            matrix.update()
            count += 1

        elapsed_time = time.time() - start_time
        mean_frequency = round(count / elapsed_time, 3)
        logger.info(
            "Mean frequency for dimensions %s: %s Hz",
            (nb_rows, nb_cols),
            mean_frequency,
        )
        if mean_frequency < min_frequency:
            break

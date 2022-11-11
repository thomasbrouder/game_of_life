"""
    Conway's game of life
    Rules
    1. Any live cell with two or three live neighbours survives.
    2. Any dead cell with three live neighbours becomes a live cell.
    3. All other live cells die in the next generation. Similarly, all other dead cells stay dead.
"""

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation


class Matrix:
    def __init__(self, game_params, nb_rows, nb_cols, white_percentage):
        self.nb_rows = nb_rows
        self.nb_cols = nb_cols
        self._white_percentage = white_percentage
        self.matrix = np.random.choice(
            a=[False, True],
            size=(nb_rows * nb_cols),
            p=[white_percentage, 1 - white_percentage]
        )
        self._game_params = game_params

    def update_matrix(self):
        new_matrix = np.tile(False, self.nb_rows * self.nb_cols)
        for idx in range(self.matrix.size):
            i, j = divmod(idx, self.nb_cols)
            indices = [(a, b) for a in range(i - 1, i + 2) for b in range(j - 1, j + 2)]
            indices = [a * self.nb_cols + b for (a, b) in indices if 0 <= a < self.nb_cols and 0 <= b < self.nb_rows]
            indices = set(indices) - set([i * self.nb_cols + j])
            alive_neighbors = sum([self.matrix[j] for j in indices])

            if self.matrix[idx]:
                alive_next_gen = self._game_params[0] <= alive_neighbors <= self._game_params[1]
            else:
                alive_next_gen = self._game_params[2] <= alive_neighbors <= self._game_params[3]
            new_matrix[idx] = alive_next_gen
        self.matrix = new_matrix


matrix = Matrix(
    game_params=[2, 3, 3, 3],
    nb_rows=100,
    nb_cols=100,
    white_percentage=0.50
)

interval = 200  # time in ms


def init():
    copy_matrix = np.reshape(matrix.matrix, (matrix.nb_rows, matrix.nb_cols))
    image.set_data(copy_matrix)


def animate(_):
    matrix.update_matrix()
    copy_matrix = np.reshape(matrix.matrix, (matrix.nb_rows, matrix.nb_cols))
    image.set_data(copy_matrix)
    return image


if __name__ == '__main__':
    fig = plt.figure()
    data = np.zeros((matrix.nb_rows, matrix.nb_cols))
    image = plt.imshow(data, cmap='gist_gray_r', vmin=0, vmax=1)

    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=matrix.nb_rows * matrix.nb_cols, interval=interval)
    plt.show()

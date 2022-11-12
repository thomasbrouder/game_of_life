"""
    Conway's game of life
    Rules:
        1. Any live cell with the right number of live neighbours (usually between two and three) survives.
        2. Any dead cell with the right number of live neighbours (usually three) becomes a live cell.
        3. Any other live cell dies in the next generation. Similarly, any other dead cell stays dead.
"""

from matplotlib import pyplot as plt
from matplotlib import animation
import matrix


def main(matrix):
    """Runs and displays the cells' matrix generation after generation.

    Args:
        matrix (matrix.Matrix): matrix of cells.

    """
    def init():
        image.set_data(matrix.cells)

    def animate(_):
        matrix.update()
        image.set_data(matrix.cells)
        return image

    fig = plt.figure()
    image = plt.imshow(matrix.cells, cmap='gist_gray_r', vmin=0, vmax=1)

    interval = 200  # period of time before displaying next generation in ms
    _ = animation.FuncAnimation(
        fig,
        animate,
        init_func=init,
        frames=matrix.nb_rows * matrix.nb_cols,
        interval=interval
    )
    plt.xticks([])
    plt.yticks([])
    plt.show()


if __name__ == '__main__':
    matrix = matrix.Matrix(
        params=[2, 3, 3, 3],
        nb_rows=150,
        nb_cols=150,
        init_live_pct=0.10
    )
    main(matrix)

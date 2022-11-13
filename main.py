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
import game_controller


def main(controller):
    """Runs and displays the cells' matrix generation after generation.

    Args:
        matrix (matrix.Matrix): matrix of cells.

    """
    nb_rows, nb_cols = controller.shape
    line_width = 0.3
    lines_color = "black"

    shift = 0.5

    def init():
        controller.step_run()
        image.set_data(controller.cells)

    def animate(_):
        controller.step_run()
        image.set_data(controller.cells)

    def onclick(event):
        """Callback function to control cells' matrix state with mouse events.

        Args:
            event (matplotlib.backend_bases.MouseEvent): mouse event

        Notes:
            left-click on a given cell: it becomes dead if it was alive and the other way around.
                Warning: the game as to be paused for this action to be effective.
            double-middle-click anywhere: the game stops or resumes

        """
        if event.dblclick and event.button == 2:
            controller.is_running = not controller.is_running
        elif event.button == 1:
            controller.cursor_coords = int(event.xdata + shift), int(event.ydata + shift)

    fig = plt.figure()
    fig.canvas.mpl_connect('button_press_event', onclick)

    image = plt.imshow(controller.cells, cmap='gist_gray_r', vmin=0, vmax=1)

    _ = animation.FuncAnimation(
        fig,
        animate,
        init_func=init,
        frames=nb_rows * nb_cols,
        interval=controller.interval
    )
    plt.xticks([])
    plt.yticks([])

    for i in range(nb_rows):
        plt.hlines(y=i - shift, xmin=-shift, xmax=nb_cols - shift, color=lines_color, linewidth=line_width)
    for i in range(nb_cols):
        plt.vlines(x=i - shift, ymin=-shift, ymax=nb_rows - shift, color=lines_color, linewidth=line_width)
    plt.show()


if __name__ == '__main__':
    my_matrix = matrix.Matrix(
        params=[2, 3, 3, 3],
        nb_rows=200,
        nb_cols=300,
        init_live_pct=0.10
    )
    controller = game_controller.Controller(my_matrix, interval=200)
    main(controller)

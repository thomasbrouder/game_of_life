"""
    Conway's game of life
    Rules:
        1. Any live cell with the right number of live neighbours (usually between two and three) survives.
        2. Any dead cell with the right number of live neighbours (usually three) becomes a live cell.
        3. Any other live cell dies in the next generation. Similarly, any other dead cell stays dead.
"""

from matplotlib import animation
import matrix
import game_controller
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvas, NavigationToolbar2QT
from matplotlib.figure import Figure
import sys


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self, controller, show_grid=True, grid_line_width=0.3, lines_color="black"):
        """Controls and shows the game.

        Args:
            controller (game_controller.Controller): game controller.
            grid_line_width (float): width of the grid lines displayed.
            lines_color (str): color of the grid lines.
            show_grid (bool):

        Notes:
            Allowed colors are listed here: https://matplotlib.org/stable/gallery/color/named_colors.html

        """
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)

        self._fig = Figure(figsize=(5, 3))
        self._canvas = FigureCanvas(self._fig)
        layout.addWidget(self._canvas)
        layout.addWidget(NavigationToolbar2QT(self._canvas, self))

        self._axis = self._canvas.figure.subplots()

        self._controller = controller
        self._nb_rows, self._nb_cols = self._controller.shape
        self._grid_line_width = grid_line_width
        self._lines_color = lines_color

        self._grid_shift = 0.5  # Used to counterbalance the fact that grid cells are centered on their coordinates.
        self._show_grid = show_grid
        self._image = None
        self._run()

    def _run(self):
        """Runs and displays the cells' matrix generation after generation.

        Args:
            matrix (matrix.Matrix): matrix of cells.

        """
        self._canvas.mpl_connect('button_press_event', self._onclick)
        self._image = self._axis.imshow(self._controller.cells, cmap='gist_gray_r', vmin=0, vmax=1)
        self.animation = animation.FuncAnimation(
            self._fig,
            func=self._animate,
            frames=self._nb_rows * self._nb_cols,
            interval=self._controller.interval
        )
        self._axis.set_xticks([])
        self._axis.set_yticks([])

        if self._show_grid:
            shift = self._grid_shift
            color = self._lines_color
            width = self._grid_line_width
            for i in range(self._nb_rows):
                self._axis.hlines(y=i - shift, xmin=-shift, xmax=self._nb_cols - shift, color=color, linewidth=width)
            for i in range(self._nb_cols):
                self._axis.vlines(x=i - shift, ymin=-shift, ymax=self._nb_rows - shift, color=color, linewidth=width)

    def _animate(self, _):
        """Updates the view."""
        self._controller.step_run()
        self._image.set_data(self._controller.cells)

    def _onclick(self, event):
        """Callback function to control cells' matrix state with mouse events.

        Args:
            event (matplotlib.backend_bases.MouseEvent): mouse event

        Notes:
            left-click on a given cell: it becomes dead if it was alive and the other way around.
                Warning: the game as to be paused for this action to be effective.
            double-middle-click anywhere: the game stops or resumes

        """
        if event.dblclick and event.button == 2:
            self._controller.is_running = not self._controller.is_running
        elif event.button == 1:
            self._controller.selected_cell = int(event.xdata + self._grid_shift), int(event.ydata + self._grid_shift)


if __name__ == '__main__':
    my_matrix = matrix.Matrix(
        params=[2, 3, 3, 3],
        nb_rows=60,
        nb_cols=100,
        init_live_pct=0.10
    )
    controller = game_controller.Controller(my_matrix, interval=50)
    qapp = QtWidgets.QApplication.instance()
    if not qapp:
        qapp = QtWidgets.QApplication(sys.argv)

    app = ApplicationWindow(controller)
    app.show()
    app.activateWindow()
    app.raise_()
    qapp.exec()

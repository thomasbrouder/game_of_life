"""
    Conway's game of life
    Rules:
        1. Any live cell with the right number of live neighbours (usually between two and three) survives.
        2. Any dead cell with the right number of live neighbours (usually three) becomes a live cell.
        3. Any other live cell dies in the next generation. Similarly, any other dead cell stays dead.
"""
import time

from matplotlib import animation
import matrix
import game_controller
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvas, NavigationToolbar2QT
from matplotlib.figure import Figure
import sys
import glob
from matplotlib.colors import ListedColormap
import logging

logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel("INFO")


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

        # Create a horizontal layout to include both the plot and buttons
        main_layout = QtWidgets.QHBoxLayout(self._main)

        # Create a layout for buttons, combo boxes, and add some buttons
        control_layout = QtWidgets.QVBoxLayout()

        files = glob.glob("data/patterns/*.txt")
        self.filenames = {
            file.split("/")[-1].split(".")[0].replace("_", " "): file for file in files
        }
        self.nameComboBox = QtWidgets.QComboBox()
        pattern_names = list(self.filenames.keys())
        self.nameComboBox.addItems(pattern_names)
        self._selected_pattern = pattern_names[0]
        self.nameComboBox.currentIndexChanged.connect(self.on_name_selected)  # Connect to a slot
        control_layout.addWidget(self.nameComboBox)

        # Add buttons
        self.play_button = QtWidgets.QPushButton('Play/Pause')
        self.add_pattern_button = QtWidgets.QPushButton('Add pattern')
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.add_pattern_button)
        self.play_button.clicked.connect(self.play_clicked_action)
        self.add_pattern_button.clicked.connect(self.add_pattern_action)
        control_layout.addStretch()  # This ensures the controls are top aligned

        self.inputField = QtWidgets.QLineEdit()
        control_layout.addWidget(self.inputField)
        self.inputField.setPlaceholderText('Enter your value here')
        self.inputField.returnPressed.connect(self.on_input_entered)

        plot_layout = QtWidgets.QVBoxLayout(self._main)

        self._fig = Figure(figsize=(5, 3))
        self._canvas = FigureCanvas(self._fig)

        # Adjust layout to reduce spacing and padding
        self._fig.subplots_adjust(left=0, right=1, top=1, bottom=0)  # Adjust these values as needed

        plot_layout.addWidget(self._canvas)
        plot_layout.addWidget(NavigationToolbar2QT(self._canvas, self))

        self._axis = self._canvas.figure.subplots()

        self._add_pattern_mode = False
        self._controller = controller
        self._nb_rows, self._nb_cols = self._controller.shape
        self._grid_line_width = grid_line_width
        self._lines_color = lines_color

        self._grid_shift = 0.5  # Used to counterbalance the fact that grid cells are centered on their coordinates.
        self._show_grid = show_grid
        self._image = None

        main_layout.addLayout(control_layout, 1)
        main_layout.addLayout(plot_layout, 6)
        # Maximize the window
        self.showMaximized()
        self._run()

    def on_input_entered(self):
        # TODO Make controller responsible for interval value changes
        self._controller.interval = self.inputField.text()
        self.animation.event_source.interval = int(self._controller.interval)

    def play_clicked_action(self):
        self.start_time = time.time()
        self._controller.is_running = not self._controller.is_running

    def add_pattern_action(self):
        self._add_pattern_mode = not self._add_pattern_mode

    def on_name_selected(self, index):
        self._selected_pattern = self.nameComboBox.currentText()

    def _run(self):
        """Runs and displays the cells' matrix generation after generation.

        Args:
            matrix (matrix.Matrix): matrix of cells.

        """
        self._canvas.mpl_connect('button_press_event', self._onclick)

        custom_cmap = ListedColormap(['black', 'white'])
        self._image = self._axis.imshow(self._controller.cells, cmap=custom_cmap, vmin=0, vmax=1)
        self.animation = animation.FuncAnimation(
            self._fig,
            func=self._animate,
            frames=self._controller.step_run,
            interval=self._controller.interval,
            cache_frame_data=False,
            blit=True,
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
        nb_iterations = self._controller._matrix.iteration
        if self._controller.is_running and nb_iterations % 30 == 0:
            elapsed_time = time.time() - self.start_time
            logger.info("Frequency: %s", round(nb_iterations / elapsed_time, 3))
        self._image.set_data(self._controller.cells)
        return [self._image]

    def _onclick(self, event):
        """Callback function to control cells' matrix state with mouse events.

        Args:
            event (matplotlib.backend_bases.MouseEvent): mouse event

        Notes:
            left-click on a given cell: it becomes dead if it was alive and the other way around.
                Warning: the game as to be paused for this action to be effective.
            double-middle-click anywhere: the game stops or resumes

        """
        if event.dblclick:
            self._controller.is_running = not self._controller.is_running

        elif event.button == 1:
            selected_cell = int(event.xdata + self._grid_shift), int(
                event.ydata + self._grid_shift)
            if self._add_pattern_mode:
                filename = self.filenames.get(self._selected_pattern)
                pattern = matrix.load_pattern(filename)
                x, y = selected_cell
                self._controller._matrix.add_pattern(pattern, pos=(y, x))
            else:
                self._controller.selected_cell = selected_cell


def run():
    my_matrix = matrix.Matrix(
        params=[2, 3, 3, 3],
        nb_rows=1000,
        nb_cols=1000,
        init_live_pct=0
    )
    controller = game_controller.Controller(my_matrix, interval=0)
    qapp = QtWidgets.QApplication.instance()
    if not qapp:
        qapp = QtWidgets.QApplication(sys.argv)

    app = ApplicationWindow(controller, lines_color="black")
    app.show()
    app.activateWindow()
    app.raise_()
    qapp.exec()


if __name__ == '__main__':
    import profile_tools
    profile_tools.profile(run)

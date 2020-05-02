"""
EvoFlock UI

This is the front end for the application to visualise the evolutionary process.


"""
import sys
import random
from PySide2 import QtGui, QtCore, QtWidgets
import screeninfo


class UserInterface(QtWidgets.QWidget):

    def __init__(self):
        super(UserInterface, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.setGeometry(0, 0,
                         screeninfo.get_monitors()[0].width,
                         screeninfo.get_monitors()[0].height)
        self.setWindowTitle("EvoFlock")
        self.user_settings_groupbox = QtWidgets.QGroupBox("Settings")
        self.user_settings_groupbox.setMaximumSize(int(screeninfo.get_monitors()[0].width/5),
                                                   screeninfo.get_monitors()[0].height)
        self.simulation_window_groupbox = QtWidgets.QGroupBox("Simulation")

        self.graphics_container = QtWidgets.QGraphicsView()
        self.scene = QtWidgets.QGraphicsScene()
        self.graphics_container.setScene(self.scene)

        self.main_window_layout = QtWidgets.QHBoxLayout()
        self.main_window_layout.addWidget(self.user_settings_groupbox)
        self.main_window_layout.addWidget(self.simulation_window_groupbox)
        self.setLayout(self.main_window_layout)

        #self.drawUniverse(self.simulation_window_groupbox.width, self.simulation_window_groupbox.height())
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.rePaint)

        self.show()

    def startAnimation(self, universe):
        """Start the animation timer.
        """
        self.universe = universe
        self.timer.start(100)

    def stopAnimation(self):
        """Stop the animation timer.
        """
        self.timer.stop()

    def rePaint(self):
        """Animate the cell generations.
        """
        self.clearScene()
        univY, univX = self.universe.getDimension()
        self.drawUniverse(univX, univY)
        self.populateCells()
        self.universe.nextGeneration()

    def clearScene(self):
        """Clear the scene.
        """
        self.scene.clear()

    def drawUniverse(self):
        """Draw the universe grid.
        """

        self.fitInView(self.scene.itemsBoundingRect())

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.draw_points(qp)
        qp.end()

    def draw_points(self, qp):
        red_colour = QtGui.QColor(255, 0, 0)
        red_colour.setNamedColor("red")
        qp.setPen(QtCore.Qt.red)

        size = self.size()
        for i in range(1000):
            x = random.randint(1, size.width() - 1)
            y = random.randint(1, size.height() - 1)
            qp.drawPoint(x, y)

    def draw_prey_points(self, qp):
        blue_colour = QtGui.QColor(0, 0, 255)
        blue_colour.setNamedColor("blue")
        qp.setPen(QtCore.Qt.blue)

        size = self.size()
        for i in range(1000):
            x = random.randint(1, size.width() - 1)
            y = random.randint(1, size.height() - 1)
            qp.drawPoint(x, y)


def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = UserInterface()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

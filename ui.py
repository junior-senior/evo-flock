"""
EvoFlock UI

This is the front end for the application to visualise the evolutionary process.


"""
import sys

from PySide2 import QtGui, QtCore, QtWidgets
import screeninfo

import EvoFlock


class UserInterface(QtWidgets.QWidget):

    def __init__(self, evo_flock):
        super(UserInterface, self).__init__()
        self.evo_flock = evo_flock
        self.init_ui()

    def init_ui(self):
        self.setGeometry(0, 0,
                         screeninfo.get_monitors()[0].width,
                         screeninfo.get_monitors()[0].height)
        self.setWindowTitle("EvoFlock")

        #self.showFullScreen()

        self.user_settings_groupbox = QtWidgets.QGroupBox("Settings")
        self.user_settings_groupbox.setMaximumSize(int(screeninfo.get_monitors()[0].width/5),
                                                   screeninfo.get_monitors()[0].height)
        self.simulation_window_groupbox = QtWidgets.QGroupBox("Simulation")

        self.main_window_layout = QtWidgets.QHBoxLayout()
        self.main_window_layout.addWidget(self.user_settings_groupbox)
        self.main_window_layout.addWidget(self.simulation_window_groupbox)
        self.setLayout(self.main_window_layout)

        self.graphics_container = QtWidgets.QGraphicsView(self.simulation_window_groupbox)
        self.scene = QtWidgets.QGraphicsScene()
        self.graphics_container.setScene(self.scene)

        self.sim_layout = QtWidgets.QGridLayout()
        self.sim_layout.addWidget(self.graphics_container)
        self.simulation_window_groupbox.setLayout(self.sim_layout)

        self.draw_world()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.re_paint)
        self.animate()
        self.show()

    def start_animation(self):
        """Start the animation timer.
        """
        self.timer.start(100)

    def stop_animation(self):
        """Stop the animation timer.
        """
        self.timer.stop()

    def re_paint(self):
        """Animate the cell generations.
        """
        self.evo_flock.main_loop()
        self.clear_scene()
        self.draw_world()
        self.populate_world()

    def clear_scene(self):
        """Clear the scene.
        """
        self.scene.clear()

    def draw_world(self):
        """Create the world space.
        """
        print()
        self.scene.setSceneRect(QtCore.QRectF(0, 0,
                                              self.simulation_window_groupbox.size().width() - 100,
                                              self.simulation_window_groupbox.size().height() - 100))

        self.graphics_container.fitInView(self.scene.itemsBoundingRect())

    def populate_world(self):
        """Draw the creatures.
        """
        # populate the grid with blue squares representing creatures
        for creature in self.evo_flock.creatures:
            self.draw_creatures(True, creature)  # Draw Creatures
        self.draw_creatures(False, self.evo_flock.predator)  # Draw Predator

    def draw_creatures(self, creature_or_predator, creature):
        """Fill the cell at grid location (x, y)
        """
        x = creature.x_position
        y = creature.y_position
        world_left = 0
        world_top = 0
        world_right = self.simulation_window_groupbox.size().width() - 100
        world_bottom = self.simulation_window_groupbox.size().height() - 100
        creature_x_in_world = int(((world_right - world_left) * x) + world_left)
        creature_y_in_world = int(((world_bottom - world_top) * y) + world_top)
        item = QtWidgets.QGraphicsRectItem(creature_x_in_world, creature_y_in_world, 10, 10)
        if creature_or_predator:
            item.setBrush(QtGui.QBrush(QtCore.Qt.blue))
        else:
            item.setBrush(QtGui.QBrush(QtCore.Qt.red))
        self.scene.addItem(item)

    def animate(self):
        """Start animating the selected pattern.
        """
        self.start_animation()


def main():
    app = QtWidgets.QApplication(sys.argv)
    evoflock = EvoFlock.EvoFlock()
    ex = UserInterface(evoflock)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

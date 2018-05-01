#!/bin/python3

import sys
import os

from PyQt5.QtCore import QSize, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QMessageBox

from config import *
from data import DataManager
from widgets import JointsCoordinateTable, ClickImageView, JointsHover, CategoryComboBox

os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = '1'

class MainWindow(QWidget):
    def __init__(self, size, title, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowIcon(QIcon('./icon.png'))
        self.setWindowIconText(WINDOW_TITLE)
        self.main_layout = QHBoxLayout(self)
        self.detail_layout = QVBoxLayout()
        self.rewriteButton = QPushButton()
        self.confirmButton = QPushButton()
        self.toggleHoverButton = QPushButton()

        self.img_view = ClickImageView()
        self.joints_hover = JointsHover(self)
        self.joints_table = JointsCoordinateTable(10, 2)
        self.category_box = CategoryComboBox()
        self.hint = QLabel()

        self.init_ui(size, title)

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == 16777220:  # Key-Enter
            self.confirmButton.click()

    @pyqtSlot(name='exit')
    def exit(self):
        self.close()

    def init_ui(self, size, title):
        self.setFixedSize(size)
        self.setWindowTitle(title)

        self.img_view.connect_to_table(self.joints_table)
        self.img_view.connect_to_box(self.category_box)
        self.img_view.connect_to_window(self)
        self.joints_table.connect_to_window(self)
        self.joints_table.connect_to_hover(self.joints_hover)
        self.category_box.connect_to_window(self)
        self.joints_hover.connect_to_table(self.joints_table)

        self.toggleHoverButton.setText('Toggle the hover')
        self.toggleHoverButton.clicked.connect(self.joints_hover.toggle_visible)
        self.rewriteButton.setText('Retry')
        self.rewriteButton.setStyleSheet('background-color: red')
        self.rewriteButton.clicked.connect(self.joints_table.clearContents)
        self.rewriteButton.clicked.connect(self.category_box.reset)
        self.confirmButton.setText('Confirm')
        self.confirmButton.setStyleSheet('background-color: green')
        # self.confirmButton.clicked.connect(self.img_view.next_image)
        self.confirmButton.clicked.connect(self.save_sample)

        self.hint.setText('*L/R refers to the image.')
        self.hint.setStyleSheet('font-size: 8pt')
        self.hint.setWordWrap(True)

        self.detail_layout.setContentsMargins(10, 10, 10, 10)
        self.detail_layout.addWidget(self.joints_table)
        self.detail_layout.addWidget(self.category_box)
        self.detail_layout.addWidget(self.toggleHoverButton)
        self.detail_layout.addWidget(self.rewriteButton)
        self.detail_layout.addWidget(self.confirmButton)
        self.detail_layout.addWidget(self.hint)

        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.img_view)
        self.main_layout.addLayout(self.detail_layout)

        self.joints_hover.raise_()

    @pyqtSlot(name='enable_confirm_button')
    def enable_confirm_button(self):
        if self.joints_table.filled() and self.category_box.is_chosen():
            self.confirmButton.setEnabled(True)

    @pyqtSlot(name='disable_confirm_button')
    def disable_confirm_button(self):
        self.confirmButton.setEnabled(False)

    @pyqtSlot(name='save_sample')
    def save_sample(self):
        DataManager().save_sample(self.img_view.current_image,
                                  sum(self.joints_table.joints, []),
                                  self.category_box.currentIndex())
        self.img_view.next_image()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow(size=QSize(WINDOW_W, WINDOW_H), title=WINDOW_TITLE)
    window.img_view.change_image(next(DataManager().image_loader))
    window.show()

    app.exec_()

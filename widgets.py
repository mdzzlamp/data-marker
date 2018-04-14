from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt5.QtWidgets import QLabel, QTableWidgetItem, QTableWidget, QAbstractItemView

from config import WINDOW_H


class ClickImageView(QLabel):
    painter: QPainter
    image_clicked = pyqtSignal(int, int, name='image_clicked')
    image_changed = pyqtSignal(name='image_changed')

    def __init__(self, *__args):
        super().__init__(*__args)
        self.setFixedSize(WINDOW_H, WINDOW_H)
        self.setMargin(0)

    def connect_to_table(self, joints_table):
        self.image_clicked.connect(joints_table.add_coordinate)
        self.image_changed.connect(joints_table.clearContents)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.image_clicked.emit(event.pos().x(), event.pos().y())

    def change_image(self, path):
        img = QPixmap(path).scaled(WINDOW_H, WINDOW_H)
        self.setPixmap(img)
        self.image_changed.emit()

    def next_image(self):
        # TODO implement data loader
        self.change_image('./data/test02.jpg')


class JointsCoordinateTable(QTableWidget):
    table_filled = pyqtSignal(bool, name='table_filled')
    table_cleared = pyqtSignal(bool, name='table_cleared')
    coordinate_changed = pyqtSignal(list, name='coordinate_added')

    def __init__(self, *__args):
        super().__init__(*__args)
        self.joints = []
        self.clearContents()
        self.currentActiveRow = 0
        self.setFixedHeight(227)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setHorizontalHeaderLabels(['x', 'y'])
        self.setVerticalHeaderLabels(['Eye L', 'Eye R', 'Neck', 'chest',
                                      'Shoulder L', 'Shoulder R',
                                      'Elbow L', 'Elbow R',
                                      'Hand L', 'Hand R'])
        for col in range(self.columnCount()):
            self.setColumnWidth(col, 70)
        for row in range(self.rowCount()):
            self.setRowHeight(row, 20)

    def connect_to_button(self, confirm_button):
        self.table_filled.connect(confirm_button.setEnabled)
        self.table_cleared.connect(confirm_button.setEnabled)

    def connect_to_hover(self, hover):
        self.coordinate_changed.connect(hover.show_joints)

    @pyqtSlot(int, int, name='add_coordinate')
    def add_coordinate(self, x, y):
        if self.currentActiveRow == self.rowCount():
            return
        print('add coordinate({0},{1}) to row({2})'.format(x, y, self.currentActiveRow))
        self.setItem(self.currentActiveRow, 0, QTableWidgetItem(str(x)))
        self.setItem(self.currentActiveRow, 1, QTableWidgetItem(str(y)))
        self.currentActiveRow += 1
        self.selectRow(self.currentActiveRow)
        self.joints.append((x, y))
        self.coordinate_changed.emit(self.joints)

        if self.currentActiveRow == self.rowCount():
            self.table_filled.emit(True)

    @pyqtSlot(name='clear_contents')
    def clearContents(self):
        super(JointsCoordinateTable, self).clearContents()
        self.currentActiveRow = 0
        self.selectRow(self.currentActiveRow)
        self.joints.clear()
        self.coordinate_changed.emit(self.joints)
        self.table_cleared.emit(False)


class JointsHover(QLabel):
    image_clicked = pyqtSignal(int, int, name='image_clicked')

    def __init__(self, *__args):
        super().__init__(*__args)
        self.setFixedSize(WINDOW_H, WINDOW_H)
        self.joints = []
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet('QLabel{background:rgba(0,0,0,0.65);}')

    def connect_to_table(self, joints_table):
        self.image_clicked.connect(joints_table.add_coordinate)

    @pyqtSlot(name='toggle_visible')
    def toggle_visible(self):
        self.setVisible(not self.isVisible())

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.image_clicked.emit(event.pos().x(), event.pos().y())

    def paintEvent(self, QPaintEvent):
        print('painting...')
        super(JointsHover, self).paintEvent(QPaintEvent)
        painter = QPainter(self)

        pen = QPen(QColor(125, 125, 125))
        pen.setWidth(8)
        painter.setPen(pen)
        if len(self.joints) >= 2:
            painter.drawLine(self.joints[0][0], self.joints[0][1], self.joints[1][0], self.joints[1][1])

        pen = QPen(QColor(255, 0, 0))
        pen.setWidth(15)
        painter.setPen(pen)
        for x, y in self.joints:
            painter.drawPoint(x, y)

        painter.end()

    @pyqtSlot(list, name='show_joints')
    def show_joints(self, joints):
        print('show_joints')
        self.joints = joints
        self.repaint()

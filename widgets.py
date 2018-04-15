from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt5.QtWidgets import QLabel, QTableWidgetItem, QTableWidget, QAbstractItemView, QComboBox

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

    def connect_to_box(self, box):
        self.image_changed.connect(box.reset)

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
    table_filled = pyqtSignal(name='table_filled')
    table_cleared = pyqtSignal(name='table_cleared')
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

    def connect_to_window(self, window):
        self.table_filled.connect(window.enable_confirm_button)
        self.table_cleared.connect(window.disable_confirm_button)

    def connect_to_hover(self, hover):
        self.coordinate_changed.connect(hover.show_joints)

    @pyqtSlot(int, int, name='add_coordinate')
    def add_coordinate(self, x, y):
        if self.filled():
            return
        self.setItem(self.currentActiveRow, 0, QTableWidgetItem(str(x)))
        self.setItem(self.currentActiveRow, 1, QTableWidgetItem(str(y)))
        self.currentActiveRow += 1
        self.selectRow(self.currentActiveRow)
        self.joints.append((x, y))
        self.coordinate_changed.emit(self.joints)

        if self.filled():
            self.table_filled.emit()

    def filled(self):
        return self.currentActiveRow == self.rowCount()

    @pyqtSlot(name='clear_contents')
    def clearContents(self):
        super(JointsCoordinateTable, self).clearContents()
        self.currentActiveRow = 0
        self.selectRow(self.currentActiveRow)
        self.joints.clear()
        self.coordinate_changed.emit(self.joints)
        self.table_cleared.emit()


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
        super(JointsHover, self).paintEvent(QPaintEvent)
        joints_cnt = len(self.joints)
        painter = QPainter(self)

        pen = QPen(QColor(125, 125, 125))
        pen.setWidth(8)
        painter.setPen(pen)
        if joints_cnt >= 2:
            painter.drawLine(self.joints[0][0], self.joints[0][1], self.joints[1][0], self.joints[1][1])
        if joints_cnt >= 3:
            painter.drawLine((self.joints[0][0] + self.joints[1][0]) // 2, (self.joints[0][1] + self.joints[1][1]) // 2,
                             self.joints[2][0], self.joints[2][1])
        if joints_cnt >= 4:
            painter.drawLine(self.joints[2][0], self.joints[2][1], self.joints[3][0], self.joints[3][1])
        if joints_cnt >= 5:
            painter.drawLine(self.joints[2][0], self.joints[2][1], self.joints[4][0], self.joints[4][1])
        if joints_cnt >= 6:
            painter.drawLine(self.joints[2][0], self.joints[2][1], self.joints[5][0], self.joints[5][1])
        if joints_cnt >= 7:
            painter.drawLine(self.joints[4][0], self.joints[4][1], self.joints[6][0], self.joints[6][1])
        if joints_cnt >= 8:
            painter.drawLine(self.joints[5][0], self.joints[5][1], self.joints[7][0], self.joints[7][1])
        if joints_cnt >= 9:
            painter.drawLine(self.joints[6][0], self.joints[6][1], self.joints[8][0], self.joints[8][1])
        if joints_cnt >= 10:
            painter.drawLine(self.joints[7][0], self.joints[7][1], self.joints[9][0], self.joints[9][1])

        pen = QPen(QColor(255, 0, 0))
        pen.setWidth(15)
        painter.setPen(pen)
        for x, y in self.joints:
            painter.drawPoint(x, y)

        painter.end()

    @pyqtSlot(list, name='show_joints')
    def show_joints(self, joints):
        self.joints = joints
        self.repaint()


class CategoryComboBox(QComboBox):
    on_chosen = pyqtSignal(name='on_chosen')

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.currentIndexChanged.connect(self.on_changed)

    def init_ui(self):
        self.addItems(['正确坐姿', '趴写', '左手托腮', '右手托腮', '头往左斜', '头往右斜', '驼背', '含笔'])

    def connect_to_window(self, window):
        self.on_chosen.connect(window.enable_confirm_button)

    def on_changed(self):
        if self.is_chosen():
            self.on_chosen.emit()

    @pyqtSlot(name='reset')
    def reset(self):
        self.setCurrentIndex(-1)    # choose nothing initially

    def is_chosen(self):
        return self.currentIndex() != -1

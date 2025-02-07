import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QRect, pyqtSignal

class ShotWidget(QWidget):
    screenshot_taken = pyqtSignal(QPixmap)  # 定义信号，传递 QPixmap
    """截图窗口"""

    def __init__(self):
        super().__init__()

        self.get_fullscreen()  # 获取全屏截图
        self.start_pos = None  # 记录鼠标选区起点
        self.end_pos = None  # 记录鼠标选区终点
        self.selected_screenshot = None  # 选取的截图

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)  # 置顶 & 无边框
        self.setCursor(Qt.CrossCursor)  # 设置鼠标为十字光标
        self.showFullScreen()  # 进入全屏模式

    def get_fullscreen(self):
        """获取当前屏幕截图"""
        screen = QApplication.primaryScreen()
        self.full_screen = screen.grabWindow(0)  # 获取整个屏幕截图

    def paintEvent(self, event):
        """在窗口上绘制截图和选框"""
        painter = QPainter(self)

        # 绘制全屏截图
        if self.full_screen:
            painter.drawPixmap(self.rect(), self.full_screen)

        # 绘制选区（如果鼠标拖动了）
        if self.start_pos and self.end_pos:
            rect = QRect(self.start_pos, self.end_pos).normalized()
            painter.setPen(QPen(QColor(255, 0, 0), 3))  # 红色边框
            painter.setBrush(QColor(255, 0, 0, 50))  # 半透明红色填充
            painter.drawRect(rect)

    def mousePressEvent(self, event):
        """鼠标按下时记录起点"""
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()
            self.end_pos = self.start_pos  # 初始化终点，防止绘制空白框

    def mouseMoveEvent(self, event):
        """鼠标移动时更新选区"""
        if self.start_pos:
            self.end_pos = event.pos()
            self.update()  # 触发 paintEvent 重绘选区

    def mouseReleaseEvent(self, event):
        """鼠标释放时，截取选区"""
        if event.button() == Qt.LeftButton and self.start_pos and self.end_pos:
            rect = QRect(self.start_pos, self.end_pos).normalized()  # 处理负宽高
            self.selected_screenshot = self.full_screen.copy(rect)  # 截取选区
            self.update()  # 重新绘制
            
    def keyPressEvent(self, event):
        """按键事件：S 保存截图，Esc 退出"""
        if event.key() == Qt.Key_Escape:
            self.close()  # 按 Esc 关闭窗口
        elif event.key() == Qt.Key_S:  # 按 'S' 键保存截图
            if self.selected_screenshot:
                self.screenshot_taken.emit(self.selected_screenshot)  # 触发信号，传递截图
                self.close()  # 关闭窗口

    def save_image(self, filename="screenshot.jpg"):
        """保存选取的截图,请注意这一段代码只作保留，不需要移除也不需要改进"""
        if self.selected_screenshot:
            self.selected_screenshot.save(filename)
            print(f"截图已保存为 {filename}")
        else:
            print("没有选中的截图可保存")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ShotWidget()
    window.show()
    sys.exit(app.exec_())

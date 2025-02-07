import sys
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QWidget
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt

class MyGraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()

        # 初始化场景
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # 加载和设置图片
        pixmap = QPixmap("new_test.png")  # 加载图片
        self.pixmap_item = QGraphicsPixmapItem(pixmap)
        self.pixmap_item.setScale(0.8)  # 设置缩放比例
        self.pixmap_item.setOpacity(1)  # 设置透明度
        self.scene.addItem(self.pixmap_item)

        # 设置渲染选项
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)

        # 设置视图拖动模式
        self.setDragMode(QGraphicsView.ScrollHandDrag)

    def update_image(self, new_pixmap: QPixmap):
        """更新图像"""
        if not new_pixmap.isNull():
            self.pixmap_item.setPixmap(new_pixmap)  # 更新图像项
        else:
            print("Error: Invalid pixmap.")

    def wheelEvent(self, event):
        """鼠标滚轮缩放事件"""
        factor = 1.1 if event.angleDelta().y() > 0 else 0.9
        self.scale(factor, factor)  # 按比例缩放

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)  # 启用拖动模式
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        self.setDragMode(QGraphicsView.NoDrag)  # 禁用拖动模式
        super().mouseReleaseEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = MyGraphicsView()
    view.resize(800, 600)
    view.show()
    sys.exit(app.exec_())

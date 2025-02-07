import sys
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt

class ImageViewer(QGraphicsView):
    def __init__(self, image_path):
        super().__init__()

        # 创建场景
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # 加载图片
        self.pixmap_item = QGraphicsPixmapItem(QPixmap(image_path))
        self.scene.addItem(self.pixmap_item)

        # 允许鼠标拖动
        self.setDragMode(QGraphicsView.ScrollHandDrag)

        # 允许鼠标缩放
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        # 设置初始缩放比例
        self.scale_factor = 1.0
        self.max_scale = 10.0  # 最大缩放比例
        self.min_scale = 0.2  # 最小缩放比例

        # 调整图像大小以适应窗口
        self.adjust_image_to_view()

        # 设置水平和垂直滚动条策略
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

    def update_image(self, image_path):
        """ 更新图像 """
        new_pixmap = QPixmap(image_path)
        if not new_pixmap.isNull():
            # 更新图像
            self.pixmap_item.setPixmap(new_pixmap)
            self.adjust_image_to_view()  # 调整图像大小以适应视图

            # 手动刷新视图
            self.viewport().update()

    def wheelEvent(self, event):
        """ 处理鼠标滚轮缩放图片 """
        zoom_in_factor = 1.05
        zoom_out_factor = 0.95

        # 判断滚轮方向进行缩放
        if event.angleDelta().y() > 0:
            scale_factor = zoom_in_factor
        else:
            scale_factor = zoom_out_factor

        # 计算新的缩放因子
        new_scale_factor = self.scale_factor * scale_factor
        if self.min_scale <= new_scale_factor <= self.max_scale:
            self.scale_factor = new_scale_factor
            self.scale(scale_factor, scale_factor)

        # 手动更新视图
        self.viewport().update()

    def resizeEvent(self, event):
        """ 调整图像以适应窗口大小 """
        super().resizeEvent(event)
        self.adjust_image_to_view()

        # 手动更新视图
        self.viewport().update()

    def adjust_image_to_view(self):
        """ 调整图像大小以适应视图的大小 """
        if self.pixmap_item.pixmap().isNull():
            return
        
        # 获取视图和图片的尺寸
        view_width = self.viewport().width()
        view_height = self.viewport().height()
        pixmap_width = self.pixmap_item.pixmap().width()
        pixmap_height = self.pixmap_item.pixmap().height()

        # 计算缩放比例，保持图片宽高比
        scale_x = view_width / pixmap_width
        scale_y = view_height / pixmap_height
        scale_factor = min(scale_x, scale_y)

        # 应用缩放
        self.setRenderHint(QPainter.Antialiasing)
        self.resetTransform()
        self.scale(scale_factor, scale_factor)
        self.scale_factor = scale_factor


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # 图片路径
    image_path = 'screenshot.jpg'
    
    viewer = ImageViewer(image_path)
    viewer.setWindowTitle('Image Viewer')
    viewer.resize(800, 600)
    viewer.show()
    
    sys.exit(app.exec_())
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
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
            self.resetTransform()  # 重置变换
            self.scale(self.scale_factor, self.scale_factor)  # 应用新的缩放因子

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
        pixmap = self.pixmap_item.pixmap()
        if pixmap.isNull() or pixmap.width() == 0 or pixmap.height() == 0:
            return  # 如果图像无效，则不进行缩放操作
        
        # 获取视图和图片的尺寸
        view_width = self.viewport().width()
        view_height = self.viewport().height()
        pixmap_width = pixmap.width()
        pixmap_height = pixmap.height()

        # 计算缩放比例，保持图片宽高比
        scale_x = view_width / pixmap_width
        scale_y = view_height / pixmap_height
        scale_factor = min(scale_x, scale_y)

        # 应用缩放
        self.setRenderHint(QPainter.Antialiasing)
        self.resetTransform()
        self.scale(scale_factor, scale_factor)
        self.scale_factor = scale_factor

import re
import sys
from PyQt5.QtWidgets import QApplication, QComboBox, QShortcut, QFileDialog, QSizePolicy, QLineEdit, QHBoxLayout, QWidget, QVBoxLayout, QFrame, QLabel, QPushButton, QDesktopWidget, QTextEdit
from PyQt5.QtGui import QPixmap, QIcon, QKeySequence, QFont
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtWidgets import QMessageBox
from image_view import ImageViewer # 打开图片文件夹的程序
from shot import ShotWidget # 截图程序
from shot_view import MyGraphicsView # 展示截图程序
from connect import Access # 接入脚本
import ctypes
import os
import json

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.ui()
        self.center_window()

        self.current_model = "ep-20250114235143-2jcft"
        self.current_api = None
        self.image_list = None
        self.shot = None
        self.output_result = None
        self.folder = None
        self.save_times_dict = None
        self.my_text = self.input_text.text()
        self.cur_image_name = '1' # 这个仅仅是防止出错用的
        self.save_times_dict = {}
    
    def ui(self):
        # 设置窗口标题
        self.setWindowTitle("Latex标签器")
        icon = QIcon('icons/logo.ico')
        self.setWindowIcon(icon)  # 将图标设置为窗口图标

        main_layout = QHBoxLayout()
        row_one_layout = QVBoxLayout()
        row_one_layout.addWidget(self.create_one())
        row_one_layout.addWidget(self.create_two())

        backgroud_frame1 = QFrame()
        backgroud_frame1.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 white, stop:1 #f5f5f5);
                border-radius: 20px;
                border: 2px solid #e0e0e0;
            }
        """)
        backgroud_frame1.setLayout(row_one_layout)
        main_layout.addWidget(backgroud_frame1)

        three_layout = self.create_three()
        main_layout.addWidget(three_layout)
        main_layout.setStretch(0, 3)  # 第一个子布局 row_one_layout 伸缩因子 3
        main_layout.setStretch(1, 7)  # 第二个子布局 row_two_layout 伸缩因子 7
        self.setLayout(main_layout)

    def create_one(self):
        one = QFrame(self)
        one.setStyleSheet('''QFrame { border: none; } QGraphicsView {border: 1.5px solid rgba(224, 224, 224, 0.9); }''')
        main_layout = QVBoxLayout()
        child_layout1 = QHBoxLayout()
        child_layout2 = QHBoxLayout()
        child_layout3 = QHBoxLayout()
        child_layout4 = QHBoxLayout()

        
        # 创建按钮
        sc_btn = QPushButton('截图(W)(按下S选中)')
        sub_btn = QPushButton('识别(Ctrl+Space)')
        save_btn = QPushButton('保存(Ctrl+S)')

        # 创建按钮
        clarification1 = QLabel('模型选择: ')
        clarification1.setStyleSheet('border: none; ')
        clarification1.setAlignment(Qt.AlignCenter)
        self.model_cb = QComboBox()
        self.model_cb.addItems(['Doubao-vision-lite-32k', 'Doubao-vision-pro-32k', 'Doubao-1.5-vision-pro-32k', '通义千问2.5-VL-72B', "Kimi"])
        check_connect = QPushButton('测试连接(Enter)')

        api_clarication = QLabel('输入你的API KEY')
        self.api_input = QLineEdit()
        self.api_input.setPlaceholderText('请在这里输入你的模型的API KEY')
        self.api_input.textChanged.connect(self.on_api_key)

        # 输入文字
        clarification2 = QLabel('输入内容: ')
        clarification2.setStyleSheet("border: none; ")
        clarification2.setAlignment(Qt.AlignCenter)
        self.input_text = QLineEdit()
        self.input_text.setPlaceholderText('请在这里输入你的提示词')
        
        child_layout1.addWidget(sc_btn)
        child_layout1.addWidget(sub_btn)
        child_layout1.addWidget(save_btn)

        child_layout2.addWidget(clarification1)
        child_layout2.addWidget(self.model_cb)
        child_layout2.addWidget(check_connect)

        child_layout3.addWidget(clarification2)
        child_layout3.addWidget(self.input_text)

        child_layout4.addWidget(api_clarication)
        child_layout4.addWidget(self.api_input)

        # 显示截图
        self.my_shot = MyGraphicsView()
        
        main_layout.addLayout(child_layout2)
        main_layout.addLayout(child_layout3)
        main_layout.addLayout(child_layout4)
        main_layout.addLayout(child_layout1)
        main_layout.addWidget(self.my_shot)

        one.setLayout(main_layout)
        one.setFrameShape(QFrame.NoFrame)

        # 绑定按钮
        sc_btn.clicked.connect(self.take_screenshot)
        self.shot_shortcut = QShortcut(QKeySequence(Qt.Key_W), self)
        self.shot_shortcut.activated.connect(self.take_screenshot)

        self.model_cb.currentIndexChanged.connect(self.selectionchange)
        self.input_text.textChanged.connect(self.on_text_changed)

        check_connect.clicked.connect(self.test_connect)
        check_shortcut = QShortcut(QKeySequence(Qt.Key_Return), self)
        check_shortcut.activated.connect(self.test_connect)

        sub_btn.clicked.connect(self.connect)
        self.connect_shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Space), self)
        self.connect_shortcut.activated.connect(self.connect) 

        save_btn.clicked.connect(self.on_save)
        self.save_shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_S), self)
        self.save_shortcut.activated.connect(self.on_save)
        return one
    
    def on_api_key(self):
        self.current_api = self.api_input.text()
    
    def on_save(self):
        if self.shot and self.output_result and self.folder:

            cur_save_image_name = self.cur_image_name + '_' + str(self.save_times_dict[self.cur_image_name]) + '.jpg'
            cur_save_label_name = self.cur_image_name + '_' + str(self.save_times_dict[self.cur_image_name]) + '.txt'
            cur_save_image_path = os.path.join(self.shot_folder, cur_save_image_name)
            cur_save_label_path = os.path.join(self.label_folder, cur_save_label_name)

            self.shot.save(cur_save_image_path)
            with open(cur_save_label_path, 'w', encoding='utf-8') as label_file:
                label_file.write(self.output_result)

            with open(self.save_times_path, 'w') as save_times_file:
                json.dump(self.save_times_dict, save_times_file)

    def take_screenshot(self):
        """启动截图窗口"""
        self.shot_widget = ShotWidget()# 创建截图窗口实例
        self.shot_widget.screenshot_taken.connect(self.handle_screenshot_taken)# 连接 screenshot_taken 信号到处理函数

    def handle_screenshot_taken(self, pixmap: QPixmap):
        """处理接收到的截图"""
        if pixmap.isNull():
            pass
        else:
            self.shot = pixmap
            self.output_result = None
            self.my_shot.update_image(self.shot)
    
    def selectionchange(self, i):
        model_map = {'Doubao-vision-lite-32k': "ep-20250114235143-2jcft", 'Doubao-1.5-vision-pro-32k': 'ep-20250131202155-57zt4', 'Doubao-vision-pro-32k': "ep-20250201110631-2tlvx", "通义千问2.5-VL-72B": "qwen-vl-plus", "Kimi": "moonshot-v1-8k-vision-preview"}
        self.current_model = model_map[self.model_cb.currentText()]

    def on_text_changed(self):
        self.my_text = self.input_text.text()
    
    def test_connect(self):
        if self.current_model and self.current_api and self.my_text:
            self.reply = Access(self.current_api, self.current_model)
            self.reply.return_str.connect(self.set_output)
            self.reply.error_occurred.connect(self.show_error)  # 连接错误信号
            self.thread = MyThread(self.reply, 'access_test', self.my_text)
            self.thread.start()

    def connect(self):
        if self.current_model and self.current_api and self.shot and self.my_text:
            self.reply = Access(self.current_api, self.current_model)
            self.reply.return_str.connect(self.set_output)
            self.reply.error_occurred.connect(self.show_error)  # 连接错误信号
            self.thread = MyThread(self.reply, 'access', self.shot, self.my_text)
            self.thread.start()

            if self.cur_image_name not in self.save_times_dict.keys():
                self.save_times_dict[self.cur_image_name] = 0
            else:
                self.save_times_dict[self.cur_image_name] += 1

    def show_error(self, error_message):
        QMessageBox.critical(self, "错误", 'Api输入有误，请核对你的Api是否正确，或确认接入该模型的Api服务已开启')  # 显示错误消息

    def create_two(self):
        # 创建 QFrame
        two = QFrame(self)
        two.setStyleSheet("""
            QFrame {
                border: none;
            }
            QTextEdit {
                border: 1.5px solid rgba(224, 224, 224, 0.9);  
            }
        """)

        # 创建一个垂直布局
        layout = QVBoxLayout(two)

        # 创建标签
        above_text = QLabel(two)
        above_text.setText('识别结果:')
        above_text.move(50, 50)  # 移动标签到指定位置
        above_text.setStyleSheet("border: none; ")
        font = QFont('SimSun', 14, QFont.Bold)  # 设置字体为Arial，大小为14，加粗
        above_text.setFont(font)
        above_text.setAlignment(Qt.AlignLeft | Qt.AlignTop)  # 设置对齐方式
        layout.addWidget(above_text)

        # 创建文本框（QTextEdit）
        self.text_box = QTextEdit()
        self.text_box.setPlaceholderText("识别内容")  # 设置文本框的占位符文本
        layout.addWidget(self.text_box)

        child_layout1 = QHBoxLayout(two)
        btn1 = QPushButton('加[]')
        btn2 = QPushButton('加()')
        btn3 = QPushButton('去[]')
        btn4 = QPushButton('去()')
        btn5 = QPushButton('加\\text{}')
        child_layout1.addWidget(btn1)
        child_layout1.addWidget(btn2)
        child_layout1.addWidget(btn3)
        child_layout1.addWidget(btn4)
        child_layout1.addWidget(btn5)
        layout.addLayout(child_layout1)

        # 设置布局到 QFrame
        two.setLayout(layout)

        # 绑定
        self.text_box.textChanged.connect(self.on_output_text)
        btn1.clicked.connect(self.btn1_method)
        btn2.clicked.connect(self.btn2_method)
        btn3.clicked.connect(self.btn3_method)
        btn4.clicked.connect(self.btn4_method)
        btn5.clicked.connect(self.btn5_method)
        return two

    def btn1_method(self):
        if self.output_result:
            final_text = '\[' + self.output_result + '\]'
            self.text_box.setPlainText(final_text)
    
    def btn2_method(self):
        if self.output_result:
            final_text = '\(' + self.output_result + '\)'
            self.text_box.setPlainText(final_text)
    
    def btn3_method(self):
        if self.output_result:
            final_text = self.output_result.replace('\[', '').replace('\]', '').replace("\n", "", 1).rstrip("\n")
            self.text_box.setPlainText(final_text)
    
    def btn4_method(self):
        if self.output_result:
            final_text = self.output_result.replace('\(', '').replace('\)', '').replace("\n", "", 1).rstrip("\n")
            self.text_box.setPlainText(final_text)
    
    def btn5_method(self):
        if self.output_result:
            final_text = self.output_result
            # 一步完成匹配和替换，无需循环
            final_text = re.sub(
                r'([\u4e00-\u9fff]+)',  # 匹配连续中文字符
                r'\\text{\1}',          # 替换为 \text{...}，注意双反斜杠
                final_text
            )
            
            self.text_box.setPlainText(final_text)

    def set_output(self, doubao_output):
        self.text_box.setPlainText(doubao_output)

    def on_output_text(self):
        self.output_result = self.text_box.toPlainText()

    def create_three(self):
        """ 创建包含图片浏览功能的QFrame """
        three = QFrame(self)
        three.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 white, stop:1 #f5f5f5);
                border-radius: 20px;
                border: 2px solid #e0e0e0;
            }
        """)


        # 创建水平布局
        third_layout = QHBoxLayout()

        # 上一页 & 下一页按钮
        previous_image = QPushButton('')
        next_image = QPushButton('')
        # 使用图标
        previous_image.setIcon(QIcon('icons/previous.png'))
        next_image.setIcon(QIcon('icons/next.png'))
        # 设置按钮的固定宽度和高度
        previous_image.setFixedSize(40, 150)
        next_image.setFixedSize(40, 150)

        middle_layout = QVBoxLayout()
        # 使用自定义的ImageViewer类
        self.image_show = ImageViewer('')  # 创建空的ImageViewer，之后动态加载图片
        sub_layer1 = QHBoxLayout()
        open_folder = QPushButton('打开图片文件夹')
        cur_filename = QLabel(f'当前图片: ')
        cur_filename.setStyleSheet('border: none; ')
        self.cur_filename = cur_filename  # 保存引用，方便后续更新文件名

        sub_layer1.addWidget(open_folder)
        sub_layer1.addWidget(cur_filename)
        middle_layout.addWidget(self.image_show)
        middle_layout.addLayout(sub_layer1)

        # 按钮功能绑定
        previous_image.clicked.connect(self.show_previous_image)
        self.previous_image_shortcut = QShortcut(QKeySequence(Qt.Key_A), self)
        self.previous_image_shortcut.activated.connect(self.show_previous_image) 

        next_image.clicked.connect(self.show_next_image)
        self.next_image_shortcut = QShortcut(QKeySequence(Qt.Key_D), self)
        self.next_image_shortcut.activated.connect(self.show_next_image) 

        open_folder.clicked.connect(self.open_folder)

        # 添加组件到布局
        third_layout.addWidget(previous_image)
        third_layout.addLayout(middle_layout)
        third_layout.addWidget(next_image)

        # 应用布局
        three.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        three.setLayout(third_layout)
        three.setFrameShape(QFrame.NoFrame)
        return three
    
    def show_previous_image(self):
        """ 显示上一张图片 """
        if self.image_list and self.current_index > 0:
            self.current_index -= 1
            self.update_image()

    def show_next_image(self):
        """ 显示下一张图片 """
        if self.image_list and self.current_index < len(self.image_list) - 1:
            self.current_index += 1
            self.update_image()
    
    def update_image(self):
        """ 更新图片显示 """
        if self.image_list:
            image_path = self.image_list[self.current_index]
            self.image_show.update_image(image_path)  # 更新现有的 ImageViewer
            cur_image_name = os.path.basename(image_path)
            self.cur_image_name = cur_image_name.split('.')[0]
            self.cur_filename.setText(f'当前图片: {cur_image_name}')
            index_dict = {'index': self.current_index}
            with open(self.index_path, 'w') as w_f:
                json.dump(index_dict, w_f)

    def open_folder(self):
        """ 打开文件夹选择对话框 """
        self.folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if self.folder:
            self.index_path = os.path.join(self.folder, 'index.json')
            if os.path.exists(self.index_path):
                with open(self.index_path, 'r') as f:
                    cur_index = json.load(f)
                    self.current_index = cur_index['index']
            else:
                self.current_index = 0  # 重置为第一张图片

            self.save_times_path = os.path.join(self.folder, 'save_times.json')
            if os.path.exists(self.save_times_path):
                with open(self.save_times_path, 'r') as f:
                    self.save_times_dict = json.load(f)
            else:
                self.save_times_dict = {}

            parent_path = os.path.dirname(self.folder)
            self.shot_folder = os.path.join(parent_path, 'label_images')
            self.label_folder = os.path.join(parent_path, 'labels')
            os.makedirs(self.shot_folder, exist_ok=True)
            os.makedirs(self.label_folder, exist_ok=True)

            self.image_list = [os.path.join(self.folder, f) for f in os.listdir(self.folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            self.update_image()

    def center_window(self):
        """设置窗口在屏幕中央，大小为屏幕的一部分"""
        screen = QDesktopWidget().screenGeometry()
        screen_width = screen.width()
        screen_height = screen.height()

        window_width = int(screen_width * 0.7)
        window_height = int(screen_height * 0.8)
        window_x = (screen_width - window_width) // 2
        window_y = (screen_height - window_height) // 2

        self.setGeometry(window_x, window_y, window_width, window_height)

class MyThread(QThread):
    def __init__(self, doubao, method, *args):
        super().__init__()
        self.reply = doubao
        self.method = method
        self.args = args

    def run(self):
        getattr(self.reply, self.method)(*self.args)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")
    # 显示主窗口
    window = MyApp()
    window.show()

    sys.exit(app.exec_())
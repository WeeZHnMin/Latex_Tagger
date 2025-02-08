import re
import sys
from PyQt5.QtWidgets import QApplication, QFormLayout, QComboBox, QShortcut, QFileDialog, QSizePolicy, QLineEdit, QHBoxLayout, QWidget, QVBoxLayout, QFrame, QLabel, QPushButton, QDesktopWidget, QTextEdit
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

        self.current_model = None
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
        # 设置窗口标题和图标
        self.setWindowTitle("Latex标签器")
        self.setWindowIcon(QIcon('icons/logo.ico'))

        main_layout = QHBoxLayout()

        # 创建并设置第一个布局
        row_one_layout = QVBoxLayout()
        row_one_layout.addWidget(self.create_one())
        row_one_layout.addWidget(self.create_two())

        # 创建带样式的背景框架并设置布局
        backgroud_frame1 = QFrame()
        backgroud_frame1.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 white, stop:1 #f5f5f5);
                border-radius: 20px;
                border: 2px solid #e0e0e0;
            }
        """)
        backgroud_frame1.setLayout(row_one_layout)

        # 将背景框架添加到主布局
        main_layout.addWidget(backgroud_frame1)

        # 创建并添加第三个布局
        three_layout = self.create_three()
        main_layout.addWidget(three_layout)

        # 设置布局的伸缩因子
        main_layout.setStretch(0, 3)  # 第一个子布局的伸缩因子
        main_layout.setStretch(1, 7)  # 第二个子布局的伸缩因子

        # 设置主布局
        self.setLayout(main_layout)


    def create_one(self):
        one = QFrame(self)
        one.setStyleSheet('''QFrame { border: none; } QGraphicsView { border: 1.5px solid rgba(224, 224, 224, 0.9); }''')

        # 主布局
        main_layout = QVBoxLayout()

        # 子布局
        child_layout1 = QHBoxLayout()  # 按钮布局
        child_layout2 = QHBoxLayout()  # 模型选择和连接布局
        child_layout3 = QHBoxLayout()  # 输入内容布局
        child_layout4 = QHBoxLayout()  
        child_layout5 = QHBoxLayout()  

        # 创建按钮
        sc_btn = QPushButton('截图(W)(按下S选中)')
        sub_btn = QPushButton('识别(Ctrl+Space)')
        save_btn = QPushButton('保存(Ctrl+S)')

        # 创建模型选择控件
        clarification1 = QLabel('模型选择: ')
        clarification1.setStyleSheet('border: none; ')
        clarification1.setAlignment(Qt.AlignCenter)
        self.model_cb = QComboBox()
        self.model_cb.addItems(['Doubao-vision-lite-32k', 'Doubao-vision-pro-32k', 'Doubao-1.5-vision-pro-32k', '通义千问2.5-VL-72B', "Kimi"])
        check_connect = QPushButton('测试连接(Enter)')

        # 创建API Key 输入框
        api_clarication = QLabel('API Key:')
        self.api_input = QLineEdit()
        self.api_input.setPlaceholderText('输入模型的API Key')
        self.api_input.textChanged.connect(self.on_api_key)

        # ID输入
        modeiId_clarication = QLabel('Model Id(仅豆包需要):')
        self.model_id = QLineEdit()
        self.model_id.setPlaceholderText('输入Model id,如果不懂请看项目的使用说明')

        # 创建输入提示框
        clarification2 = QLabel('输入内容: ')
        clarification2.setStyleSheet("border: none; ")
        clarification2.setAlignment(Qt.AlignCenter)
        self.input_text = QLineEdit()
        self.input_text.setPlaceholderText('请在这里输入你的提示词')

        # 布局添加部件
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

        child_layout5.addWidget(modeiId_clarication)
        child_layout5.addWidget(self.model_id)

        # 显示截图
        self.my_shot = MyGraphicsView()

        # 将子布局添加到主布局
        main_layout.addLayout(child_layout2)
        main_layout.addLayout(child_layout3)
        main_layout.addLayout(child_layout4)
        main_layout.addLayout(child_layout5)
        main_layout.addLayout(child_layout1)
        main_layout.addWidget(self.my_shot)

        # 设置主框架
        one.setLayout(main_layout)
        one.setFrameShape(QFrame.NoFrame)

        # 绑定按钮和快捷键
        sc_btn.clicked.connect(self.take_screenshot)
        self.shot_shortcut = QShortcut(QKeySequence(Qt.Key_W), self)
        self.shot_shortcut.activated.connect(self.take_screenshot)

        self.model_cb.currentIndexChanged.connect(self.selectionchange)
        self.input_text.textChanged.connect(self.on_text_changed)
        self.model_id.textChanged.connect(self.on_modelId)

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

    def on_modelId(self):
        '''监听并更新输入的Model id'''
        self.current_model = self.model_id.text()
        print(f'当前model if为{self.current_model}')
    
    def on_api_key(self):
        '''监听并更新输入的API Key'''
        self.current_api = self.api_input.text()
    
    def on_save(self):
        '''保存截图和识别文本'''
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
        model_map = {'Doubao-vision-lite-32k': None, 'Doubao-1.5-vision-pro-32k': None, 'Doubao-vision-pro-32k': None, "通义千问2.5-VL-72B": "qwen-vl-plus", "Kimi": "moonshot-v1-8k-vision-preview"}
        if 'Doubao' in self.model_cb.currentText():
            self.current_model = self.model_id.text()
        else:
            self.current_model = model_map[self.model_cb.currentText()]

    def on_text_changed(self):
        '''监听输入的提示词(你的输入文字内容)'''
        self.my_text = self.input_text.text()
    
    def test_connect(self):
        """测试连接功能的实现"""
        if self.current_model and self.current_api and self.my_text:
            self.reply = Access(self.current_api, self.current_model)
            self.reply.return_str.connect(self.set_output)
            self.reply.error_occurred.connect(self.show_error)  # 连接错误信号
            self.thread = MyThread(self.reply, 'access_test', self.my_text)
            self.thread.start()

    def connect(self):
        """识别图像的功能实现"""
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
        QMessageBox.critical(self, "错误", f'Api输入有误，请核对你的Api是否正确以及输入的对应模型ID,错误: \n{error_message}')  # 显示错误消息

    def create_two(self):
        # 创建 QFrame 并设置样式
        two = QFrame(self)
        two.setStyleSheet("""
            QFrame { border: none; }
            QTextEdit { border: 1.5px solid rgba(224, 224, 224, 0.9); }
        """)

        # 创建垂直布局
        layout = QVBoxLayout(two)

        # 创建并设置标签
        above_text = QLabel(two)
        above_text.setText('识别结果:')
        above_text.setStyleSheet("border: none; ")
        above_text.setFont(QFont('SimSun', 14, QFont.Bold))  # 设置字体
        above_text.setAlignment(Qt.AlignLeft | Qt.AlignTop)  # 设置对齐方式
        layout.addWidget(above_text)

        # 创建文本框并设置占位符
        self.text_box = QTextEdit()
        self.text_box.setPlaceholderText("识别内容")
        layout.addWidget(self.text_box)

        # 创建按钮布局并添加按钮
        child_layout1 = QHBoxLayout(two)
        child_layout2 = QHBoxLayout(two)
        buttons = [
            ('加[]', self.btn1_method),
            ('加()', self.btn2_method),
            ('去[]', self.btn3_method),
            ('去()', self.btn4_method),
            ('加\\text{}', self.btn5_method),
            ('加$', self.btn6_method),
            ('去$', self.btn7_method),
        ]
        
        for btn_text, method in buttons[:4]:
            button = QPushButton(btn_text)
            button.clicked.connect(method)
            child_layout1.addWidget(button)
        for btn_text, method in buttons[4:]:
            button = QPushButton(btn_text)
            button.clicked.connect(method)
            child_layout2.addWidget(button)

        # 将按钮布局添加到主布局
        layout.addLayout(child_layout1)
        layout.addLayout(child_layout2)

        # 设置布局到 QFrame
        two.setLayout(layout)

        # 绑定文本框的事件
        self.text_box.textChanged.connect(self.on_output_text)

        return two

    def btn1_method(self):
        '''加\[\]功能的实现'''
        if self.output_result:
            final_text = '\[' + self.output_result + '\]'
            self.text_box.setPlainText(final_text)
    
    def btn2_method(self):
        '''加\(\)功能的实现'''
        if self.output_result:
            final_text = '\(' + self.output_result + '\)'
            self.text_box.setPlainText(final_text)
    
    def btn3_method(self):
        '''去\[\]功能的实现'''
        if self.output_result:
            final_text = self.output_result.replace('\[', '').replace('\]', '').replace("\n", "", 1).rstrip("\n")
            self.text_box.setPlainText(final_text)
    
    def btn4_method(self):
        '''去\(\)功能的实现'''
        if self.output_result:
            final_text = self.output_result.replace('\(', '').replace('\)', '').replace("\n", "", 1).rstrip("\n")
            self.text_box.setPlainText(final_text)
    
    def btn5_method(self):
        """用\\text{}包裹中文内容，在部分识别中，没有\\text{}包裹的话Latex文本会出错"""
        if self.output_result:
            final_text = self.output_result
            final_text = re.sub(
                r'([\u4e00-\u9fff]+)',  
                r'\\text{\1}',          
                final_text
            )
            
            self.text_box.setPlainText(final_text)
    
    def btn6_method(self):
        '''用$符号包裹公式'''
        if self.output_result:
            final_text = '$' + self.output_result + '$'
            self.text_box.setPlainText(final_text)
    
    def btn7_method(self):
        '''去$符号的实现'''
        if self.output_result:
            final_text = self.output_result.replace('$', '').replace('$', '').replace("\n", "", 1).rstrip("\n")
            self.text_box.setPlainText(final_text)

    def set_output(self, model_output):
        """实时更新“识别内容”"""
        self.text_box.setPlainText(model_output)

    def on_output_text(self):
        """实时读取“识别内容”"""
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
        previous_image.setIcon(QIcon('icons/previous.png'))
        next_image.setIcon(QIcon('icons/next.png'))
        previous_image.setFixedSize(40, 150)
        next_image.setFixedSize(40, 150)

        # 中间部分布局
        middle_layout = QVBoxLayout()
        self.image_show = ImageViewer('')  # 创建空的ImageViewer，动态加载图片

        # 子布局 - 文件夹选择和当前图片显示
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

        # 设置框架大小和布局
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
        if not self.image_list:
            return  # 如果图片列表为空，直接返回

        # 获取当前图片路径并更新显示
        image_path = self.image_list[self.current_index]
        self.image_show.update_image(image_path)  # 更新现有的 ImageViewer

        # 获取图片名称并更新显示的文件名
        cur_image_name = os.path.basename(image_path)
        self.cur_image_name = cur_image_name.split('.')[0]
        self.cur_filename.setText(f'当前图片: {cur_image_name}')

        # 更新索引到文件
        index_dict = {'index': self.current_index}
        with open(self.index_path, 'w') as w_f:
            json.dump(index_dict, w_f)

    def open_folder(self):
        """ 打开文件夹选择对话框 """
        self.folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if not self.folder:
            return  # 如果未选择文件夹，则直接返回

        # 设置索引路径并加载当前索引
        self.index_path = os.path.join(self.folder, 'index.json')
        self.current_index = 0  # 默认重置为第一张图片
        if os.path.exists(self.index_path):
            with open(self.index_path, 'r') as f:
                self.current_index = json.load(f).get('index', 0)

        # 设置保存次数路径并加载保存次数
        self.save_times_path = os.path.join(self.folder, 'save_times.json')
        if os.path.exists(self.save_times_path):
            with open(self.save_times_path, 'r') as f:
                self.save_times_dict = json.load(f)
        else:
            self.save_times_dict = {}

        # 创建文件夹路径
        parent_path = os.path.dirname(self.folder)
        self.shot_folder = os.path.join(parent_path, 'label_images')
        self.label_folder = os.path.join(parent_path, 'labels')
        os.makedirs(self.shot_folder, exist_ok=True)
        os.makedirs(self.label_folder, exist_ok=True)

        # 获取图片列表并更新显示
        self.image_list = [
            os.path.join(self.folder, f) 
            for f in os.listdir(self.folder) 
            if f.lower().endswith(('.png', '.jpg', '.jpeg'))
        ]
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
    '''多线程并发连接模型'''
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
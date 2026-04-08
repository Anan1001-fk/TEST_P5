import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# 模拟示波器连接和测量类
class MockKesightOscilloscope:
    """模拟Kesight示波器连接的类，用于演示"""

    def __init__(self, address="TCPIP0::192.168.1.100::inst0::INSTR"):
        self.address = address
        self.connected = False
        self.sampling_rate = 10e9  # 10 GHz
        self.record_length = 10000

    def connect(self):
        """模拟连接示波器"""
        print(f"Connecting to oscilloscope at {self.address}...")
        self.connected = True
        return True

    def disconnect(self):
        """模拟断开连接"""
        print("Disconnecting from oscilloscope...")
        self.connected = False

    def is_connected(self):
        """检查连接状态"""
        return self.connected

    def measure_eye_diagram(self, channel=1, duration=1e-6):
        """模拟测量眼图"""
        if not self.connected:
            return None, None, None

        print(f"Measuring eye diagram on channel {channel}...")

        # 生成模拟数据
        time = np.linspace(0, duration, int(self.sampling_rate * duration))

        # 模拟NRZ信号
        bit_rate = 5e9  # 5 Gbps
        bits = np.random.randint(0, 2, int(bit_rate * duration))

        # 创建信号
        signal = np.zeros_like(time)
        for i, bit in enumerate(bits):
            start_idx = int(i * len(time) / len(bits))
            end_idx = int((i + 1) * len(time) / len(bits))
            signal[start_idx:end_idx] = bit

        # 添加噪声和抖动
        noise = np.random.normal(0, 0.05, len(signal))
        jitter = np.random.normal(0, 0.01 * duration, len(signal))
        time_jittered = time + jitter

        # 计算眼图相关参数
        eye_height = 0.9 - 0.05 * np.random.random()
        eye_width = 0.95 / bit_rate - 0.05 * np.random.random() / bit_rate
        eye_closure = np.random.random() * 0.1

        return time_jittered, signal + noise, {
            'eye_height': eye_height,
            'eye_width': eye_width,
            'eye_closure': eye_closure,
            'bit_rate': bit_rate,
            'amplitude': 1.0
        }

    def measure_jitter(self, channel=1, duration=10e-6):
        """模拟测量抖动"""
        if not self.connected:
            return None, None, None

        print(f"Measuring jitter on channel {channel}...")

        # 生成模拟数据
        time = np.linspace(0, duration, int(self.sampling_rate * duration))

        # 模拟时钟信号
        clock_freq = 2.5e9  # 2.5 GHz
        ideal_clock = 0.5 * (1 + np.sign(np.sin(2 * np.pi * clock_freq * time)))

        # 添加抖动
        tj_rms = 5e-12  # 5 ps RMS
        tj_pp = 25e-12  # 25 ps peak-to-peak
        deterministic_jitter = 2e-12 * np.sin(2 * np.pi * 1e6 * time)  # 1 MHz周期性抖动
        random_jitter = np.random.normal(0, tj_rms, len(time))

        total_jitter = deterministic_jitter + random_jitter
        jittered_clock = 0.5 * (1 + np.sign(np.sin(2 * np.pi * clock_freq * (time + total_jitter))))

        # 计算抖动参数
        tj_rms_measured = np.std(total_jitter)
        tj_pp_measured = np.max(total_jitter) - np.min(total_jitter)
        dj_measured = np.max(deterministic_jitter) - np.min(deterministic_jitter)
        rj_measured = np.std(random_jitter)

        return time, jittered_clock, {
            'tj_rms': tj_rms_measured,
            'tj_pp': tj_pp_measured,
            'dj': dj_measured,
            'rj': rj_measured,
            'frequency': clock_freq
        }


# 主应用窗口
class KesightAutomationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.oscilloscope = MockKesightOscilloscope()
        self.test_results = []
        self.init_ui()

    def init_ui(self):
        """初始化UI界面"""
        self.setWindowTitle("Kesight示波器自动化测试系统")
        self.setGeometry(100, 100, 1200, 800)

        # 设置应用图标
        self.setWindowIcon(QIcon(self.create_icon()))

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        main_layout = QVBoxLayout(central_widget)

        # 创建菜单栏
        self.create_menu_bar()

        # 创建工具栏
        self.create_toolbar()

        # 创建状态栏
        self.statusBar().showMessage("就绪")

        # 创建标签页
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # 添加连接控制标签页
        self.create_connection_tab()

        # 添加眼图测试标签页
        self.create_eye_diagram_tab()

        # 添加抖动测试标签页
        self.create_jitter_tab()

        # 添加结果显示标签页
        self.create_results_tab()

        # 添加关于标签页
        self.create_about_tab()

    def create_icon(self):
        """创建应用图标"""
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制示波器图标
        painter.setPen(QPen(Qt.blue, 2))
        painter.drawRect(4, 4, 24, 24)

        # 绘制波形
        painter.setPen(QPen(Qt.red, 2))
        points = [
            QPoint(6, 20), QPoint(10, 10), QPoint(14, 25),
            QPoint(18, 8), QPoint(22, 15), QPoint(26, 20)
        ]
        for i in range(len(points) - 1):
            painter.drawLine(points[i], points[i + 1])

        painter.end()
        return pixmap

    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu('文件')

        export_action = QAction('导出测试结果', self)
        export_action.setShortcut('Ctrl+E')
        export_action.triggered.connect(self.export_results)
        file_menu.addAction(export_action)

        save_action = QAction('保存配置', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_configuration)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction('退出', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 测试菜单
        test_menu = menubar.addMenu('测试')

        run_eye_test_action = QAction('运行眼图测试', self)
        run_eye_test_action.setShortcut('F5')
        run_eye_test_action.triggered.connect(self.run_eye_diagram_test)
        test_menu.addAction(run_eye_test_action)

        run_jitter_test_action = QAction('运行抖动测试', self)
        run_jitter_test_action.setShortcut('F6')
        run_jitter_test_action.triggered.connect(self.run_jitter_test)
        test_menu.addAction(run_jitter_test_action)

        # 工具菜单
        tools_menu = menubar.addMenu('工具')

        connect_action = QAction('连接示波器', self)
        connect_action.triggered.connect(self.connect_oscilloscope)
        tools_menu.addAction(connect_action)

        disconnect_action = QAction('断开连接', self)
        disconnect_action.triggered.connect(self.disconnect_oscilloscope)
        tools_menu.addAction(disconnect_action)

        # 帮助菜单
        help_menu = menubar.addMenu('帮助')

        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        """创建工具栏"""
        toolbar = self.addToolBar('工具')
        toolbar.setMovable(False)

        # 连接按钮
        connect_btn = QAction(QIcon.fromTheme('network-connect'), '连接示波器', self)
        connect_btn.triggered.connect(self.connect_oscilloscope)
        toolbar.addAction(connect_btn)

        # 断开按钮
        disconnect_btn = QAction(QIcon.fromTheme('network-disconnect'), '断开连接', self)
        disconnect_btn.triggered.connect(self.disconnect_oscilloscope)
        toolbar.addAction(disconnect_btn)

        toolbar.addSeparator()

        # 眼图测试按钮
        eye_test_btn = QAction(QIcon.fromTheme('view-statistics'), '眼图测试', self)
        eye_test_btn.triggered.connect(self.run_eye_diagram_test)
        toolbar.addAction(eye_test_btn)

        # 抖动测试按钮
        jitter_test_btn = QAction(QIcon.fromTheme('view-history'), '抖动测试', self)
        jitter_test_btn.triggered.connect(self.run_jitter_test)
        toolbar.addAction(jitter_test_btn)

        toolbar.addSeparator()

        # 导出按钮
        export_btn = QAction(QIcon.fromTheme('document-export'), '导出结果', self)
        export_btn.triggered.connect(self.export_results)
        toolbar.addAction(export_btn)

    def create_connection_tab(self):
        """创建连接控制标签页"""
        connection_tab = QWidget()
        layout = QVBoxLayout(connection_tab)

        # 连接状态组
        status_group = QGroupBox("连接状态")
        status_layout = QVBoxLayout()

        self.connection_status_label = QLabel("状态: 未连接")
        self.connection_status_label.setStyleSheet("font-weight: bold; color: red;")
        status_layout.addWidget(self.connection_status_label)

        self.oscilloscope_address_label = QLabel("示波器地址: 未设置")
        status_layout.addWidget(self.oscilloscope_address_label)

        # 连接控制
        control_layout = QHBoxLayout()

        address_label = QLabel("示波器地址:")
        self.address_input = QLineEdit("TCPIP0::192.168.1.100::inst0::INSTR")
        self.address_input.setPlaceholderText("输入示波器地址")

        connect_btn = QPushButton("连接")
        connect_btn.clicked.connect(self.connect_oscilloscope)

        disconnect_btn = QPushButton("断开连接")
        disconnect_btn.clicked.connect(self.disconnect_oscilloscope)

        control_layout.addWidget(address_label)
        control_layout.addWidget(self.address_input)
        control_layout.addWidget(connect_btn)
        control_layout.addWidget(disconnect_btn)

        status_layout.addLayout(control_layout)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # 设备信息组
        info_group = QGroupBox("设备信息")
        info_layout = QFormLayout()

        self.device_model_label = QLabel("未知")
        self.device_serial_label = QLabel("未知")
        self.device_firmware_label = QLabel("未知")

        info_layout.addRow("设备型号:", self.device_model_label)
        info_layout.addRow("序列号:", self.device_serial_label)
        info_layout.addRow("固件版本:", self.device_firmware_label)

        refresh_btn = QPushButton("刷新设备信息")
        refresh_btn.clicked.connect(self.refresh_device_info)
        info_layout.addRow("", refresh_btn)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        layout.addStretch()
        self.tab_widget.addTab(connection_tab, "连接控制")

    def create_eye_diagram_tab(self):
        """创建眼图测试标签页"""
        eye_tab = QWidget()
        layout = QVBoxLayout(eye_tab)

        # 测试参数组
        params_group = QGroupBox("测试参数")
        params_layout = QFormLayout()

        self.eye_channel_input = QSpinBox()
        self.eye_channel_input.setRange(1, 4)
        self.eye_channel_input.setValue(1)

        self.eye_datarate_input = QDoubleSpinBox()
        self.eye_datarate_input.setRange(0.1, 113)
        self.eye_datarate_input.setValue(8)
        self.eye_datarate_input.setSuffix(" Gbps")
        self.eye_datarate_input.setSingleStep(1)

        self.eye_bitrate_input = QDoubleSpinBox()
        self.eye_bitrate_input.setRange(0.1, 100)
        self.eye_bitrate_input.setValue(5)
        self.eye_bitrate_input.setSuffix(" Gbps")
        self.eye_bitrate_input.setSingleStep(0.1)

        params_layout.addRow("通道:", self.eye_channel_input)
        params_layout.addRow("测试速率:", self.eye_datarate_input)
        params_layout.addRow("预期比特率:", self.eye_bitrate_input)

        # 测试控制
        test_control_layout = QHBoxLayout()
        self.run_eye_test_btn = QPushButton("运行眼图测试")
        self.run_eye_test_btn.clicked.connect(self.run_eye_diagram_test)
        self.run_eye_test_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")

        self.save_eye_results_btn = QPushButton("保存结果")
        self.save_eye_results_btn.clicked.connect(lambda: self.save_test_results("eye"))
        self.save_eye_results_btn.setEnabled(False)

        test_control_layout.addWidget(self.run_eye_test_btn)
        test_control_layout.addWidget(self.save_eye_results_btn)
        test_control_layout.addStretch()

        params_layout.addRow("", test_control_layout)
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)

        # 结果组
        results_group = QGroupBox("测试结果")
        results_layout = QVBoxLayout()

        # 创建matplotlib图形
        self.eye_figure = Figure(figsize=(8, 4))
        self.eye_canvas = FigureCanvas(self.eye_figure)
        results_layout.addWidget(self.eye_canvas)

        # 参数显示
        self.eye_results_text = QTextEdit()
        self.eye_results_text.setMaximumHeight(100)
        self.eye_results_text.setReadOnly(True)
        results_layout.addWidget(self.eye_results_text)

        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        self.tab_widget.addTab(eye_tab, "眼图测试")

    def create_jitter_tab(self):
        """创建抖动测试标签页"""
        jitter_tab = QWidget()
        layout = QVBoxLayout(jitter_tab)

        # 测试参数组
        params_group = QGroupBox("测试参数")
        params_layout = QFormLayout()

        self.jitter_channel_input = QSpinBox()
        self.jitter_channel_input.setRange(1, 4)
        self.jitter_channel_input.setValue(1)

        self.jitter_duration_input = QDoubleSpinBox()
        self.jitter_duration_input.setRange(1, 10000)
        self.jitter_duration_input.setValue(100)
        self.jitter_duration_input.setSuffix(" μs")
        self.jitter_duration_input.setSingleStep(10)

        self.jitter_frequency_input = QDoubleSpinBox()
        self.jitter_frequency_input.setRange(0.1, 50)
        self.jitter_frequency_input.setValue(2.5)
        self.jitter_frequency_input.setSuffix(" GHz")
        self.jitter_frequency_input.setSingleStep(0.1)

        params_layout.addRow("通道:", self.jitter_channel_input)
        params_layout.addRow("测试时长:", self.jitter_duration_input)
        params_layout.addRow("预期频率:", self.jitter_frequency_input)

        # 测试控制
        test_control_layout = QHBoxLayout()
        self.run_jitter_test_btn = QPushButton("运行抖动测试")
        self.run_jitter_test_btn.clicked.connect(self.run_jitter_test)
        self.run_jitter_test_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")

        self.save_jitter_results_btn = QPushButton("保存结果")
        self.save_jitter_results_btn.clicked.connect(lambda: self.save_test_results("jitter"))
        self.save_jitter_results_btn.setEnabled(False)

        test_control_layout.addWidget(self.run_jitter_test_btn)
        test_control_layout.addWidget(self.save_jitter_results_btn)
        test_control_layout.addStretch()

        params_layout.addRow("", test_control_layout)
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)

        # 结果组
        results_group = QGroupBox("测试结果")
        results_layout = QVBoxLayout()

        # 创建matplotlib图形
        self.jitter_figure = Figure(figsize=(8, 4))
        self.jitter_canvas = FigureCanvas(self.jitter_figure)
        results_layout.addWidget(self.jitter_canvas)

        # 参数显示
        self.jitter_results_text = QTextEdit()
        self.jitter_results_text.setMaximumHeight(100)
        self.jitter_results_text.setReadOnly(True)
        results_layout.addWidget(self.jitter_results_text)

        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        self.tab_widget.addTab(jitter_tab, "抖动测试")

    def create_results_tab(self):
        """创建结果显示标签页"""
        results_tab = QWidget()
        layout = QVBoxLayout(results_tab)

        # 结果表
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(7)
        self.results_table.setHorizontalHeaderLabels([
            "测试时间", "测试类型", "通道", "状态", "眼高", "眼宽", "总抖动"
        ])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.results_table)

        # 结果操作按钮
        button_layout = QHBoxLayout()

        clear_results_btn = QPushButton("清除结果")
        clear_results_btn.clicked.connect(self.clear_results)

        export_results_btn = QPushButton("导出到Excel")
        export_results_btn.clicked.connect(self.export_results)

        button_layout.addWidget(clear_results_btn)
        button_layout.addWidget(export_results_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        self.tab_widget.addTab(results_tab, "测试结果")

    def create_about_tab(self):
        """创建关于标签页"""
        about_tab = QWidget()
        layout = QVBoxLayout(about_tab)

        # 应用信息
        info_group = QGroupBox("应用信息")
        info_layout = QVBoxLayout()

        app_name = QLabel("Kesight示波器自动化测试系统")
        app_name.setStyleSheet("font-size: 18px; font-weight: bold;")

        app_version = QLabel("版本: 1.0.0")
        app_description = QLabel("""
        该应用用于自动化执行Kesight示波器的眼图测试和抖动测试，
        并将测试结果保存到Excel文件中。

        功能特性:
        • 连接和控制Kesight示波器
        • 执行眼图测试并显示结果
        • 执行抖动测试并显示结果
        • 保存测试结果到Excel
        • 查看历史测试记录
        """)

        info_layout.addWidget(app_name)
        info_layout.addWidget(app_version)
        info_layout.addWidget(app_description)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # 系统信息
        sys_group = QGroupBox("系统信息")
        sys_layout = QFormLayout()

        python_version = QLabel(f"{sys.version}")
        qt_version = QLabel(f"{PYQT_VERSION_STR}")
        pandas_version = QLabel(f"{pd.__version__}")

        sys_layout.addRow("Python版本:", python_version)
        sys_layout.addRow("PyQt5版本:", qt_version)
        sys_layout.addRow("Pandas版本:", pandas_version)

        sys_group.setLayout(sys_layout)
        layout.addWidget(sys_group)

        layout.addStretch()

        self.tab_widget.addTab(about_tab, "关于")

    def connect_oscilloscope(self):
        """连接示波器"""
        address = self.address_input.text()
        if not address:
            QMessageBox.warning(self, "警告", "请输入示波器地址")
            return

        self.oscilloscope.address = address

        # 模拟连接
        success = self.oscilloscope.connect()

        if success:
            self.connection_status_label.setText("状态: 已连接")
            self.connection_status_label.setStyleSheet("font-weight: bold; color: green;")
            self.oscilloscope_address_label.setText(f"示波器地址: {address}")
            self.statusBar().showMessage(f"已连接到示波器: {address}", 5000)

            # 更新设备信息
            self.device_model_label.setText("Kesight DSOX1102G")
            self.device_serial_label.setText("MY12345678")
            self.device_firmware_label.setText("2.41")
        else:
            QMessageBox.critical(self, "错误", "无法连接到示波器")

    def disconnect_oscilloscope(self):
        """断开示波器连接"""
        self.oscilloscope.disconnect()
        self.connection_status_label.setText("状态: 未连接")
        self.connection_status_label.setStyleSheet("font-weight: bold; color: red;")
        self.statusBar().showMessage("已断开示波器连接", 5000)

    def refresh_device_info(self):
        """刷新设备信息"""
        if self.oscilloscope.is_connected():
            self.statusBar().showMessage("设备信息已刷新", 3000)
        else:
            QMessageBox.warning(self, "警告", "请先连接示波器")

    def run_eye_diagram_test(self):
        """运行眼图测试"""
        if not self.oscilloscope.is_connected():
            QMessageBox.warning(self, "警告", "请先连接示波器")
            return

        self.statusBar().showMessage("正在进行眼图测试...")

        # 获取测试参数
        channel = self.eye_channel_input.value()
        duration = self.eye_duration_input.value() * 1e-6  # 转换为秒

        # 运行测试
        time, signal, results = self.oscilloscope.measure_eye_diagram(channel, duration)

        if time is not None and signal is not None and results is not None:
            # 更新图表
            self.eye_figure.clear()
            ax = self.eye_figure.add_subplot(111)

            # 显示信号
            ax.plot(time * 1e6, signal, 'b-', alpha=0.7, linewidth=0.5)
            ax.set_xlabel('时间 (μs)')
            ax.set_ylabel('幅度 (V)')
            ax.set_title('眼图测试结果')
            ax.grid(True, alpha=0.3)

            self.eye_canvas.draw()

            # 更新结果文本
            results_text = f"""
            眼图测试结果:
            • 眼高: {results['eye_height']:.4f} V
            • 眼宽: {results['eye_width'] * 1e12:.2f} ps
            • 眼闭合度: {results['eye_closure'] * 100:.2f} %
            • 比特率: {results['bit_rate'] * 1e-9:.2f} Gbps
            • 信号幅度: {results['amplitude']:.3f} V
            """
            self.eye_results_text.setText(results_text)

            # 启用保存按钮
            self.save_eye_results_btn.setEnabled(True)

            # 保存测试结果到内存
            test_result = {
                'timestamp': datetime.now(),
                'test_type': '眼图测试',
                'channel': channel,
                'status': '通过',
                'eye_height': results['eye_height'],
                'eye_width': results['eye_width'] * 1e12,  # 转换为ps
                'total_jitter': 'N/A',
                'raw_data': results
            }
            self.test_results.append(test_result)

            # 更新结果表
            self.update_results_table()

            self.statusBar().showMessage("眼图测试完成", 5000)
        else:
            QMessageBox.critical(self, "错误", "眼图测试失败")

    def run_jitter_test(self):
        """运行抖动测试"""
        if not self.oscilloscope.is_connected():
            QMessageBox.warning(self, "警告", "请先连接示波器")
            return

        self.statusBar().showMessage("正在进行抖动测试...")

        # 获取测试参数
        channel = self.jitter_channel_input.value()
        duration = self.jitter_duration_input.value() * 1e-6  # 转换为秒

        # 运行测试
        time, signal, results = self.oscilloscope.measure_jitter(channel, duration)

        if time is not None and signal is not None and results is not None:
            # 更新图表
            self.jitter_figure.clear()
            ax = self.jitter_figure.add_subplot(111)

            # 显示信号
            ax.plot(time[:1000] * 1e6, signal[:1000], 'r-', alpha=0.8, linewidth=1)
            ax.set_xlabel('时间 (μs)')
            ax.set_ylabel('幅度 (V)')
            ax.set_title('抖动测试结果 (前1000个采样点)')
            ax.grid(True, alpha=0.3)

            self.jitter_canvas.draw()

            # 更新结果文本
            results_text = f"""
            抖动测试结果:
            • 总抖动(RMS): {results['tj_rms'] * 1e12:.2f} ps
            • 总抖动(峰峰值): {results['tj_pp'] * 1e12:.2f} ps
            • 确定性抖动: {results['dj'] * 1e12:.2f} ps
            • 随机抖动: {results['rj'] * 1e12:.2f} ps
            • 时钟频率: {results['frequency'] * 1e-9:.2f} GHz
            """
            self.jitter_results_text.setText(results_text)

            # 启用保存按钮
            self.save_jitter_results_btn.setEnabled(True)

            # 保存测试结果到内存
            test_result = {
                'timestamp': datetime.now(),
                'test_type': '抖动测试',
                'channel': channel,
                'status': '通过',
                'eye_height': 'N/A',
                'eye_width': 'N/A',
                'total_jitter': results['tj_pp'] * 1e12,  # 转换为ps
                'raw_data': results
            }
            self.test_results.append(test_result)

            # 更新结果表
            self.update_results_table()

            self.statusBar().showMessage("抖动测试完成", 5000)
        else:
            QMessageBox.critical(self, "错误", "抖动测试失败")

    def update_results_table(self):
        """更新结果表格"""
        self.results_table.setRowCount(len(self.test_results))

        for i, result in enumerate(self.test_results):
            self.results_table.setItem(i, 0, QTableWidgetItem(result['timestamp'].strftime("%Y-%m-%d %H:%M:%S")))
            self.results_table.setItem(i, 1, QTableWidgetItem(result['test_type']))
            self.results_table.setItem(i, 2, QTableWidgetItem(str(result['channel'])))
            self.results_table.setItem(i, 3, QTableWidgetItem(result['status']))

            eye_height = result['eye_height'] if result['eye_height'] != 'N/A' else f"{result['eye_height']:.4f} V"
            eye_width = result['eye_width'] if result['eye_width'] != 'N/A' else f"{result['eye_width']:.2f} ps"
            total_jitter = result['total_jitter'] if result[
                                                         'total_jitter'] != 'N/A' else f"{result['total_jitter']:.2f} ps"

            self.results_table.setItem(i, 4, QTableWidgetItem(str(eye_height)))
            self.results_table.setItem(i, 5, QTableWidgetItem(str(eye_width)))
            self.results_table.setItem(i, 6, QTableWidgetItem(str(total_jitter)))

    def save_test_results(self, test_type):
        """保存测试结果到临时文件"""
        if not self.test_results:
            QMessageBox.warning(self, "警告", "没有测试结果可保存")
            return

        # 过滤指定类型的测试结果
        filtered_results = [r for r in self.test_results if test_type in r['test_type']]

        if not filtered_results:
            QMessageBox.warning(self, "警告", f"没有{test_type}测试结果可保存")
            return

        # 创建DataFrame
        df_data = []
        for result in filtered_results:
            row = {
                '测试时间': result['timestamp'],
                '测试类型': result['test_type'],
                '通道': result['channel'],
                '状态': result['status'],
            }

            if test_type == "eye":
                row['眼高(V)'] = result['eye_height']
                row['眼宽(ps)'] = result['eye_width']
                row['比特率(Gbps)'] = result['raw_data'].get('bit_rate', 0) * 1e-9
                row['信号幅度(V)'] = result['raw_data'].get('amplitude', 0)
            else:
                row['总抖动_RMS(ps)'] = result['raw_data'].get('tj_rms', 0) * 1e12
                row['总抖动_峰峰值(ps)'] = result['total_jitter']
                row['确定性抖动(ps)'] = result['raw_data'].get('dj', 0) * 1e12
                row['随机抖动(ps)'] = result['raw_data'].get('rj', 0) * 1e12
                row['时钟频率(GHz)'] = result['raw_data'].get('frequency', 0) * 1e-9

            df_data.append(row)

        df = pd.DataFrame(df_data)

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{test_type}_test_results_{timestamp}.xlsx"

        # 保存到Excel
        try:
            df.to_excel(filename, index=False)
            self.statusBar().showMessage(f"结果已保存到 {filename}", 5000)
            QMessageBox.information(self, "成功", f"测试结果已保存到 {filename}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")

    def export_results(self):
        """导出所有结果到Excel"""
        if not self.test_results:
            QMessageBox.warning(self, "警告", "没有测试结果可导出")
            return

        # 让用户选择保存位置
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(
            self, "保存测试结果", "",
            "Excel文件 (*.xlsx);;所有文件 (*)",
            options=options
        )

        if filename:
            if not filename.endswith('.xlsx'):
                filename += '.xlsx'

            # 创建DataFrame
            df_data = []
            for result in self.test_results:
                row = {
                    '测试时间': result['timestamp'],
                    '测试类型': result['test_type'],
                    '通道': result['channel'],
                    '状态': result['status'],
                }

                # 添加测试特定参数
                if 'eye' in result['test_type']:
                    row['眼高(V)'] = result['eye_height']
                    row['眼宽(ps)'] = result['eye_width']
                    row['眼闭合度(%)'] = result['raw_data'].get('eye_closure', 0) * 100
                    row['比特率(Gbps)'] = result['raw_data'].get('bit_rate', 0) * 1e-9
                else:
                    row['总抖动_RMS(ps)'] = result['raw_data'].get('tj_rms', 0) * 1e12
                    row['总抖动_峰峰值(ps)'] = result['total_jitter']
                    row['确定性抖动(ps)'] = result['raw_data'].get('dj', 0) * 1e12
                    row['随机抖动(ps)'] = result['raw_data'].get('rj', 0) * 1e12
                    row['时钟频率(GHz)'] = result['raw_data'].get('frequency', 0) * 1e-9

                df_data.append(row)

            df = pd.DataFrame(df_data)

            # 保存到Excel
            try:
                df.to_excel(filename, index=False)
                self.statusBar().showMessage(f"所有结果已导出到 {filename}", 5000)
                QMessageBox.information(self, "成功", f"测试结果已导出到 {filename}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")

    def clear_results(self):
        """清除所有结果"""
        reply = QMessageBox.question(
            self, '确认',
            '确定要清除所有测试结果吗？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.test_results.clear()
            self.results_table.setRowCount(0)
            self.statusBar().showMessage("已清除所有测试结果", 3000)

    def save_configuration(self):
        """保存配置"""
        QMessageBox.information(self, "信息", "配置保存功能正在开发中")

    def show_about(self):
        """显示关于对话框"""
        about_text = """
        <h2>Kesight示波器自动化测试系统</h2>
        <p>版本: 1.0.0</p>
        <p>该应用用于自动化执行Kesight示波器的测试，包括眼图测试和抖动测试。</p>
        <p>功能包括:</p>
        <ul>
          <li>连接和控制Kesight示波器</li>
          <li>执行眼图测试并显示结果</li>
          <li>执行抖动测试并显示结果</li>
          <li>保存测试结果到Excel文件</li>
          <li>查看历史测试记录</li>
        </ul>
        <p>© 2023 版权所有</p>
        """
        QMessageBox.about(self, "关于", about_text)


def main():
    """主函数"""
    app = QApplication(sys.argv)

    # 设置应用程序样式
    app.setStyle('Fusion')

    # 创建并显示主窗口
    window = KesightAutomationApp()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
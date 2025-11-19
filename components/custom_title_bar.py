#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义窗口标题栏组件
用于替代系统标题栏，可以定制尺寸和内容
"""

import os
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QLineEdit
from PySide6.QtCore import Qt, QSize, Signal, QTimer
from PySide6.QtGui import QIcon, QMouseEvent, QPainter, QColor, QPixmap


class CustomTitleBar(QWidget):
    """自定义窗口标题栏类"""
    
    # 定义信号：用于窗口控制
    minimize_clicked = Signal()
    maximize_clicked = Signal()
    close_clicked = Signal()
    search_text_changed = Signal(str)  # 搜索文本变化信号
    
    def __init__(self, parent=None, title: str = "Simond 保险箱", logo_path: str = None):
        super().__init__(parent)
        self.title = title
        self.logo_path = logo_path
        self._is_maximized = False
        
        # 初始化界面
        self.init_ui()
    
    def init_ui(self):
        """初始化标题栏界面"""
        # 设置标题栏高度（默认50像素，可自定义）
        self.setFixedHeight(50)
        
        # 设置背景色（使用系统颜色，顶部圆角12px）
        self.setStyleSheet("""
            CustomTitleBar {
                background-color: palette(window);
                border-bottom: 1px solid palette(mid);
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }
        """)
        
        # 创建水平布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)  # 设置边距（可自定义）
        layout.setSpacing(10)  # 设置间距（可自定义）
        
        # ========== 左侧区域：Logo和标题 ==========
        # 创建Logo标签
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(24, 24)  # 设置Logo大小
        self.logo_label.setScaledContents(True)  # 允许缩放内容
        self.set_logo(self.logo_path)  # 设置Logo
        layout.addWidget(self.logo_label)
        
        # 创建标题标签（使用系统文本颜色）
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #999999;
            }
        """)
        layout.addWidget(self.title_label)
        
        # ========== 搜索框区域 ==========
        # 创建搜索框容器（用于包含搜索框和图标）
        search_container = QWidget()
        search_container.setFixedHeight(32)
        search_container_layout = QHBoxLayout(search_container)
        search_container_layout.setContentsMargins(0, 0, 0, 0)
        search_container_layout.setSpacing(0)
        
        # 创建搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索应用、游戏等")
        self.search_input.setFixedHeight(32)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d30;
                border: none;
                border-radius: 6px;
                padding-left: 12px;
                padding-right: 32px;
                font-size: 13px;
                color: #cccccc;
            }
            QLineEdit:focus {
                background-color: #3d3d40;
                border: 1px solid #0078d4;
            }
            QLineEdit::placeholder {
                color: #808080;
            }
        """)
        self.search_input.textChanged.connect(self.search_text_changed.emit)
        search_container_layout.addWidget(self.search_input)
        
        # 创建搜索图标（放在搜索框内部右侧）
        self.search_icon_label = QLabel(self.search_input)
        self.search_icon_label.setFixedSize(16, 16)
        self.search_icon_label.setScaledContents(True)
        self.search_icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)  # 让鼠标事件穿透
        # 创建搜索图标（放大镜）
        search_pixmap = QPixmap(16, 16)
        search_pixmap.fill(Qt.GlobalColor.transparent)
        search_painter = QPainter(search_pixmap)
        search_painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        search_painter.setPen(QColor(128, 128, 128))
        search_painter.setBrush(Qt.BrushStyle.NoBrush)
        # 绘制放大镜
        search_painter.drawEllipse(2, 2, 8, 8)
        search_painter.drawLine(10, 10, 14, 14)
        search_painter.end()
        self.search_icon_label.setPixmap(search_pixmap)
        
        # 更新图标位置的函数
        def update_search_icon_position():
            if self.search_input:
                self.search_icon_label.move(self.search_input.width() - 20, 8)
        
        # 保存更新函数以便后续调用
        self._update_search_icon_position = update_search_icon_position
        
        # 初始定位
        self.search_input.resizeEvent = lambda e: (QLineEdit.resizeEvent(self.search_input, e), update_search_icon_position())
        # 延迟更新，确保搜索框已正确布局
        QTimer.singleShot(0, update_search_icon_position)
        
        # 将搜索框容器添加到主布局，设置最小宽度
        search_container.setMinimumWidth(300)
        layout.addWidget(search_container, 1)  # 设置拉伸因子为1，使其占据可用空间
        
        # 添加弹性空间，使右侧按钮靠右对齐
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(spacer)
        
        # ========== 右侧区域：窗口控制按钮 ==========
        # 最小化按钮（使用系统颜色）
        self.minimize_btn = QPushButton("−")
        self.minimize_btn.setFixedSize(30, 30)
        self.minimize_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 18px;
                color: palette(window-text);
            }
            QPushButton:hover {
                background-color: palette(button);
            }
        """)
        self.minimize_btn.clicked.connect(self.minimize_clicked.emit)
        layout.addWidget(self.minimize_btn)
        
        # 最大化/还原按钮（使用系统颜色）
        self.maximize_btn = QPushButton("□")
        self.maximize_btn.setFixedSize(30, 30)
        self.maximize_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 16px;
                color: palette(window-text);
            }
            QPushButton:hover {
                background-color: palette(button);
            }
        """)
        self.maximize_btn.clicked.connect(self.maximize_clicked.emit)
        layout.addWidget(self.maximize_btn)
        
        # 关闭按钮（使用系统颜色，悬停时使用红色）
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 20px;
                color: palette(window-text);
            }
            QPushButton:hover {
                background-color: #e81123;
                color: white;
            }
        """)
        self.close_btn.clicked.connect(self.close_clicked.emit)
        layout.addWidget(self.close_btn)
        
        # 保存鼠标按下位置，用于窗口拖动
        self._drag_position = None
    
    def set_title(self, title: str):
        """设置标题文本"""
        self.title = title
        self.title_label.setText(title)
    
    def set_bar_height(self, height: int):
        """设置标题栏高度"""
        self.setFixedHeight(height)
    
    def set_background_color(self, color: str):
        """设置背景颜色"""
        self.setStyleSheet(f"""
            CustomTitleBar {{
                background-color: {color};
                border-bottom: 1px solid #d0d0d0;
            }}
        """)
    
    def set_title_style(self, style: str):
        """设置标题样式（CSS样式字符串）"""
        self.title_label.setStyleSheet(style)
    
    def get_search_text(self) -> str:
        """获取搜索框中的文本"""
        return self.search_input.text() if hasattr(self, 'search_input') else ""
    
    def set_search_text(self, text: str):
        """设置搜索框中的文本"""
        if hasattr(self, 'search_input'):
            self.search_input.setText(text)
    
    def set_logo(self, logo_path: str = None):
        """设置Logo图标
        
        Args:
            logo_path: Logo图片文件路径。如果为None或文件不存在，则创建一个简单的占位符图标
        """
        if logo_path and os.path.exists(logo_path):
            # 从文件加载Logo
            pixmap = QPixmap(logo_path)
            self.logo_label.setPixmap(pixmap)
        else:
            # 创建一个简单的占位符Logo（蓝色圆角矩形）
            pixmap = QPixmap(24, 24)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(QColor(66, 133, 244))  # 蓝色
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(2, 2, 20, 20, 4, 4)  # 圆角矩形
            # 在矩形中心绘制一个简单的"S"字母
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(painter.font())
            font = painter.font()
            font.setBold(True)
            font.setPointSize(14)
            painter.setFont(font)
            painter.drawText(6, 18, "S")
            painter.end()
            self.logo_label.setPixmap(pixmap)
    
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件：用于窗口拖动"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件：拖动窗口"""
        if self._drag_position is not None:
            window = self.window()
            if window:
                delta = event.globalPosition().toPoint() - self._drag_position
                window.move(window.pos() + delta)
                self._drag_position = event.globalPosition().toPoint()
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件"""
        self._drag_position = None
        super().mouseReleaseEvent(event)
    
    def update_maximize_button(self, is_maximized: bool):
        """更新最大化按钮状态"""
        self._is_maximized = is_maximized
        if is_maximized:
            self.maximize_btn.setText("❐")  # 还原图标
        else:
            self.maximize_btn.setText("□")  # 最大化图标


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义窗口标题栏组件
用于替代系统标题栏，可以定制尺寸和内容
"""

import os
import re
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, 
    QSizePolicy, QLineEdit, QGraphicsDropShadowEffect, QApplication
)
from PySide6.QtCore import Qt, QSize, Signal, QTimer, QPoint
from PySide6.QtGui import QIcon, QMouseEvent, QPainter, QColor, QPixmap, QPainterPath, QPalette
from PySide6.QtSvg import QSvgRenderer
from components.user_settings_menu import UserSettingsMenu


def load_svg_icon_with_system_color(svg_path: str, size: int = 14) -> QPixmap:
    """加载 SVG 图标并应用系统颜色策略（window-text）
    
    Args:
        svg_path: SVG 文件路径
        size: 图标大小
    
    Returns:
        QPixmap: 渲染后的图标
    """
    if not os.path.exists(svg_path):
        # 如果文件不存在，返回透明占位符
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        return pixmap
    
    # 获取系统颜色（window-text）
    app = QApplication.instance()
    if app:
        palette = app.palette()
        system_color = palette.color(QPalette.ColorRole.WindowText)
        color_hex = system_color.name()
    else:
        # 如果没有应用程序实例，使用默认颜色
        color_hex = "#212121"
    
    # 读取 SVG 文件内容
    with open(svg_path, 'r', encoding='utf-8') as f:
        svg_content = f.read()
    
    # 替换 fill 颜色（跳过 fill="none"）
    def replace_fill(match):
        fill_value = match.group(1)
        if fill_value == 'none':
            return match.group(0)  # 保持 fill="none" 不变
        return f'fill="{color_hex}"'
    
    # 替换所有 fill 属性（除了 fill="none"）
    svg_content = re.sub(r'fill="([^"]*)"', replace_fill, svg_content)
    svg_content = re.sub(r"fill='([^']*)'", lambda m: f'fill="{color_hex}"' if m.group(1) != 'none' else m.group(0), svg_content)
    
    # 创建临时 SVG 渲染器
    renderer = QSvgRenderer(svg_content.encode('utf-8'))
    
    # 创建 pixmap 并渲染
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer.render(painter)
    painter.end()
    
    return pixmap


class CustomTitleBar(QWidget):
    """自定义窗口标题栏类"""
    
    # 定义信号：用于窗口控制
    minimize_clicked = Signal()
    maximize_clicked = Signal()
    close_clicked = Signal()
    search_text_changed = Signal(str)  # 搜索文本变化信号
    settings_clicked = Signal()  # 用户设置按钮点击信号
    
    def __init__(self, parent=None, title: str = "Simond 保险箱", logo_path: str = None,
                 user_name: str = "Pang Jiashun", user_email: str = "418889238@qq.com", 
                 user_initials: str = "PJ"):
        super().__init__(parent)
        self.title = title
        self.logo_path = logo_path
        self._is_maximized = False
        self.user_name = user_name
        self.user_email = user_email
        self.user_initials = user_initials
        
        # 初始化界面
        self.init_ui()
        
        # 创建用户设置菜单
        self.user_menu = UserSettingsMenu(self, user_name, user_email, user_initials)
        self.user_menu.hide()
    
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
        
        # 创建主水平布局
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 0, 0, 0)
        main_layout.setSpacing(8)
        
        # ========== 左侧区域：Logo + 标题 ==========
        left_container = QWidget()
        left_layout = QHBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)
        
        # 创建Logo标签
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(18, 18)  # 设置Logo大小
        self.logo_label.setScaledContents(True)  # 允许缩放内容
        self.set_logo(self.logo_path)  # 设置Logo
        left_layout.addWidget(self.logo_label)
        
        # 创建标题标签（使用系统文本颜色）
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: palette(window-text);
            }
        """)
        left_layout.addWidget(self.title_label)
        
        left_container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        main_layout.addWidget(left_container)
        
        # 左侧弹簧
        left_spacer = QWidget()
        left_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        main_layout.addWidget(left_spacer)
        
        # ========== 中间：搜索框容器 ==========
        search_container = QWidget()
        # 增加容器高度以容纳阴影（32px搜索框 + 上下各6px阴影空间 = 44px）
        search_container.setFixedHeight(44)
        search_container_layout = QHBoxLayout(search_container)
        # 添加边距以显示阴影（左右各6px，上下各6px）
        search_container_layout.setContentsMargins(6, 6, 6, 6)
        search_container_layout.setSpacing(0)
        
        # 让这个容器成为"真正的卡片"
        search_card = QWidget()
        search_card.setObjectName("SearchCard")
        card_layout = QHBoxLayout(search_card)
        card_layout.setContentsMargins(12, 0, 12, 0)
        card_layout.setSpacing(0)
        search_container_layout.addWidget(search_card)
        
        # 给"卡片"加圆角和背景
        search_card.setStyleSheet("""
            QWidget#SearchCard {
                background-color: palette(base);
                border-radius: 6px;
            }
        """)
        
        # 把阴影效果挂在 search_card 上
        shadow_effect = QGraphicsDropShadowEffect(search_card)
        shadow_effect.setBlurRadius(10)               # 模糊半径更大，更柔软
        shadow_effect.setXOffset(0)
        shadow_effect.setYOffset(1)                  # 阴影向下拉一些
        shadow_effect.setColor(QColor(0, 0, 0, 60)) # 更深一点的半透明黑
        search_card.setGraphicsEffect(shadow_effect)
        
        # 创建搜索框（透明背景，让外层容器负责背景）
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索文件")
        self.search_input.setFixedHeight(32)
        self.search_input.setFocusPolicy(Qt.FocusPolicy.ClickFocus)  # 只在点击时获得焦点
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: transparent;
                border: none;
                padding-left: 0px;
                padding-right: 32px;
                font-size: 13px;
                color: palette(window-text);
            }
            QLineEdit::placeholder {
                color: palette(placeholder-text);
            }
        """)
        
        # 保存原始placeholder文本，并在focus时隐藏
        self._original_placeholder = "搜索文件"
        
        # 重写focus事件以隐藏placeholder
        original_focus_in = self.search_input.focusInEvent
        original_focus_out = self.search_input.focusOutEvent
        
        def focus_in_event(event):
            self.search_input.setPlaceholderText("")
            if original_focus_in:
                original_focus_in(event)
        
        def focus_out_event(event):
            if not self.search_input.text():
                self.search_input.setPlaceholderText(self._original_placeholder)
            if original_focus_out:
                original_focus_out(event)
        
        self.search_input.focusInEvent = focus_in_event
        self.search_input.focusOutEvent = focus_out_event
        
        self.search_input.textChanged.connect(self.search_text_changed.emit)
        self.search_input.clearFocus()  # 确保默认不获得焦点
        card_layout.addWidget(self.search_input)
        
        # 创建搜索图标（放在搜索框内部右侧）
        self.search_icon_label = QLabel(self.search_input)
        self.search_icon_label.setFixedSize(14, 14)
        self.search_icon_label.setScaledContents(True)
        self.search_icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)  # 让鼠标事件穿透
        
        # 使用系统颜色策略加载 SVG 图标
        search_icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons", "ic_fluent_search_16_regular.svg")
        search_pixmap = load_svg_icon_with_system_color(search_icon_path, 14)
        self.search_icon_label.setPixmap(search_pixmap)
        
        # 更新图标位置的函数（右侧内边距10px，上下居中）
        def update_search_icon_position():
            if self.search_input:
                w = self.search_input.width()
                h = self.search_input.height()
                # 右侧内边距默认，上下居中
                self.search_icon_label.move(
                    w - self.search_icon_label.width(),
                    (h - self.search_icon_label.height()) // 2
                )
        
        # 保存更新函数以便后续调用
        self._update_search_icon_position = update_search_icon_position
        
        # 初始定位
        self.search_input.resizeEvent = lambda e: (QLineEdit.resizeEvent(self.search_input, e), update_search_icon_position())
        # 延迟更新，确保搜索框已正确布局
        QTimer.singleShot(0, update_search_icon_position)
        
        # 固定搜索框宽度
        search_container.setFixedWidth(500)
        main_layout.addWidget(search_container)
        
        # 右侧弹簧
        right_spacer = QWidget()
        right_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        main_layout.addWidget(right_spacer)
        
        # ========== 用户设置容器 ==========
        user_settings_container = QWidget()
        user_settings_layout = QHBoxLayout(user_settings_container)
        
        # 用户设置按钮（圆形头像）
        self.settings_btn = QPushButton()
        self.settings_btn.setFixedSize(30, 30)  # 圆形按钮
        self.settings_btn.setCheckable(True)   # 🔥 关键：让按钮成为开关
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: palette(light);
                border: none;
                border-radius: 15px;
                color: palette(button-text);
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                font-size: 11px;          /* hover 时变小 */
                font-weight: normal;      /* hover 时取消加粗 */
            }
        """)
        # 创建用户头像图标（使用文字，也可以后续替换为图片）
        # 这里使用"U"作为用户图标占位符，可以后续替换为实际头像
        self.settings_btn.setText(self.user_initials)
        
        # # 记录按下时菜单是否是打开的
        # self._menu_was_open_on_press = False
        # original_mouse_press = self.settings_btn.mousePressEvent
        
        # def settings_btn_mouse_press(event):
        #     if event.button() == Qt.MouseButton.LeftButton:
        #         # 记录"按下这一刻菜单是不是开的"
        #         self._menu_was_open_on_press = self.user_menu.isVisible()
        #     # 保持原有行为
        #     if original_mouse_press:
        #         original_mouse_press(event)
        
        # self.settings_btn.mousePressEvent = settings_btn_mouse_press
        
        # self.settings_btn.clicked.connect(self.show_user_menu)
        self.settings_btn.toggled.connect(self.toggle_user_menu)

        user_settings_layout.addWidget(self.settings_btn)
        
        user_settings_container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        main_layout.addWidget(user_settings_container)
        
        # ========== 窗口控制容器 ==========
        window_controls_container = QWidget()
        window_controls_layout = QHBoxLayout(window_controls_container)
        window_controls_layout.setContentsMargins(0, 0, 0, 0)
        window_controls_layout.setSpacing(0)
        
        # 最小化按钮（使用系统颜色）
        self.minimize_btn = QPushButton("−")
        self.minimize_btn.setFixedSize(46, 32)
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
        window_controls_layout.addWidget(self.minimize_btn)
        
        # 最大化/还原按钮（使用系统颜色）
        self.maximize_btn = QPushButton("□")
        self.maximize_btn.setFixedSize(46, 32)
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
        window_controls_layout.addWidget(self.maximize_btn)
        
        # 关闭按钮（使用系统颜色，悬停时使用红色）
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(46, 32)
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
                border-top-right-radius: 12px;
            }
        """)
        self.close_btn.clicked.connect(self.close_clicked.emit)
        window_controls_layout.addWidget(self.close_btn)
        
        window_controls_container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        main_layout.addWidget(window_controls_container, alignment=Qt.AlignTop)
        
        # 控制两边伸缩比例，让中间更"居中感"
        main_layout.setStretch(0, 0)  # 左容器
        main_layout.setStretch(1, 1)  # 左弹簧
        main_layout.setStretch(2, 0)  # 搜索容器
        main_layout.setStretch(3, 1)  # 右弹簧
        main_layout.setStretch(4, 0)  # 右容器
        
        # 保存鼠标按下位置，用于窗口拖动
        self._drag_position = None
    
    def toggle_user_menu(self, checked):
        if checked:
            self.show_user_menu()
        else:
            self.user_menu.hide()

    def hideEvent(self, event):
        # 通知标题栏按钮取消选中
        if hasattr(self.parent(), "settings_btn"):
            self.parent().settings_btn.setChecked(False)
        super().hideEvent(event)

    def show_user_menu(self):
        """显示或隐藏用户设置菜单（点击头像按钮时切换）
        
        - 如果按下按钮时菜单是展开的：这次点击只负责"收回"
        - 如果按下按钮时菜单是收起的：这次点击负责"展开"
        """
        # 如果按下时就是展开状态，则这次点击只关不再开
        if getattr(self, "_menu_was_open_on_press", False):
            self.user_menu.hide()
            return
        
        # 否则按下时是收起的，这次点击就展开
        if not self.user_menu.isVisible():
            self.user_menu.adjustSize()
            button_pos = self.settings_btn.mapToGlobal(QPoint(0, 0))
            menu_x = button_pos.x() + self.settings_btn.width() - self.user_menu.width()
            menu_y = button_pos.y() + self.settings_btn.height() + 4
            self.user_menu.show_at_position(QPoint(menu_x, menu_y))
    
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
            pixmap = QPixmap(18, 18)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(QColor(66, 133, 244))  # 蓝色
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(1, 1, 16, 16, 3, 3)  # 圆角矩形
            # 在矩形中心绘制一个简单的"S"字母
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(painter.font())
            font = painter.font()
            font.setPointSize(11)
            painter.setFont(font)
            painter.drawText(4, 14, "S")
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


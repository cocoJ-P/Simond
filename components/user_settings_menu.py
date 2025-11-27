#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户设置下拉菜单组件
独立的下拉菜单，用于显示用户信息和设置选项
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt, QSize, Signal, QPropertyAnimation, QEasingCurve, QPoint, QRect
from PySide6.QtGui import QMouseEvent, QPainter, QColor, QPixmap, QPainterPath, QFont, QBrush


class UserSettingsMenu(QWidget):
    """用户设置下拉菜单"""
    
    # 定义信号：菜单项点击
    logout_clicked = Signal()
    payment_methods_clicked = Signal()
    redeem_code_clicked = Signal()
    payment_help_clicked = Signal()
    manage_account_clicked = Signal()
    send_feedback_clicked = Signal()
    storage_settings_clicked = Signal()
    
    def __init__(self, parent=None, user_name: str = "Pang Jiashun", 
                 user_email: str = "418889238@qq.com", user_initials: str = "PJ"):
        super().__init__(parent)
        self.user_name = user_name
        self.user_email = user_email
        self.user_initials = user_initials
        
        # 设置窗口属性（无边框、弹出窗口、透明背景、无阴影）
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.Popup |
            Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 初始化动画
        self._init_animation()
        
        # 初始化界面
        self.init_ui()
    
    def _init_animation(self):
        """初始化动画效果"""
        # 几何动画（位置和大小）
        self.geometry_animation = QPropertyAnimation(self, b"geometry")
        self.geometry_animation.setDuration(200)  # 200ms动画时长
        self.geometry_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def init_ui(self):
        """初始化菜单界面"""
        # 设置固定宽度
        self.setFixedWidth(280)
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建主容器（背景已在paintEvent中绘制，这里设为透明）
        self.container = QWidget()
        self.container.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
            }
        """)
        # 保存容器引用
        container = self.container
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # ========== 用户信息区域 ==========
        user_info_widget = QWidget()
        user_info_widget.setFixedHeight(80)
        user_info_widget.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
        """)
        user_info_layout = QHBoxLayout(user_info_widget)
        user_info_layout.setContentsMargins(16, 16, 16, 16)
        user_info_layout.setSpacing(12)
        
        # 用户头像
        avatar_label = QLabel()
        avatar_label.setFixedSize(48, 48)
        avatar_label.setScaledContents(True)
        # 创建圆形头像
        avatar_pixmap = QPixmap(48, 48)
        avatar_pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(avatar_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # 绘制圆形背景
        painter.setBrush(QColor(66, 133, 244))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, 48, 48)
        # 绘制文字
        painter.setPen(QColor(255, 255, 255))
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(avatar_pixmap.rect(), Qt.AlignmentFlag.AlignCenter, self.user_initials)
        painter.end()
        avatar_label.setPixmap(avatar_pixmap)
        user_info_layout.addWidget(avatar_label)
        
        # 用户信息（姓名、邮箱、注销）
        user_text_layout = QVBoxLayout()
        user_text_layout.setContentsMargins(0, 0, 0, 0)
        user_text_layout.setSpacing(4)
        
        # 用户名
        name_label = QLabel(self.user_name)
        name_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        user_text_layout.addWidget(name_label)
        
        # 邮箱
        email_label = QLabel(self.user_email)
        email_label.setStyleSheet("""
            QLabel {
                color: #999999;
                font-size: 12px;
            }
        """)
        user_text_layout.addWidget(email_label)
        
        # 注销按钮
        logout_btn = QPushButton("注销")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #4CC2FF;
                font-size: 12px;
                text-align: left;
                padding: 0;
            }
            QPushButton:hover {
                color: #66D4FF;
            }
        """)
        def on_logout_clicked():
            self.logout_clicked.emit()
            self.hide()
        logout_btn.clicked.connect(on_logout_clicked)
        user_text_layout.addWidget(logout_btn)
        
        user_info_layout.addLayout(user_text_layout)
        user_info_layout.addStretch()
        
        container_layout.addWidget(user_info_widget)
        
        # ========== 分隔线 ==========
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("""
            QFrame {
                background-color: #3d3d40;
                border: none;
                max-height: 1px;
            }
        """)
        container_layout.addWidget(separator)
        
        # ========== 菜单项区域 ==========
        menu_items_layout = QVBoxLayout()
        menu_items_layout.setContentsMargins(8, 8, 8, 8)
        menu_items_layout.setSpacing(0)
        
        # 菜单项列表
        menu_items = [
            ("支付方式", self.payment_methods_clicked, "💳"),
            ("兑换代码或礼品卡", self.redeem_code_clicked, "🎁"),
            ("有关付款和退款的帮助", self.payment_help_clicked, "❓"),
            ("管理帐户和设备", self.manage_account_clicked, "🖥️"),
            ("发送反馈", self.send_feedback_clicked, "✈️"),
            ("存储设置", self.storage_settings_clicked, "⚙️"),
        ]
        
        for text, signal, icon_text in menu_items:
            menu_item = self.create_menu_item(text, icon_text, signal)
            menu_items_layout.addWidget(menu_item)
        
        container_layout.addLayout(menu_items_layout)
        
        main_layout.addWidget(container)
    
    def create_menu_item(self, text: str, icon_text: str, signal: Signal):
        """创建菜单项"""
        item_widget = QPushButton()
        item_widget.setFixedHeight(40)
        item_widget.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                color: #ffffff;
                font-size: 13px;
                text-align: left;
                padding-left: 12px;
            }
            QPushButton:hover {
                background-color: #3d3d40;
            }
        """)
        
        # 创建布局
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(12, 0, 12, 0)
        item_layout.setSpacing(12)
        
        # 图标标签
        icon_label = QLabel(icon_text)
        icon_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 16px;
                background-color: transparent;
            }
        """)
        icon_label.setFixedWidth(20)
        item_layout.addWidget(icon_label)
        
        # 文字标签
        text_label = QLabel(text)
        text_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 13px;
                background-color: transparent;
            }
        """)
        item_layout.addWidget(text_label)
        item_layout.addStretch()
        
        # 连接点击事件：点击后发出信号并关闭菜单
        def on_item_clicked():
            signal.emit()
            self.hide()
        
        item_widget.clicked.connect(on_item_clicked)
        
        return item_widget
    
    def show_at_position(self, pos: QPoint):
        """在指定位置显示菜单（带动画效果：从按钮下方展开）"""
        # 确保菜单已调整大小
        self.adjustSize()
        menu_width = self.width()
        menu_height = self.height()
        
        # 计算起始位置：在按钮正下方，高度为0（从按钮下方开始展开）
        start_rect = QRect(pos.x(), pos.y(), menu_width, 0)
        # 结束位置：在按钮正下方，完整高度
        final_rect = QRect(pos.x(), pos.y(), menu_width, menu_height)
        
        # 先设置到起始位置（按钮正下方，高度为0）
        self.setGeometry(start_rect)
        self.show()
        self.setFocus()
        
        # 启动几何动画（从按钮下方展开）
        if self.geometry_animation.state() != QPropertyAnimation.State.Running:
            self.geometry_animation.setStartValue(start_rect)
            self.geometry_animation.setEndValue(final_rect)
            self.geometry_animation.start()
    
    def paintEvent(self, event):
        """绘制磨玻璃效果背景（毛玻璃效果）"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制圆角矩形背景（磨玻璃效果）
        rect = self.rect()
        path = QPainterPath()
        path.addRoundedRect(rect, 8, 8)
        
        # 磨玻璃效果：使用半透明的深色背景
        # rgba(45, 45, 48, 240) - 较高的不透明度以产生磨玻璃效果
        # 注意：真正的磨玻璃需要背景模糊，这里使用半透明模拟
        brush = QBrush(QColor(45, 45, 48, 240))
        painter.fillPath(path, brush)
        
        # 添加轻微的边框以增强视觉效果
        painter.setPen(QColor(60, 60, 63, 100))
        painter.drawPath(path)
    
    def focusOutEvent(self, event):
        """失去焦点时关闭菜单"""
        self.hide()
        super().focusOutEvent(event)


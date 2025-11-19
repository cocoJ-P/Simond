#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义顶部栏组件
用于定制窗口最上方工具栏的尺寸和内容
"""

from PySide6.QtWidgets import QToolBar, QWidget, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QAction


class CustomTopBar(QToolBar):
    """自定义顶部栏类"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 设置工具栏属性
        self.setMovable(False)  # 禁止拖动
        self.setFloatable(False)  # 禁止浮动
        
        # 设置工具栏尺寸
        self.setIconSize(QSize(24, 24))  # 图标大小
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)  # 图标和文字并排
        
        # 初始化界面
        self.init_ui()
    
    def init_ui(self):
        """初始化顶部栏界面"""
        
        # ========== 左侧区域：应用标题/Logo ==========
        # 可以添加应用Logo或标题
        title_label = QLabel("Simond 保险箱")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 0 10px;")
        self.addWidget(title_label)
        
        # 添加分隔符
        self.addSeparator()
        
        # ========== 中间区域：主要功能按钮 ==========
        # 选择保险箱文件夹按钮
        self.action_choose_dir = QAction("选择保险箱文件夹…", self)
        self.addAction(self.action_choose_dir)
        
        # 可以添加更多按钮
        # self.action_refresh = QAction("刷新", self)
        # self.addAction(self.action_refresh)
        
        # 添加分隔符
        self.addSeparator()
        
        # ========== 右侧区域：其他功能 ==========
        # 可以添加设置、帮助等按钮
        # self.action_settings = QAction("设置", self)
        # self.addAction(self.action_settings)
        
        # 添加弹性空间，使右侧按钮靠右对齐
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.addWidget(spacer)
    
    def set_bar_height(self, height: int):
        """设置顶部栏高度"""
        self.setFixedHeight(height)
    
    def set_icon_size(self, width: int, height: int):
        """设置图标大小"""
        self.setIconSize(QSize(width, height))
    
    def add_custom_action(self, text: str, icon_path: str = None, callback=None):
        """添加自定义动作按钮"""
        action = QAction(text, self)
        if icon_path:
            action.setIcon(QIcon(icon_path))
        if callback:
            action.triggered.connect(callback)
        self.addAction(action)
        return action
    
    def add_custom_widget(self, widget: QWidget):
        """添加自定义组件"""
        self.addWidget(widget)
    
    def clear_actions(self):
        """清空所有动作"""
        self.clear()


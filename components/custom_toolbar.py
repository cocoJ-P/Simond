#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义工具栏组件
用于文件操作和视图切换
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Signal


class CustomToolbar(QWidget):
    """自定义工具栏类"""
    
    # 定义信号：按钮点击事件
    refresh_clicked = Signal()
    upload_clicked = Signal()
    delete_clicked = Signal()
    view_mode_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 初始化界面
        self.init_ui()
    
    def init_ui(self):
        """初始化工具栏界面"""
        # 设置工具栏高度
        self.setFixedHeight(50)
        
        # 设置直角矩形边框
        self.setStyleSheet("""
            QWidget {
                border: 1px solid palette(mid);
                border-radius: 0px;
                background-color: palette(base);
            }
        """)
        
        # 创建水平布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        # 添加工具按钮
        self.btn_refresh = QPushButton("刷新")
        self.btn_upload = QPushButton("上传")
        self.btn_delete = QPushButton("删除")
        self.btn_view_mode = QPushButton("视图")
        
        # 将按钮添加到布局
        layout.addWidget(self.btn_refresh)
        layout.addWidget(self.btn_upload)
        layout.addWidget(self.btn_delete)
        layout.addWidget(self.btn_view_mode)
        layout.addStretch()  # 添加弹性空间，使按钮靠左对齐
        
        # 连接按钮信号到组件信号
        self.btn_refresh.clicked.connect(self.refresh_clicked.emit)
        self.btn_upload.clicked.connect(self.upload_clicked.emit)
        self.btn_delete.clicked.connect(self.delete_clicked.emit)
        self.btn_view_mode.clicked.connect(self.view_mode_clicked.emit)
    
    def set_view_mode_text(self, text: str):
        """设置视图模式按钮的文本"""
        self.btn_view_mode.setText(text)




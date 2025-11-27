#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simond 保险箱 (MVP)
一个桌面端文件管理应用
使用 QFileSystemModel + QListView 实现图标视图
使用 PySide6 实现
"""

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListView, 
    QFileSystemModel, QVBoxLayout, QHBoxLayout, QWidget
)
from PySide6.QtCore import QDir, QSize, Qt, QRectF
from PySide6.QtGui import QPainter, QPainterPath, QPalette, QPen

from components.custom_title_bar import CustomTitleBar
from components.custom_sidebar import CustomSidebar
from components.custom_toolbar import CustomToolbar


class VaultWindow(QMainWindow):
    """保险箱主窗口类"""
    
    def __init__(self):
        super().__init__()
        
        # 保险箱根目录路径（初始为空）
        self.vault_dir = ""
        
        # 初始化界面
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        # 隐藏系统标题栏，使用自定义标题栏
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        self.setFixedSize(1100, 700)
        
        # 居中窗口
        screen = QApplication.primaryScreen()
        rect = screen.availableGeometry()
        self.move(
            rect.center().x() - 1100 // 2,
            rect.center().y() - 700 // 2
        )
        
        # 设置窗口背景为透明，以便绘制圆角
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # ========== 创建主容器 ==========
        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ========== 创建自定义标题栏 ==========
        self.title_bar = CustomTitleBar(self, "Simond 保险箱")
        main_layout.addWidget(self.title_bar)
        
        # 连接标题栏控制按钮的信号
        self.title_bar.minimize_clicked.connect(self.showMinimized)
        self.title_bar.maximize_clicked.connect(self.toggle_maximize)
        self.title_bar.close_clicked.connect(self.close)
        
        # ========== 创建内容区域容器（水平布局：侧边栏 + 主内容） ==========
        content_widget = QWidget()
        content_widget.setObjectName("ContentWidget")
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        main_layout.addWidget(content_widget)
        
        # ========== 创建侧边栏 ==========
        self.sidebar = CustomSidebar(self)
        content_layout.addWidget(self.sidebar)
        
        # 连接侧边栏菜单项点击信号
        self.sidebar.item_clicked.connect(self.on_sidebar_item_clicked)
        
        # ========== 创建主内容区域容器 ==========
        main_content_widget = MainContentCard()
        main_content_widget.setObjectName("MainContent")
        main_content_layout = QVBoxLayout(main_content_widget)
        main_content_layout.setContentsMargins(0, 0, 0, 0)
        main_content_layout.setSpacing(0)
        content_layout.addWidget(main_content_widget)
        
        # ========== 创建工具栏 ==========
        self.toolbar = CustomToolbar(self)
        main_content_layout.addWidget(self.toolbar)
        
        # ========== 创建文件系统模型 ==========
        self.file_model = QFileSystemModel()
        # 设置过滤器：只显示文件，不显示文件夹（过滤掉 . 和 ..）
        # NoDotAndDotDot 过滤掉 . 和 .. 目录
        self.file_model.setFilter(QDir.Filter.Files | QDir.Filter.NoDotAndDotDot)
        
        # ========== 创建列表视图 ==========
        self.list_view = QListView()
        self.list_view.setModel(self.file_model)
        
        # 设置为图标模式（IconMode）
        self.list_view.setViewMode(QListView.ViewMode.IconMode)
        
        # 设置图标大小（64x64 像素）
        self.list_view.setIconSize(QSize(64, 64))
        
        # 设置图标之间的间距（16 像素）
        self.list_view.setSpacing(16)
        
        # 设置网格大小（图标大小 + 间距 + 文字高度）
        # 这里设置为自动调整，也可以手动设置
        self.list_view.setGridSize(QSize(100, 100))
        
        # 设置布局模式为自动调整（Adjust）
        self.list_view.setResizeMode(QListView.ResizeMode.Adjust)
        
        # 启用拖拽功能
        self.list_view.setAcceptDrops(True)
        self.list_view.setDragDropMode(QListView.DragDropMode.DropOnly)
        
        # 连接双击事件
        self.list_view.doubleClicked.connect(self.on_file_double_clicked)

        # ✨ 关键：让视图本身和 viewport 都透明
        self.list_view.setStyleSheet("""
        QListView {
            background: transparent;
            border: none;
        }
        """)
        
        # 连接工具栏按钮信号
        self.toolbar.view_mode_clicked.connect(self.on_view_mode_clicked)
        
        # 将列表视图添加到主内容区域
        main_content_layout.addWidget(self.list_view)
        
        # ========== 启用窗口级别的拖拽功能 ==========
        # 设置窗口接受拖拽（用于从系统资源管理器拖入文件）
        self.setAcceptDrops(True)

        # # 关键：让主内容区域自身不再画不透明矩形背景
        # self.setStyleSheet("""
        # #CentralWidget, #ContentWidget, #MainContent {
        #     background: transparent;
        # }
        # """)
      
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        rect = self.rect()

        # 使用浮点矩形提升抗锯齿
        r = QRectF(rect)
        r.adjust(1, 1, -1, -1)

        radius = 12

        # 系统色
        window_color = self.palette().color(QPalette.Window)
        border_color = self.palette().color(QPalette.Mid)

        # 背景
        painter.setPen(Qt.NoPen)
        painter.setBrush(window_color)
        painter.drawRoundedRect(r, radius, radius)

        # 边框
        pen = QPen(border_color, 1)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(r, radius, radius)
    
    def toggle_maximize(self):
        """切换最大化/还原窗口"""
        if self.isMaximized():
            self.showNormal()
            self.title_bar.update_maximize_button(False)
        else:
            self.showMaximized()
            self.title_bar.update_maximize_button(True)
        
    def on_sidebar_item_clicked(self, item_id: str):
        """处理侧边栏菜单项点击事件"""
        print(f"侧边栏菜单项点击：{item_id}")
        # 后续可以在这里添加：切换视图、筛选文件等功能
        # 例如：
        # if item_id == "home":
        #     # 显示所有文件
        # elif item_id == "recent":
        #     # 显示最近使用的文件
        # elif item_id == "favorites":
        #     # 显示收藏的文件
        # elif item_id == "settings":
        #     # 打开设置窗口
    
    def on_file_double_clicked(self, index):
        """处理文件双击事件"""
        # 获取文件的绝对路径
        file_path = self.file_model.filePath(index)
        print(f"双击文件：{file_path}")
        
        # 后续可以在这里添加：打开文件、预览、计算哈希等功能
    
    
    def on_view_mode_clicked(self):
        """处理视图模式按钮点击事件"""
        # 切换视图模式：图标模式和列表模式
        current_mode = self.list_view.viewMode()
        if current_mode == QListView.ViewMode.IconMode:
            self.list_view.setViewMode(QListView.ViewMode.ListMode)
            self.toolbar.set_view_mode_text("图标")
        else:
            self.list_view.setViewMode(QListView.ViewMode.IconMode)
            self.toolbar.set_view_mode_text("列表")


# 自定义的主内容区域卡片
class MainContentCard(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(1, 1, -1, -1)
        r = 12  # 圆角半径

        bg = self.palette().color(QPalette.Base)
        border_color = self.palette().color(QPalette.Mid)

        # ====== 背景路径 ======
        path = QPainterPath()

        # 左上圆角
        path.moveTo(rect.left() + 10, rect.top())
        path.quadTo(rect.left(), rect.top(), rect.left(), rect.top() + 10)

        # 左边（直线）
        path.lineTo(rect.left(), rect.bottom() - r)

        # 左下直角
        path.lineTo(rect.left(), rect.bottom())
        path.lineTo(rect.right() - r, rect.bottom())

        # 下边（继续到右下圆角起点）
        path.quadTo(rect.right(), rect.bottom(), rect.right(), rect.bottom() - r)

        # 右边
        path.lineTo(rect.right(), rect.top())

        # 上边回到起点
        path.lineTo(rect.left() + r, rect.top())

        # 填充背景
        painter.setPen(Qt.NoPen)
        painter.setBrush(bg)
        painter.drawPath(path)

        # ====== 边框路径（只画上边 + 左边）======

        border = QPainterPath()

        # 左上圆角 10的圆角
        border.moveTo(rect.left() + 10, rect.top())
        border.quadTo(rect.left(), rect.top(), rect.left(), rect.top() + 10)

        # 左边直线
        border.lineTo(rect.left(), rect.bottom())

        # 回到圆角起点，画上边
        border.moveTo(rect.left() + r - 2, rect.top())
        border.lineTo(rect.right(), rect.top())

        pen = QPen(border_color, 0.2)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(border)

def main():
    """主函数：启动应用程序"""
    app = QApplication([])
    
    # 创建并显示主窗口
    window = VaultWindow()
    window.show()
    
    # 运行应用
    app.exec()


if __name__ == "__main__":
    main()


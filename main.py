#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simond 保险箱 (MVP)
一个极简的桌面端文件管理应用
使用 QFileSystemModel + QListView 实现图标视图
使用 PySide6 实现
"""

import os
import shutil
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListView, QFileDialog, 
    QMessageBox, QToolBar, QFileSystemModel, QVBoxLayout, QWidget
)
from PySide6.QtCore import QDir, QSize, Qt, QRect
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QAction, QPainter, QPainterPath, QColor, QRegion, QPalette
from components.custom_top_bar import CustomTopBar
from components.custom_title_bar import CustomTitleBar


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
        self.setGeometry(100, 100, 900, 600)
        
        # 设置窗口背景为透明，以便绘制圆角
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # ========== 创建主容器 ==========
        central_widget = QWidget()
        central_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
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
        
        # ========== 创建自定义顶部栏（工具栏） ==========
        self.top_bar = CustomTopBar(self)
        main_layout.addWidget(self.top_bar)
        
        # 连接"选择保险箱文件夹"动作的信号
        self.top_bar.action_choose_dir.triggered.connect(self.choose_vault_dir)
        
        # ========== 创建内容区域容器 ==========
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(content_widget)
        
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
        
        # 将列表视图添加到内容区域
        content_layout.addWidget(self.list_view)
        
        # ========== 启用窗口级别的拖拽功能 ==========
        # 设置窗口接受拖拽（用于从系统资源管理器拖入文件）
        self.setAcceptDrops(True)
        
        # ========== 状态栏：显示当前保险箱路径 ==========
        self.statusBar().showMessage("尚未选择保险箱文件夹")
        # 设置状态栏底部圆角样式（使用系统颜色）
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: palette(window);
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            }
        """)
        
        # 设置窗口圆角mask
        self.update_rounded_corners()
    
    def update_rounded_corners(self):
        """更新窗口圆角mask（12px圆角）"""
        if self.isMaximized():
            return
        path = QPainterPath()
        rect = QRect(0, 0, self.width(), self.height())
        path.addRoundedRect(rect, 12, 12)
        # 使用更高质量的多边形转换
        polygon = path.toFillPolygon()
        region = QRegion(polygon.toPolygon())
        self.setMask(region)
    
    def resizeEvent(self, event):
        """窗口大小改变时更新圆角"""
        super().resizeEvent(event)
        if not self.isMaximized():
            self.update_rounded_corners()
    
    def paintEvent(self, event):
        """绘制圆角边框和背景"""
        painter = QPainter(self)
        # 启用高质量抗锯齿
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        
        # 获取系统调色板颜色
        palette = self.palette()
        window_color = palette.color(QPalette.ColorRole.Window)
        border_color = palette.color(QPalette.ColorRole.Mid)
        
        # 绘制圆角矩形背景
        path = QPainterPath()
        rect = QRect(0, 0, self.width(), self.height())
        path.addRoundedRect(rect, 12, 12)
        
        # 填充背景（使用系统颜色）
        painter.fillPath(path, window_color)
        
        # 绘制边框（使用系统边框颜色）
        pen = painter.pen()
        pen.setColor(border_color)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawPath(path)
    
    def toggle_maximize(self):
        """切换最大化/还原窗口"""
        if self.isMaximized():
            self.showNormal()
            self.title_bar.update_maximize_button(False)
            # 还原时重新应用圆角
            self.update_rounded_corners()
        else:
            # 最大化时移除圆角mask（最大化窗口通常不需要圆角）
            self.setMask(QRegion())
            self.showMaximized()
            self.title_bar.update_maximize_button(True)
        
    def choose_vault_dir(self):
        """选择保险箱根目录"""
        # 弹出文件夹选择对话框
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择保险箱文件夹",
            "",  # 默认路径为空，从用户目录开始
            QFileDialog.Option.ShowDirsOnly
        )
        
        if directory:
            # 保存路径
            self.vault_dir = directory
            
            # 设置文件系统模型的根路径
            root_index = self.file_model.setRootPath(directory)
            
            # 设置列表视图的根索引，使视图显示该目录内容
            self.list_view.setRootIndex(root_index)
            
            # 更新状态栏显示
            self.statusBar().showMessage(f"当前保险箱：{self.vault_dir}")
    
    def on_file_double_clicked(self, index):
        """处理文件双击事件"""
        # 获取文件的绝对路径
        file_path = self.file_model.filePath(index)
        print(f"双击文件：{file_path}")
        
        # 后续可以在这里添加：打开文件、预览、计算哈希等功能
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """处理拖拽进入事件（窗口级别）"""
        # 只接受包含本地文件路径的拖拽
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dropEvent(self, event: QDropEvent):
        """处理文件拖放事件（窗口级别）"""
        # 获取拖入的文件路径列表
        urls = event.mimeData().urls()
        
        if not urls:
            event.ignore()
            return
        
        # 检查是否已选择保险箱文件夹
        if not self.vault_dir:
            QMessageBox.warning(
                self,
                "提示",
                "请先选择保险箱文件夹"
            )
            event.ignore()
            return
        
        # 处理每个拖入的文件
        copied_count = 0
        failed_files = []
        
        for url in urls:
            # 获取本地文件路径
            local_path = url.toLocalFile()
            
            # 检查是否为有效文件路径
            if not local_path or not os.path.isfile(local_path):
                continue
            
            try:
                # 获取文件名
                file_name = os.path.basename(local_path)
                dest_path = os.path.join(self.vault_dir, file_name)
                
                # 复制文件到保险箱目录
                # 注意：这里直接覆盖同名文件（MVP 阶段）
                # 后续可以扩展：检查重名、添加时间戳、询问用户等
                shutil.copy2(local_path, dest_path)
                copied_count += 1
                
            except Exception as e:
                # 记录失败的文件
                failed_files.append((os.path.basename(local_path), str(e)))
        
        # 显示操作结果
        if copied_count > 0:
            # QFileSystemModel 会自动刷新，但为了确保，可以手动触发
            # 由于使用了 QFileSystemModel，文件系统变化会自动反映到视图中
            
            # 如果有失败的文件，显示警告
            if failed_files:
                failed_msg = "\n".join([f"{name}: {error}" for name, error in failed_files])
                QMessageBox.warning(
                    self,
                    "部分文件复制失败",
                    f"成功复制 {copied_count} 个文件\n\n失败的文件：\n{failed_msg}"
                )
            else:
                QMessageBox.information(
                    self,
                    "成功",
                    f"已成功复制 {copied_count} 个文件到保险箱"
                )
        else:
            if failed_files:
                failed_msg = "\n".join([f"{name}: {error}" for name, error in failed_files])
                QMessageBox.critical(
                    self,
                    "复制失败",
                    f"所有文件复制失败：\n{failed_msg}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "提示",
                    "没有有效的文件被拖入"
                )
        
        event.acceptProposedAction()


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


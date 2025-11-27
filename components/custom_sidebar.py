
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义侧边栏组件
用于导航和功能切换
"""

import os
import re
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy, QLabel, QApplication
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QIcon, QPixmap, QPalette
from PySide6.QtSvg import QSvgRenderer

class SidebarItem(QPushButton):
    """侧边栏菜单项"""
    
    def __init__(self, text: str,  
                 icon_regular_path: str = None, icon_filled_path: str = None,
                 vertical_layout: bool = True):
        super().__init__()
        self.text = text
        self._is_selected = False
        self._is_hovered = False
        self.vertical_layout = vertical_layout
        
        # 图标路径
        self.icon_regular_path = icon_regular_path
        self.icon_filled_path = icon_filled_path
        
        self.setFixedHeight(70)
    
        self.setup_vertical_layout()
     
        
        # 设置文本和图标布局
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                text-align: center;
                color: palette(window-text);
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: palette(mid);
            }
            QPushButton:pressed {
                background-color: palette(light);
            }
        """)
        
        # 更新图标显示
        self.update_icon()
    
    def setup_vertical_layout(self):
        """设置垂直布局（图标在上，文字在下）"""
        # 创建内部容器
        container = QWidget(self)
        container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 创建图标标签
        self.icon_label = QLabel(container)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setFixedSize(28, 28)
        container_layout.addWidget(self.icon_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        # 创建文字标签
        self.text_label = QLabel(self.text, container)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setStyleSheet("font-size: 10px; color: palette(window-text);")
        container_layout.addWidget(self.text_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        # 将容器添加到按钮（通过设置按钮的布局）
        btn_layout = QVBoxLayout(self)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_layout.addWidget(container, alignment=Qt.AlignmentFlag.AlignCenter)
    
    def _get_system_color(self, role: QPalette.ColorRole) -> str:
        """获取系统颜色并转换为十六进制字符串"""
        app = QApplication.instance()
        if app:
            palette = app.palette()
            system_color = palette.color(role)
            return system_color.name()
        else:
            # 如果没有应用程序实例，使用默认颜色
            defaults = {
                QPalette.ColorRole.Highlight: "#0078D4",  # 默认蓝色
                QPalette.ColorRole.HighlightedText: "#FFFFFF",  # 默认白色
                QPalette.ColorRole.WindowText: "#E0E0E0",  # 默认浅灰色（更白）
            }
            return defaults.get(role, "#E0E0E0")
    
    def update_icon(self):
        """根据 hover 和选中状态更新图标"""
        icon = None
        
        # 获取系统颜色
        highlight_color = self._get_system_color(QPalette.ColorRole.Highlight)  # 系统高亮色（通常是蓝色）
        highlighted_text_color = self._get_system_color(QPalette.ColorRole.HighlightedText)  # 高亮文本色（通常是白色）
        default_color = self._get_system_color(QPalette.ColorRole.WindowText)  # 窗口文本色（通常比灰色更白）
        
        # 如果处于选中状态，使用 filled 图标并应用系统高亮颜色
        if self._is_selected and self.icon_filled_path:
            if os.path.exists(self.icon_filled_path):
                icon = load_svg_icon_with_color(self.icon_filled_path, highlight_color, 28)
        # 如果处于 hover 状态且未选中，使用 regular 图标并应用高亮文本颜色
        elif self._is_hovered and not self._is_selected and self.icon_regular_path:
            if os.path.exists(self.icon_regular_path):
                icon = load_svg_icon_with_color(self.icon_regular_path, highlighted_text_color, 28)
        # 否则使用 regular 图标，未选中且未hover时使用窗口文本颜色（更白）
        elif self.icon_regular_path:
            if os.path.exists(self.icon_regular_path):
                icon = load_svg_icon_with_color(self.icon_regular_path, default_color, 28)
        
        # 根据布局方式设置图标（垂直布局）
        if hasattr(self, 'icon_label') and icon:
            pixmap = icon.pixmap(28, 28)
            self.icon_label.setPixmap(pixmap)
        elif hasattr(self, 'icon_label'):
            self.icon_label.clear()
    
    def enterEvent(self, event):
        """鼠标进入事件（hover）"""
        self._is_hovered = True
        self.update_icon()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """鼠标离开事件（失去 hover）"""
        self._is_hovered = False
        self.update_icon()
        super().leaveEvent(event)
    
    def set_selected(self, selected: bool):
        """设置选中状态"""
        self._is_selected = selected
        # 更新图标显示
        self.update_icon()
        if selected:
            style = """
                QPushButton {
                    background-color: palette(Window);
                    border: none;
                    text-align: center;
                    font-size: 10px;
                    color: palette(window-text);
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: palette(light);
                }
            """
            self.setStyleSheet(style)
            if self.vertical_layout and hasattr(self, 'text_label'):
                self.text_label.setStyleSheet("font-size: 10px; color: palette(window-text);")
        else:
            style = """
                QPushButton {
                    background-color: transparent;
                    border: none;
                    text-align: center;
                    color: palette(window-text);
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: rgb(69, 69, 69);
                }
                QPushButton:pressed {
                    background-color: palette(mid);
                }
            """
            self.setStyleSheet(style)
            if self.vertical_layout and hasattr(self, 'text_label'):
                self.text_label.setStyleSheet("font-size: 10px; color: palette(window-text);")


class CustomSidebar(QWidget):
    """自定义侧边栏类"""
    
    # 定义信号：菜单项点击
    item_clicked = Signal(str)  # 传递菜单项标识
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_item = None
        self.items = {}
        
        # 初始化界面
        self.init_ui()
    
    def init_ui(self):
        """初始化侧边栏界面"""
        # 设置侧边栏宽度（默认200像素）
        self.setFixedWidth(100)
        
        # 设置背景色（使用系统颜色）
        self.setStyleSheet("""
            CustomSidebar {
                background-color: palette(window);
                border-right: 1px solid palette(mid);
            }
        """)
        
        # 创建垂直布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)  # 设置边距
        layout.setSpacing(4)  # 设置菜单项之间的间距
        
        # ========== 创建菜单项 ==========
        # 主页（带图标）
        # 获取图标路径（相对于项目根目录）
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        home_icon_regular = os.path.join(base_dir, "icons", "ic_fluent_home_20_regular.svg")
        home_icon_filled = os.path.join(base_dir, "icons", "ic_fluent_home_20_filled.svg")
        
        home_item = SidebarItem(
            "主页", 
            icon_regular_path=home_icon_regular,
            icon_filled_path=home_icon_filled,
            vertical_layout=True
        )
        home_item.clicked.connect(lambda: self.on_item_clicked("home", home_item))
        self.items["home"] = home_item
        layout.addWidget(home_item)
        
        # 本地
        local_icon_regular = os.path.join(base_dir, "icons", "ic_fluent_laptop_20_regular.svg")
        local_icon_filled = os.path.join(base_dir, "icons", "ic_fluent_laptop_20_filled.svg")
        local_item = SidebarItem(
            "本地", 
            icon_regular_path=local_icon_regular,
            icon_filled_path=local_icon_filled,
            vertical_layout=True
        )
        local_item.clicked.connect(lambda: self.on_item_clicked("local", local_item))
        self.items["local"] = local_item
        layout.addWidget(local_item)
        
        # 我的空间
        my_space_icon_regular = os.path.join(base_dir, "icons", "ic_fluent_cloud_20_regular.svg")
        my_space_icon_filled = os.path.join(base_dir, "icons", "ic_fluent_cloud_20_filled.svg")
        my_space_item = SidebarItem(
            "我的空间", 
            icon_regular_path=my_space_icon_regular,
            icon_filled_path=my_space_icon_filled,
            vertical_layout=True
        )
        my_space_item.clicked.connect(lambda: self.on_item_clicked("my_space", my_space_item))
        self.items["my_space"] = my_space_item
        layout.addWidget(my_space_item)
        
        # 进行中
        in_progress_icon_regular = os.path.join(base_dir, "icons", "ic_fluent_earth_leaf_20_regular.svg")
        in_progress_icon_filled = os.path.join(base_dir, "icons", "ic_fluent_earth_leaf_20_filled.svg")
        in_progress_item = SidebarItem(
            "进行中", 
            icon_regular_path=in_progress_icon_regular,
            icon_filled_path=in_progress_icon_filled,
            vertical_layout=True
        )
        in_progress_item.clicked.connect(lambda: self.on_item_clicked("in_progress", in_progress_item))
        self.items["in_progress"] = in_progress_item
        layout.addWidget(in_progress_item)
        
        # 添加弹性空间，使菜单项靠上对齐
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(spacer)
        
        # 设置
        settings_icon_regular = os.path.join(base_dir, "icons", "ic_fluent_square_dovetail_joint_28_regular.svg")
        settings_icon_filled = os.path.join(base_dir, "icons", "ic_fluent_square_dovetail_joint_28_filled.svg")
        
        settings_item = SidebarItem(
            "工作台", 
            icon_regular_path=settings_icon_regular,
            icon_filled_path=settings_icon_filled,
            vertical_layout=True
        )
        settings_item.clicked.connect(lambda: self.on_item_clicked("settings", settings_item))
        self.items["settings"] = settings_item
        layout.addWidget(settings_item)
        
        # 默认选中"主页"
        self.set_current_item("home")
    
    def on_item_clicked(self, item_id: str, item: SidebarItem):
        """处理菜单项点击事件"""
        self.set_current_item(item_id)
        self.item_clicked.emit(item_id)
    
    def set_current_item(self, item_id: str):
        """设置当前选中的菜单项"""
        # 取消之前选中项的样式
        if self.current_item and self.current_item in self.items:
            self.items[self.current_item].set_selected(False)
        
        # 设置新的选中项
        if item_id in self.items:
            self.items[item_id].set_selected(True)
            self.current_item = item_id
    
    def add_item(self, item_id: str, text: str, icon_text: str = ""):
        """动态添加菜单项"""
        if item_id in self.items:
            return
        
        item = SidebarItem(text, icon_text)
        item.clicked.connect(lambda: self.on_item_clicked(item_id, item))
        self.items[item_id] = item
        
        # 找到弹性空间之前的位置插入
        layout = self.layout()
        spacer_index = layout.count() - 2  # 弹性空间在倒数第二个位置
        layout.insertWidget(spacer_index, item)
    
    def remove_item(self, item_id: str):
        """移除菜单项"""
        if item_id in self.items:
            item = self.items[item_id]
            self.layout().removeWidget(item)
            item.deleteLater()
            del self.items[item_id]
            
            # 如果移除的是当前选中项，切换到主页
            if self.current_item == item_id:
                self.set_current_item("home")

def load_svg_icon_with_color(svg_path: str, color: str, size: int = 20) -> QIcon:
    """加载 SVG 图标并应用指定颜色"""
    if not os.path.exists(svg_path):
        return QIcon()
    
    # 读取 SVG 文件内容
    with open(svg_path, 'r', encoding='utf-8') as f:
        svg_content = f.read()
    
    # 替换 fill 颜色（跳过 fill="none"）
    def replace_fill(match):
        fill_value = match.group(1)
        if fill_value == 'none':
            return match.group(0)  # 保持 fill="none" 不变
        return f'fill="{color}"'
    
    # 替换所有 fill 属性（除了 fill="none"）
    svg_content = re.sub(r'fill="([^"]*)"', replace_fill, svg_content)
    svg_content = re.sub(r"fill='([^']*)'", lambda m: f'fill="{color}"' if m.group(1) != 'none' else m.group(0), svg_content)
    
    # 创建临时 SVG 渲染器
    renderer = QSvgRenderer(svg_content.encode('utf-8'))
    
    # 创建 pixmap 并渲染
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer.render(painter)
    painter.end()
    
    return QIcon(pixmap)

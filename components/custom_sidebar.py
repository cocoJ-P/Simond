
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
                 icon_regular_path: str = None, icon_filled_path: str = None):
        super().__init__()
        self.text = text
        self._is_selected = False
        self._is_hovered = False
        
        # 图标路径
        self.icon_regular_path = icon_regular_path
        self.icon_filled_path = icon_filled_path
        
        self.setFixedHeight(60)
    
        self.setup_vertical_layout()
     
        
        # 设置文本和图标布局
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: palette(window-text);
                border-radius: 6px;
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
        self.text_label.setStyleSheet("font-size: 10px; color: palette(window-text); font-weight: bold;")
        container_layout.addWidget(self.text_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        # 将容器添加到按钮（通过设置按钮的布局）
        btn_layout = QVBoxLayout(self)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_layout.addWidget(container, alignment=Qt.AlignmentFlag.AlignCenter)

    
    def update_icon(self):
        """根据 hover 和选中状态更新图标"""
        app = QApplication.instance()
        if not app:
            return

        palette = QApplication.instance().palette()
        
        highlight_color = palette.color(QPalette.ColorRole.Highlight).name()
        hover_color = palette.color(QPalette.ColorRole.WindowText).name()     # hover 时
        # 判断当前是深色主题还是浅色主题
        window_color = palette.color(QPalette.ColorRole.Window)
        is_dark_theme = window_color.lightness() < 128   # 0~255，越小越暗

        if is_dark_theme:
            # 深色模式：用更亮一点的灰（Midlight）
            idle_qcolor = palette.color(QPalette.ColorRole.Midlight)
        else:
            # 浅色模式：用正常灰（Mid）
            idle_qcolor = palette.color(QPalette.ColorRole.Mid)

        idle_color = idle_qcolor.name()

        # 初始化变量
        icon = None
        text_color = None

        # 选中状态 → 使用系统高亮色
        if self._is_selected and self.icon_filled_path:
            if os.path.exists(self.icon_filled_path):
                icon = load_svg_icon_with_color(self.icon_filled_path, highlight_color, 28)
                text_color = highlight_color

        # hover 未选中 → 使用系统文本色（浅色模式深黑，深色模式白）
        elif self._is_hovered and not self._is_selected and self.icon_regular_path:
            if os.path.exists(self.icon_regular_path):
                icon = load_svg_icon_with_color(self.icon_regular_path, hover_color, 28)
                text_color = hover_color

        # idle → 使用系统灰色
        elif self.icon_regular_path:
            if os.path.exists(self.icon_regular_path):
                icon = load_svg_icon_with_color(self.icon_regular_path, idle_color, 28)
                text_color = idle_color

        # 设置到 QLabel
        if hasattr(self, 'icon_label') and icon:
            pixmap = icon.pixmap(28, 28)
            self.icon_label.setPixmap(pixmap)
        elif hasattr(self, 'icon_label'):
            self.icon_label.clear()
        
        # 更新文字标签颜色，使其与图标颜色一致
        if hasattr(self, 'text_label') and text_color and not self._is_selected:
            self.text_label.setStyleSheet(f"font-size: 10px; color: {text_color}; font-weight: bold;")

    
    # 针对按钮图标的样式监控，根据鼠标是否进入或离开，更新图标显示
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
                    color: palette(window-text);
                    border-radius: 6px;
                }
          
            """
            self.setStyleSheet(style)
            if hasattr(self, 'text_label'):
                # 选中时隐藏文字标签，只显示图标
                self.text_label.hide()
        else:
            style = """
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: palette(window-text);
                    border-radius: 6px;

                }
   
                QPushButton:pressed {
                    background-color: palette(mid);
                }
            """
            self.setStyleSheet(style)
            if hasattr(self, 'text_label'):
                # 未选中时显示文字标签（颜色由 update_icon() 控制）
                self.text_label.show()


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
        # 设置侧边栏宽度（默认70像素）
        self.setFixedWidth(70)
        
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
            icon_filled_path=home_icon_filled
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
            icon_filled_path=local_icon_filled
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
            icon_filled_path=my_space_icon_filled
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
            icon_filled_path=in_progress_icon_filled
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
            icon_filled_path=settings_icon_filled
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

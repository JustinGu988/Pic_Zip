import ctypes
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from zip_logic import start_conversion, METHOD_MSPAINT, METHOD_PILLOW

# 结构：
# App (tk.Tk)  <-- 创建和切换页面
#  │
#  ├── MethodPage (tk.Frame)  <-- 选取方式页面
#  │
#  ├── BaseSettingsPage (tk.Frame)  <-- 公共
#  │     │
#  │     ├── PillowSettingsPage  <-- 继承，扩展特有参数
#  │     └── MsSettingsPage      <-- 继承，扩展特有参数
#  │
#  └── ResultPage (tk.Frame)  <-- 结果页面


class App(tk.Tk):
    # 主程序控制器，继承自tk.Tk
    def __init__(self):
        # 开启DPI感知，解决2K/4K屏幕显示问题
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass  # 如果不是Windows系统，忽略

        super().__init__()
        self.title("图片处理工具")
        self.resizable(True, True)

        # 用于存储页面的容器
        self._frames = {}

        # 初始化页面并放入容器
        for F in (MethodPage, PillowSettingsPage, MsSettingsPage, ResultPage):
            page_name = F.__name__
            frame = F(parent=self, controller=self)
            self._frames[page_name] = frame
            # 将所有页面叠放在同一位置
            frame.grid(row=0, column=0, sticky="nsew")

        # 让主窗口的第0行和第0列拥有“弹性权重”
        # 这样拉伸主窗口时，主窗口会把多出来的空间分配给放在(0,0)位置的页面
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 默认显示第一个页面
        self.show_frame("MethodPage")

    # 让窗口根据内部控件自适应大小，并居中显示在屏幕正中央
    def center_window(self):
        self.update_idletasks()  # 强制刷新，让 Tkinter 算出真实的宽高
        w = self.winfo_width()  # 获取窗口实际宽度
        h = self.winfo_height()  # 获取窗口实际高度

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        x = (screen_w // 2) - (w // 2)
        y = (screen_h // 2) - (h // 2)

        # 只设置位置，不设置固定大小
        self.geometry(f"+{x}+{y}")

    # 切换到指定页面
    def show_frame(self, page_name):
        frame = self._frames[page_name]
        frame.tkraise()  # 将目标页面提升到最前面
        self.center_window()  # 每次切换页面重新居中

    def show_result(self, logs_text):
        self.show_frame("ResultPage")
        self._frames["ResultPage"].show_logs(logs_text)


class MethodPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="选择图片转存方式：", font=("Microsoft YaHei", 11)).pack(
            pady=15
        )

        self.var_choice = tk.StringVar(value=METHOD_PILLOW)
        tk.Radiobutton(
            self, text="Pillow", variable=self.var_choice, value=METHOD_PILLOW
        ).pack(anchor="w", padx=60)
        tk.Radiobutton(
            self, text="MSPaint", variable=self.var_choice, value=METHOD_MSPAINT
        ).pack(anchor="w", padx=60)

        tk.Button(
            self,
            text="确认",
            command=self.confirm_choice,
            bg="#4CAF50",
            fg="white",
            width=10,
        ).pack(pady=15)

    def confirm_choice(self):
        selected = self.var_choice.get()
        if selected == METHOD_PILLOW:
            self.controller.show_frame("PillowSettingsPage")
        elif selected == METHOD_MSPAINT:
            self.controller.show_frame("MsSettingsPage")
        else:
            messagebox.showinfo("提示", "Method Selection错误")


class BaseSettingsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # 文件夹路径
        tk.Label(self, text="文件夹路径:").grid(row=0, column=0, sticky="e", pady=5)
        self.entry_path = tk.Entry(self, width=40)
        self.entry_path.grid(row=0, column=1, columnspan=3, sticky="w", padx=5)
        tk.Button(self, text="浏览...", command=self.browse_folder).grid(
            row=0, column=4, padx=5
        )

        # 勾选框
        self.var_jpg = tk.BooleanVar(value=False)
        self.var_png = tk.BooleanVar(value=False)
        tk.Checkbutton(self, text="压缩 JPG", variable=self.var_jpg).grid(
            row=1, column=1, sticky="w"
        )
        tk.Checkbutton(self, text="转存 PNG→JPG", variable=self.var_png).grid(
            row=2, column=1, sticky="w"
        )

        # 大小范围
        tk.Label(self, text="大小范围 (MB):").grid(row=3, column=0, sticky="e", pady=5)
        self.entry_valid_size_min = tk.Entry(self, width=10)
        self.entry_valid_size_min.insert(0, "0.1")
        self.entry_valid_size_min.grid(row=3, column=1, sticky="w", padx=5)
        tk.Label(self, text="to ").grid(row=3, column=2)
        self.entry_valid_size_max = tk.Entry(self, width=10)
        self.entry_valid_size_max.insert(0, "20")
        self.entry_valid_size_max.grid(row=3, column=3, sticky="w")

    def browse_folder(self):
        folder = filedialog.askdirectory(title="选择图片文件夹")
        self.entry_path.delete(0, tk.END)
        self.entry_path.insert(0, folder)


class PillowSettingsPage(BaseSettingsPage):
    # GUI结构：
    # grid()
    # ├─ 第0~3行：[继承自 BaseSettingsPage 的公共控件]
    # │    ├─ 第0行：Label("文件夹路径:")...
    # │    ├─ 第1行：Checkbutton("压缩 JPG")
    # │    ├─ 第2行：Checkbutton("转存 PNG→JPG")
    # │    └─ 第3行：Label("大小范围 (MB):")...
    # ├─ 第4行：Label("JPEG 质量")...
    # ├─ 第5行：Label("色度抽样")...
    # └─ 第6行：btn_frame (tk.Frame) [columnspan=5, 跨越所有列]
    #     pack()
    #     ├─ 左侧：Button("返回")
    #     └─ 左侧：Button("确认并开始")
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # Pillow 特有参数
        tk.Label(self, text="JPEG 质量 (0-100):").grid(
            row=4, column=0, sticky="e", pady=5
        )
        self.entry_quality = tk.Entry(self, width=10)
        self.entry_quality.insert(0, "97")
        self.entry_quality.grid(row=4, column=1, sticky="w", padx=5)

        tk.Label(self, text="色度抽样 (0=4:4:4, 1=4:2:2, 2=4:2:0):").grid(
            row=5, column=0, sticky="e", pady=5
        )
        self.entry_subsampling = tk.Entry(self, width=10)
        self.entry_subsampling.insert(0, "0")
        self.entry_subsampling.grid(row=5, column=1, sticky="w", padx=5)

        # 按钮区域
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=6, column=0, columnspan=5, pady=20)
        tk.Button(
            btn_frame,
            text="返回",
            command=lambda: controller.show_frame("MethodPage"),
            width=10,
        ).pack(side="left", padx=10)
        tk.Button(
            btn_frame,
            text="确认并开始",
            command=self.confirm,
            width=20,
            bg="#4CAF50",
            fg="white",
        ).pack(side="left", padx=10)

    def confirm(self):
        # 收集参数并调用逻辑
        confirm_delete = messagebox.askokcancel(
            "确认操作", "开始处理后将删除原始图片文件。\n是否继续？", icon="warning"
        )
        if confirm_delete:
            start_conversion(
                METHOD_PILLOW,
                self.entry_path.get(),
                self.var_jpg.get(),
                self.var_png.get(),
                float(self.entry_valid_size_min.get()) * 1024 * 1024,
                float(self.entry_valid_size_max.get()) * 1024 * 1024,
                int(self.entry_quality.get()),
                int(self.entry_subsampling.get()),
            )
            from zip_logic import interceptor

            logs = "\n".join(interceptor.output)
            self.controller.show_result(logs)


class MsSettingsPage(BaseSettingsPage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # MSPaint 特有参数
        tk.Label(self, text="下拉单上移次数:").grid(row=4, column=0, sticky="e", pady=5)
        self.entry_jpg_press_up = tk.Entry(self, width=10)
        self.entry_jpg_press_up.insert(0, "3")
        self.entry_jpg_press_up.grid(row=4, column=1, sticky="w", padx=5)

        tk.Label(self, text="下拉单下移次数:").grid(row=5, column=0, sticky="e", pady=5)
        self.entry_jpg_press_dw = tk.Entry(self, width=10)
        self.entry_jpg_press_dw.insert(0, "0")
        self.entry_jpg_press_dw.grid(row=5, column=1, sticky="w", padx=5)

        # 按钮区域
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=6, column=0, columnspan=5, pady=20)
        tk.Button(
            btn_frame,
            text="返回",
            command=lambda: controller.show_frame("MethodPage"),
            width=10,
        ).pack(side="left", padx=10)
        tk.Button(
            btn_frame,
            text="确认并开始",
            command=self.confirm,
            width=20,
            bg="#4CAF50",
            fg="white",
        ).pack(side="left", padx=10)

    def confirm(self):
        # 收集参数并调用逻辑
        confirm_delete = messagebox.askokcancel(
            "确认操作", "开始处理后将删除原始图片文件。\n是否继续？", icon="warning"
        )
        if confirm_delete:
            start_conversion(
                METHOD_MSPAINT,
                self.entry_path.get(),
                self.var_jpg.get(),
                self.var_png.get(),
                float(self.entry_valid_size_min.get()) * 1024 * 1024,
                float(self.entry_valid_size_max.get()) * 1024 * 1024,
                int(self.entry_jpg_press_up.get()),
                int(self.entry_jpg_press_dw.get()),
            )
            from zip_logic import interceptor

            logs = "\n".join(interceptor.output)
            self.controller.show_result(logs)


class ResultPage(tk.Frame):
    # GUI结构：
    #   grid()
    #   ├─ 第0行：Label("压缩执行结果")
    #   ├─ 第1行：text_frame (tk.Frame)
    #   │    pack()
    #   │    ├─ 左侧：self.text_area (tk.Text)
    #   │    └─ 右侧：scrollbar (tk.Scrollbar)
    #   └─ 第2行：Button("返回设置页")
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # 让第1行和第0列具有弹性权重
        # 这样当窗口拉伸时，第1行的控件会跟着变大
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        tk.Label(self, text="压缩执行结果", font=("Microsoft YaHei", 12, "bold")).grid(
            row=0, column=0, pady=10
        )

        text_frame = tk.Frame(self)
        # 让text_frame填满剩余空间，并随窗口拉伸
        text_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.text_area = tk.Text(text_frame, wrap="none", font=("Consolas", 10))
        v_scrollbar = tk.Scrollbar(text_frame, command=self.text_area.yview)
        h_scrollbar = tk.Scrollbar(
            text_frame, orient="horizontal", command=self.text_area.xview
        )
        self.text_area.config(
            yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set
        )

        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        self.text_area.pack(side="left", fill="both", expand=True)

        tk.Button(
            self,
            text="返回设置页",
            command=lambda: controller.show_frame("PillowSettingsPage"),
            bg="#2196F3",
            fg="white",
            width=15,
        ).grid(row=2, column=0, pady=10)

    def show_logs(self, logs_text):
        self.text_area.config(state="normal")
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", logs_text)
        self.text_area.config(state="disabled")
        self.text_area.see(tk.END)  # 视图滚动到文本框的最底部

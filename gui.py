import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from zip_logic import start_conversion, METHOD_MSPAINT, METHOD_PILLOW

# 文件包含三个GUI页面
#   - 首页：选取转存方式
#   - Pillow页面
#   - MSPaint页面


# GUI页面：选取转存方式
def get_method_gui():
    def confirm_choice():
        selected_value = var_choice.get()
        root.destroy()

    root = tk.Tk()
    root.title("选择转存方式")
    root.geometry("300x180")

    # Default value
    var_choice = tk.StringVar(value="pillow")

    tk.Label(root, text="选择图片转存方式：", font=("Microsoft YaHei", 11)).pack(
        pady=15
    )
    tk.Radiobutton(root, text="Pillow", variable=var_choice, value=METHOD_PILLOW).pack(
        anchor="w", padx=60
    )
    tk.Radiobutton(
        root, text="MSPaint", variable=var_choice, value=METHOD_MSPAINT
    ).pack(anchor="w", padx=60)
    tk.Button(
        root, text="确认", command=confirm_choice, bg="#4CAF50", fg="white", width=10
    ).pack(pady=15)

    # 启动事件循环，程序会在这里暂停，直到 root.destroy() 被调用
    root.mainloop()

    # 窗口关闭后，返回选择（pillow or mspaint）
    return var_choice.get()


# GUI页面：Pillow转存
def get_pillow_settings():
    def browse_folder():
        folder = filedialog.askdirectory(title="选择图片文件夹")
        entry_path.delete(0, tk.END)
        entry_path.insert(0, folder)

    def confirm():
        folder_path = entry_path.get()
        zip_jpg = var_jpg.get()
        zip_png = var_png.get()
        valid_size = float(entry_valid_size.get()) * 1024 * 1024
        pillow_quality = int(entry_quality.get())
        pillow_subsampling = int(entry_subsampling.get())

        # GUI调用压缩Function
        confirm_delete = messagebox.askokcancel(
            "确认操作", "开始处理后将删除原始图片文件。\n是否继续？", icon="warning"
        )

        if confirm_delete:
            root.destroy()
            start_conversion(
                METHOD_PILLOW,
                folder_path,
                zip_jpg,
                zip_png,
                valid_size,
                pillow_quality,
                pillow_subsampling,
            )

    root = tk.Tk()
    root.title("图片压缩设置")
    root.geometry("840x320")

    # 文件夹路径
    tk.Label(root, text="文件夹路径:").grid(row=0, column=0, sticky="e", pady=5)
    entry_path = tk.Entry(root, width=40)
    entry_path.grid(row=0, column=1, padx=5)
    tk.Button(root, text="浏览...", command=browse_folder).grid(row=0, column=2, padx=5)

    # 勾选框
    var_jpg = tk.BooleanVar(value=False)
    var_png = tk.BooleanVar(value=False)
    tk.Checkbutton(root, text="压缩 JPG", variable=var_jpg).grid(
        row=1, column=1, sticky="w"
    )
    tk.Checkbutton(root, text="转存 PNG→JPG", variable=var_png).grid(
        row=2, column=1, sticky="w"
    )

    # 数值输入
    tk.Label(root, text="最小有效大小 (MB):").grid(row=3, column=0, sticky="e", pady=5)
    entry_valid_size = tk.Entry(root, width=10)
    entry_valid_size.insert(0, "0.1")
    entry_valid_size.grid(row=3, column=1, sticky="w")

    tk.Label(root, text="JPEG 质量 (0-100):").grid(row=4, column=0, sticky="e", pady=5)
    entry_quality = tk.Entry(root, width=10)
    entry_quality.insert(0, "95")
    entry_quality.grid(row=4, column=1, sticky="w")

    tk.Label(root, text="色度抽样 (0=4:4:4, 1=4:2:2, 2=4:2:0):").grid(
        row=5, column=0, sticky="e", pady=5
    )
    entry_subsampling = tk.Entry(root, width=10)
    entry_subsampling.insert(0, "0")
    entry_subsampling.grid(row=5, column=1, sticky="w")

    tk.Button(
        root, text="确认并开始", command=confirm, width=20, bg="#4CAF50", fg="white"
    ).grid(row=6, column=1, pady=20)

    root.mainloop()


# GUI页面：MSPaint转存
def get_mspaint_settings():
    def browse_folder():
        folder = filedialog.askdirectory(title="选择图片文件夹")
        entry_path.delete(0, tk.END)
        entry_path.insert(0, folder)

    def confirm():
        folder_path = entry_path.get()
        zip_jpg = var_jpg.get()
        zip_png = var_png.get()
        valid_size = float(entry_valid_size.get()) * 1024 * 1024
        list_press_up = int(entry_jpg_press_up.get())
        list_press_dw = int(entry_jpg_press_dw.get())

        # GUI调用压缩Function
        confirm_delete = messagebox.askokcancel(
            "确认操作", "开始处理后将删除原始图片文件。\n是否继续？", icon="warning"
        )

        if confirm_delete:
            root.destroy()
            start_conversion(
                METHOD_MSPAINT,
                folder_path,
                zip_jpg,
                zip_png,
                valid_size,
                list_press_up,
                list_press_dw,
            )

    root = tk.Tk()
    root.title("图片压缩设置")
    root.geometry("760x300")

    # 文件夹路径
    tk.Label(root, text="文件夹路径:").grid(row=0, column=0, sticky="e", pady=5)
    entry_path = tk.Entry(root, width=40)
    entry_path.grid(row=0, column=1, padx=5)
    tk.Button(root, text="浏览...", command=browse_folder).grid(row=0, column=2, padx=5)

    # 勾选框
    var_jpg = tk.BooleanVar(value=False)
    var_png = tk.BooleanVar(value=False)
    tk.Checkbutton(root, text="转存 JPG", variable=var_jpg).grid(
        row=1, column=1, sticky="w"
    )
    tk.Checkbutton(root, text="转存 PNG→JPG", variable=var_png).grid(
        row=2, column=1, sticky="w"
    )

    # 数值输入
    tk.Label(root, text="最小有效大小 (MB):").grid(row=3, column=0, sticky="e", pady=5)
    entry_valid_size = tk.Entry(root, width=10)
    entry_valid_size.insert(0, "0.1")
    entry_valid_size.grid(row=3, column=1, sticky="w")

    tk.Label(root, text="下拉单上移次数:").grid(row=4, column=0, sticky="e", pady=5)
    entry_jpg_press_up = tk.Entry(root, width=10)
    entry_jpg_press_up.insert(0, "3")
    entry_jpg_press_up.grid(row=4, column=1, sticky="w")

    tk.Label(root, text="下拉单下移次数:").grid(row=5, column=0, sticky="e", pady=5)
    entry_jpg_press_dw = tk.Entry(root, width=10)
    entry_jpg_press_dw.insert(0, "0")
    entry_jpg_press_dw.grid(row=5, column=1, sticky="w")

    tk.Button(
        root, text="确认并开始", command=confirm, width=20, bg="#4CAF50", fg="white"
    ).grid(row=6, column=1, pady=20)

    root.mainloop()

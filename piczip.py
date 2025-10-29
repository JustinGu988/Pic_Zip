import os
import pyautogui  # pip install pyautogui
import time
import subprocess
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image

METHOD_PILLOW = "P"
METHOD_MSPAINT = "M"


# 转存功能：判定条件、选取转存方法、输出size变化
def start_conversion(
    conversion_method,
    folder_path,
    ZIP_JPG,
    ZIP_PNG,
    valid_size,
    PILLOW_QUALITY,
    PILLOW_SUBSAMPLING,
):

    # 控制台输出size变化
    def print_output(original_size, new_size, convert_type, file_name):
        ratio = (new_size - original_size) / original_size * 100
        print(
            f"{original_size/1024/1024:.2f} MB → "
            + f"{new_size/1024/1024:.2f} MB ({ratio:.1f}%): "
            + f"{convert_type}, {file_name}"
        )

    # 确保路径存在
    if not os.path.isdir(folder_path):
        print(f"目录不存在: {folder_path}")
        return

    print(f"开始遍历文件夹中的图片: {folder_path}\n")

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        original_size = os.path.getsize(file_path)

        # 设定文件类型（避免选取文件夹）
        valid_file = file_name.lower().endswith((".jpg", ".png"))

        # 判断文件类型和大小
        if valid_file and (original_size <= valid_size):
            print_output(original_size, original_size, "  <MB  ", file_name)

        elif valid_file and (original_size > valid_size):
            if file_name.lower().endswith(".jpg") and ZIP_JPG:
                new_path = allocate_conversion_method(
                    conversion_method,
                    "jpg",
                    file_path,
                    PILLOW_QUALITY,
                    PILLOW_SUBSAMPLING,
                )
                new_size = os.path.getsize(new_path)
                print_output(
                    original_size, new_size, "  JPG  ", os.path.basename(new_path)
                )

            elif file_name.lower().endswith(".png") and ZIP_PNG:
                new_path = allocate_conversion_method(
                    conversion_method,
                    "png",
                    file_path,
                    PILLOW_QUALITY,
                    PILLOW_SUBSAMPLING,
                )
                new_size = os.path.getsize(new_path)
                print_output(
                    original_size, new_size, "PNG→JPG", os.path.basename(new_path)
                )


# 转存功能：根据 conversion_method、file_type 选取转存方法
def allocate_conversion_method(
    conversion_method, file_type, file_path, PILLOW_QUALITY, PILLOW_SUBSAMPLING
):
    # 用pillow压缩jpg
    def jpg_pillow(file_path):
        new_path = os.path.splitext(file_path)[0] + "_dwnsiz.jpg"
        with Image.open(file_path) as img:
            img.save(
                new_path,
                format="JPEG",
                quality=PILLOW_QUALITY,
                subsampling=PILLOW_SUBSAMPLING,
                optimize=True,
                progressive=True,
            )
        os.remove(file_path)  # 删除原始文件
        return new_path

    # 用pillow压缩png
    def png_pillow(file_path):
        # 生成输出路径
        output_dir = os.path.join(os.path.dirname(file_path), "pngToJpg")
        os.makedirs(output_dir, exist_ok=True)

        # 生成目标文件名
        jpg_path = os.path.join(
            output_dir, os.path.splitext(os.path.basename(file_path))[0] + "_dwnsiz.jpg"
        )

        with Image.open(file_path) as img:
            rgb_img = img.convert("RGB")
            rgb_img.save(
                jpg_path,
                format="JPEG",
                quality=PILLOW_QUALITY,
                subsampling=PILLOW_SUBSAMPLING,
                optimize=True,
                progressive=True,
            )

        os.remove(file_path)  # 删除原始 PNG
        return jpg_path

    if conversion_method == METHOD_PILLOW and file_type == "jpg":
        return jpg_pillow(file_path)
    elif conversion_method == METHOD_PILLOW and file_type == "png":
        return png_pillow(file_path)
    else:
        raise ValueError(
            f"allocate_conversion_method() 无法判定: conversion_method={conversion_method}, file_type={file_type}"
        )


# GUI页面：选取转存方式
def get_method_gui():
    def confirm_choice():
        global CHOOSE_METHOD
        CHOOSE_METHOD = var_choice.get()
        root.destroy()

    root = tk.Tk()
    root.title("选择转存方式")
    root.geometry("300x180")

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

    root.mainloop()


# GUI页面：Pillow转存
def get_pillow_settings():
    def browse_folder():
        folder = filedialog.askdirectory(title="选择图片文件夹")
        entry_path.delete(0, tk.END)
        entry_path.insert(0, folder)

    def confirm():
        global ORIGINAL_FOLDER_PATH, ZIP_JPG, ZIP_PNG, VALID_SIZE, PILLOW_QUALITY, PILLOW_SUBSAMPLING
        ORIGINAL_FOLDER_PATH = entry_path.get()
        ZIP_JPG = var_jpg.get()
        ZIP_PNG = var_png.get()
        VALID_SIZE = int(entry_valid_size.get()) * 1024 * 1024
        PILLOW_QUALITY = int(entry_quality.get())
        PILLOW_SUBSAMPLING = int(entry_subsampling.get())

        # GUI调用压缩Function
        confirm_delete = messagebox.askokcancel(
            "确认操作", "开始处理后将删除原始图片文件。\n是否继续？", icon="warning"
        )

        if confirm_delete:
            print(
                f"ORIGINAL_FOLDER_PATH = {ORIGINAL_FOLDER_PATH}, "
                + f"ZIP_JPG = {ZIP_JPG}, "
                + f"ZIP_PNG = {ZIP_PNG}, "
                + f"VALID_SIZE = {entry_valid_size}, "
                + f"PILLOW_QUALITY = {PILLOW_QUALITY}, "
                + f"PILLOW_SUBSAMPLING = {PILLOW_SUBSAMPLING}"
            )
            root.destroy()
            start_conversion(
                METHOD_PILLOW,
                ORIGINAL_FOLDER_PATH,
                ZIP_JPG,
                ZIP_PNG,
                VALID_SIZE,
                PILLOW_QUALITY,
                PILLOW_SUBSAMPLING,
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
    var_jpg = tk.BooleanVar(value=True)
    var_png = tk.BooleanVar(value=True)
    tk.Checkbutton(root, text="压缩 JPG", variable=var_jpg).grid(
        row=1, column=1, sticky="w"
    )
    tk.Checkbutton(root, text="转存 PNG→JPG", variable=var_png).grid(
        row=2, column=1, sticky="w"
    )

    # 数值输入
    tk.Label(root, text="最小有效大小 (MB):").grid(row=3, column=0, sticky="e", pady=5)
    entry_valid_size = tk.Entry(root, width=10)
    entry_valid_size.insert(0, "2")
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
def jpg_use_mspaint(file_path):
    # 打开画图
    subprocess.Popen(["mspaint.exe", file_path])
    time.sleep(1.5)  # 等待画图启动

    # 模拟按键 Ctrl+S 保存
    pyautogui.hotkey("ctrl", "s")
    time.sleep(0.5)

    # 关闭画图
    pyautogui.hotkey("alt", "f4")
    time.sleep(0.5)


# 调用 GUI 获取输入
get_method_gui()
if CHOOSE_METHOD == METHOD_PILLOW:
    get_pillow_settings()

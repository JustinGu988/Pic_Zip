import os
import pyautogui  # pip install pyautogui
import time
import subprocess
from PIL import Image

# 开关
ORIGINAL_FOLDER_PATH = r"C:\Users\Administrator\Desktop\test"
ZIP_JPG = True
ZIP_PNG = True

# PILLOW 压缩设定
PILLOW_QUALITY = 95  # 质量
PILLOW_SUBSAMPLING = 0  # 色度抽样, 0 = 4:4:4, 1 = 4:2:2, 2 = 4:2:0


def compress_jpgs(folder_path):
    # 确保路径存在
    if not os.path.isdir(folder_path):
        print(f"目录不存在: {folder_path}")
        return

    print(f"开始遍历文件夹中的 JPG PNG: {folder_path}\n")

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        original_size = os.path.getsize(file_path)
        valid_file = file_name.lower().endswith((".jpg", ".png"))
        valid_size = 2 * 1024 * 1024  # 2MB

        # 判断文件类型和大小
        if valid_file & (original_size <= valid_size):
            print_output(original_size, original_size, "  <=2MB  ", file_name)

        elif valid_file & (original_size > valid_size):

            # 处理JPG
            if file_name.lower().endswith(".jpg") & ZIP_JPG:
                # 调用方法
                jpg_use_pillow(file_path)
                new_size = os.path.getsize(file_path)
                print_output(original_size, new_size, "  JPG  ", file_name)

            # 处理PNG
            elif file_name.lower().endswith(".png") & ZIP_PNG:
                jpg_path = png_use_pillow(file_path)
                new_size = os.path.getsize(jpg_path)
                print_output(original_size, new_size, "PNG→JPG", file_name)
                # os.remove(file_path)  # 删除原始 PNG


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


def jpg_use_pillow(file_path):
    with Image.open(file_path) as img:
        img.save(
            file_path,  # 覆盖原文件
            format="JPEG",
            quality=PILLOW_QUALITY,
            subsampling=PILLOW_SUBSAMPLING,
            optimize=True,  # 优化 Huffman 表
            progressive=True,  # 渐进式 JPEG
        )


def png_use_pillow(file_path):
    # 生成输出路径
    output_dir = os.path.join(os.path.dirname(file_path), "pngToJpg")
    os.makedirs(
        output_dir, exist_ok=True
    )  # 自动创建 pngToJpg 文件夹（如果已存在就忽略）

    # 转换的JPG图片存入pngToJpg，并覆盖同名文件
    jpg_path = os.path.join(
        os.path.dirname(file_path),  # 取到当前 PNG 所在的文件夹路径
        "pngToJpg",  # 在这个路径下新建一个子文件夹 pngToJpg
        os.path.splitext(os.path.basename(file_path))[0]
        + ".jpg",  # PNG 文件名去掉扩展名，加上 .jpg
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
    return jpg_path


def print_output(original_size, new_size, convert_type, file_name):
    ratio = (new_size - original_size) / original_size * 100
    print(
        f"{original_size/1024/1024:.2f} MB → "
        + f"{new_size/1024/1024:.2f} MB ({ratio:.1f}%): "
        + f"{convert_type}, {file_name}"
    )


# 使用方法：替换为你的文件夹路径
compress_jpgs(f"{ORIGINAL_FOLDER_PATH}")

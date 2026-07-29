import os
import re
import sys
import random
import time
import subprocess
import pyautogui  # pip install pyautogui
import pyperclip  # pip install pyperclip
from PIL import Image  # python -m pip install pillow
from datetime import datetime

METHOD_PILLOW = "P"
METHOD_MSPAINT = "M"
TYPE_JPG = "jpg"
TYPE_PNG = "png"

# 结构：
# OutputInterceptor (Class)  <-- 全局print拦截器 (内存 + 本地txt)
#  │
#  └── sys.stdout = interceptor  <-- 被start_conversion, shorten_tails接管
#
# start_conversion()
#  │  ├─ 步骤逻辑：
#  │  ├─ 1. 遍历文件夹 & 过滤条件 (类型、大小)
#  │  ├─ 2. 调用 allocate_conversion_method() 分发任务
#  │  └─ 3. 调用 print_output() 格式化输出
#  │
#  └── allocate_conversion_method()  <-- 转存，重命名，删除原文件
#        │
#        ├── Pillow
#        └── MSPaint
#
# shorten_tails()
#  │
#  ├── and_x_more
#  └── tails


# 定义并实例化全局拦截器，用于拦截print内容
class OutputInterceptor:
    def __init__(self):
        self.output = []
        # 打开 output_log.txt，'a' 模式表示追加写入（文件不存在会自动创建）
        # encoding='utf-8' 确保中文不会乱码
        self.log_file = open("output_log.txt", "a", encoding="utf-8")

    def write(self, text):
        if text.strip():
            self.output.append(text)
            # 将内容同时写入到本地的 txt 文件中
            self.log_file.write(text + "\n")
            self.log_file.flush()

    def flush(self):
        if not self.log_file.closed:
            self.log_file.close()


interceptor = OutputInterceptor()


def start_conversion(
    conversion_method,
    folder_path,
    zip_jpg,
    zip_png,
    valid_size_min,
    valid_size_max,
    var_1,  # for pillow: pillow_quality; for png: jpg_list_press_up
    var_2,  # for pillow: pillow_subsampling; for png: jpg_list_press_dw
):

    # 将print指向拦截器
    sys.stdout = interceptor

    # 格式化输出逻辑
    def print_output(original_size, new_size, convert_type, file_name):
        if original_size == 0:
            ratio = 0
        else:
            ratio = (new_size - original_size) / original_size * 100

        ratio_display = f"{'++++++' if ratio > 0 and original_size != 0 else f'{ratio:>6.1f}'}"  # 宽度6，1位小数

        # 格式化输出
        # {value:>W.Pf} 含义:
        # > : 右对齐 (< 左对齐，^ 居中)
        # W : 总宽度 (包含数字、小数点和单位)
        # .P : 保留的小数位数
        # f : 浮点数
        # 示例：
        # 23.45 MB →  50.00 MB (+146.9%): filename1
        #  1.20 MB →   0.50 MB (+140.0%): filename2
        log_text = (
            f"{convert_type:^7} "
            f"{original_size/1024/1024:>5.2f} MB →"  # 宽度5，2位小数
            f"{new_size/1024/1024:>6.2f} MB ("  # 宽度5，2位小数
            f"{ratio_display}%): "
            f"{file_name}"
        )
        # 输出到拦截器
        print(log_text, end="")

    # 确保路径存在
    if not os.path.isdir(folder_path):
        print(f"目录不存在: {folder_path}")
        return

    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"\n{current_time}", f"开始遍历文件夹中的图片: {folder_path}")
    print(
        f"conversion_method: {conversion_method};",
        f"zip_jpg: {zip_jpg};",
        f"zip_png: {zip_png};",
        f"valid_size_min: {valid_size_min/1024/1024};",
        f"valid_size_max: {valid_size_max/1024/1024};",
        f"var_1: {var_1};",
        f"var_2: {var_2}",
    )

    # 遍历，分发任务，结果输出
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        original_size = os.path.getsize(file_path)

        # 设定文件类型判定（避免选取文件夹）
        valid_pic_file = file_name.lower().endswith((".jpg", ".png", "jfif"))
        valid_jpg = file_name.lower().endswith(".jpg")
        valid_png = file_name.lower().endswith(".png")
        valid_size = valid_size_min <= original_size <= valid_size_max

        # 判断大小、类型
        if any(
            [
                not valid_pic_file,
                valid_jpg and not zip_jpg,
                valid_png and not zip_png,
            ]
        ):
            continue

        elif valid_pic_file and not valid_size:
            print_output(original_size, original_size, "  <MB  ", file_name)

        elif valid_jpg and zip_jpg and valid_size:
            new_path = allocate_conversion_method(
                conversion_method, TYPE_JPG, file_path, var_1, var_2
            )
            new_size = os.path.getsize(new_path)
            print_output(original_size, new_size, "  JPG  ", os.path.basename(new_path))

        elif valid_png and zip_png and valid_size:
            new_path = allocate_conversion_method(
                conversion_method, TYPE_PNG, file_path, var_1, var_2
            )
            new_size = os.path.getsize(new_path)
            print_output(original_size, new_size, "PNG→JPG", os.path.basename(new_path))

        else:
            print_output(original_size, original_size, "FIL INV", file_name)


# 根据 conversion_method、file_type 选取转存方法
def allocate_conversion_method(conversion_method, file_type, file_path, var_1, var_2):
    # 用pillow转换jpg
    def pillow_jpg(file_path):
        new_path = os.path.splitext(file_path)[0] + "_plJ2J.jpg"
        with Image.open(file_path) as img:
            img.save(
                new_path,
                format="JPEG",
                quality=var_1,
                subsampling=var_2,
                optimize=True,
                progressive=True,
            )
        os.remove(file_path)  # 删除原始文件
        return new_path

    # 用pillow转换png为jpg
    def pillow_png(file_path):
        # 生成输出路径
        output_dir = os.path.join(os.path.dirname(file_path), "pl_pngToJpg")
        os.makedirs(output_dir, exist_ok=True)

        # 生成目标文件名
        jpg_path = os.path.join(
            output_dir, os.path.splitext(os.path.basename(file_path))[0] + "_plP2J.jpg"
        )

        with Image.open(file_path) as img:
            rgb_img = img.convert("RGB")
            rgb_img.save(
                jpg_path,
                format="JPEG",
                quality=var_1,
                subsampling=var_2,
                optimize=True,
                progressive=True,
            )

        os.remove(file_path)  # 删除原始 PNG
        return jpg_path

    # 用mspaint另存png为jpg
    def mspaint_png(file_path):
        folder = os.path.dirname(file_path)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        save_dir = os.path.join(folder, "ms_pngToJpg")
        os.makedirs(save_dir, exist_ok=True)
        new_file_name = f"{base_name}_msP2J.jpg"
        new_path = os.path.join(save_dir, new_file_name)
        list_press_up = var_1
        list_press_dw = var_2

        # 打开画图
        subprocess.Popen(["mspaint.exe", file_path])
        time.sleep(1.5)

        # 打开“另存为”窗口
        pyautogui.hotkey("f12")
        time.sleep(1.5)

        # 输入文件名
        pyperclip.copy(new_file_name)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.3)

        # 打开文件类型下拉框
        pyautogui.hotkey("alt", "t")
        time.sleep(0.3)

        # 选择JPEG类型
        pyautogui.press("down", presses=1, interval=0.3)  # 呼出下拉栏
        time.sleep(0.3)
        pyautogui.press(
            "up", presses=list_press_up, interval=0.3
        )  # 在下拉栏中向上选list_press_up个
        pyautogui.press(
            "down", presses=list_press_dw, interval=0.3
        )  # 在下拉栏中向下选list_press_dw个
        pyautogui.press("enter")
        time.sleep(0.3)

        # 选取另存为的文件夹
        pyperclip.copy(save_dir)
        pyautogui.hotkey("ctrl", "l")  # 聚焦地址栏
        time.sleep(0.3)
        pyautogui.hotkey("ctrl", "v")  # 粘贴文件夹路径
        time.sleep(0.3)
        pyautogui.press("enter")
        time.sleep(0.3)

        # 保存组合键
        pyautogui.hotkey("alt", "s")
        time.sleep(0.3)
        pyautogui.press("enter")  # 防止弹窗
        time.sleep(1)

        # 关闭画图
        pyautogui.hotkey("alt", "f4")
        time.sleep(0.5)

        # 等待保存完成，最多 3 秒
        for _ in range(6):
            if os.path.exists(new_path):
                # 删除原文件
                if os.path.exists(file_path):
                    os.remove(file_path)
                return new_path
            time.sleep(0.5)

        raise FileNotFoundError(f"MSPaint 未成功保存文件: {new_path}")

    # 用mspaint保存jpg
    def mspaint_jpg(file_path):
        # 打开画图
        subprocess.Popen(["mspaint.exe", file_path])
        time.sleep(1.5)

        # 执行“保存”覆盖原图
        pyautogui.hotkey("ctrl", "s")
        time.sleep(1)

        # 关闭画图
        pyautogui.hotkey("alt", "f4")
        time.sleep(0.5)

        # 确保文件依旧存在（简单检查）
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"保存失败：文件不存在 {file_path}")

        return file_path

    if conversion_method == METHOD_PILLOW and file_type == TYPE_JPG:
        return pillow_jpg(file_path)
    elif conversion_method == METHOD_PILLOW and file_type == TYPE_PNG:
        return pillow_png(file_path)
    elif conversion_method == METHOD_MSPAINT and file_type == TYPE_JPG:
        return mspaint_jpg(file_path)
    elif conversion_method == METHOD_MSPAINT and file_type == TYPE_PNG:
        return mspaint_png(file_path)
    else:
        raise ValueError(
            f"allocate_conversion_method() 无法判定: file_path={file_path}"
        )


def shorten_tails(folder_path, and_x_more, tails):
    if not os.path.exists(folder_path):
        print(f"目录不存在: {folder_path}")
        return

    # 将print指向拦截器
    sys.stdout = interceptor

    # 匹配带后缀的文件
    files = [
        f
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f)) and "." in f
    ]

    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"\nshorten_tails\n{current_time}", f"开始遍历文件夹中的图片: {folder_path}")

    for filename in files:
        name, ext = os.path.splitext(filename)
        new_name = name

        if and_x_more:
            # 使用正则匹配 and_数字_more_ 并替换为空
            new_name = re.sub(r"and_\d+_more_", "", new_name)

        if tails:
            # 定位最后一个 '__'，它后面直到结尾的内容就是 哈希值 + 后缀
            # 如果rfind找不到，会返回-1
            last_double_underscore_idx = new_name.rfind("__")

            if last_double_underscore_idx != -1:
                # 提取 '__' 后面的所有内容，例如 "855e...b289_msP2J" 或 "855e...b289"
                # [ ... : ] 代表 "一直截取到字符串的末尾"
                tail_part = new_name[last_double_underscore_idx + 2 :]

                # 用下划线分割，第一部分必定是哈希值，剩下的部分是后缀（如果有）
                # 123771166_p0_plP2J 变成 123771166 + _p0_plP2J
                tail_segments = tail_part.split("_", 1)
                original_hash = tail_segments[0]

                # 如果哈希长度大于10，则随机取4个字符
                if len(original_hash) > 10:
                    random_chars = "".join(random.sample(original_hash, 4))
                    new_tail_part = tail_part.replace(original_hash, random_chars, 1)
                    # 替换回主文件名
                    new_name = (
                        new_name[: last_double_underscore_idx + 2] + new_tail_part
                    )

        # 如果名字发生了改变，则执行重命名
        if new_name != name:
            old_path = os.path.join(folder_path, filename)
            new_path = os.path.join(folder_path, new_name + ext)

            # 防止重名覆盖
            counter = 1
            while os.path.exists(new_path):
                new_path = os.path.join(folder_path, f"{new_name}_{counter}{ext}")
                counter += 1

            try:
                os.rename(old_path, new_path)
                print(
                    f"original name:\n{filename}\nnew name:\n{os.path.basename(new_path)}\n"
                )
            except Exception as e:
                print(f"original name:\n{filename}\n错误:\n{e}\n")

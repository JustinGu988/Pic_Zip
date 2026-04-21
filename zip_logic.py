import os
import time
import subprocess
import pyautogui  # pip install pyautogui
import pyperclip  # pip install pyperclip
from PIL import Image

METHOD_PILLOW = "P"
METHOD_MSPAINT = "M"

# 转存分为以下步骤：
# start_conversion
#   - 判定条件：1.大小、2.文件类型
#   - 根据文件类型选取转存方法，allocate_conversion_method
# allocate_conversion_method
#   - 转存，重命名
#   - 删除原文件
# start_conversion
#   - print结果


# 1.判定条件、2.选取转存方法、3.print
def start_conversion(
    conversion_method,
    folder_path,
    zip_jpg,
    zip_png,
    valid_size,
    var_1,  # for pillow: pillow_quality; for png: jpg_list_press_up
    var_2,  # for pillow: pillow_subsampling; for png: jpg_list_press_dw
):

    # 控制台输出size变化
    def print_output(original_size, new_size, convert_type, file_name):
        if original_size == 0:
            ratio = 0
        else:
            ratio = (new_size - original_size) / original_size * 100

        ratio_display = f"{'++++++' if ratio >= 0 and original_size != 0 else f'{ratio:>6.1f}'}"  # 宽度6，1位小数

        # 格式化输出
        # {value:>W.Pf} 含义:
        # > : 右对齐 (< 左对齐，^ 居中)
        # W : 总宽度 (包含数字、小数点和单位)
        # .P : 保留的小数位数
        # f : 浮点数
        # 示例：
        # 23.45 MB →  50.00 MB (+146.9%): filename1
        #  1.20 MB →   0.50 MB (+140.0%): filename2
        print(
            f"{convert_type:^7} "
            f"{original_size/1024/1024:>5.2f} MB →"  # 宽度5，2位小数
            f"{new_size/1024/1024:>6.2f} MB ("  # 宽度5，2位小数
            f"{ratio_display}%): "
            f"{file_name}"
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
        valid_pic_file = file_name.lower().endswith((".jpg", ".png"))
        valid_jpg = file_name.lower().endswith(".jpg")
        valid_png = file_name.lower().endswith(".png")

        # 1. 判断文件大小
        # 2. 判断文件类型
        if valid_pic_file and original_size <= valid_size:
            print_output(original_size, original_size, "  <MB  ", file_name)

        elif valid_jpg and zip_jpg and original_size > valid_size:
            new_path = allocate_conversion_method(
                conversion_method, "jpg", file_path, var_1, var_2
            )
            new_size = os.path.getsize(new_path)
            print_output(original_size, new_size, "  JPG  ", os.path.basename(new_path))

        elif valid_png and zip_png and original_size > valid_size:
            new_path = allocate_conversion_method(
                conversion_method, "png", file_path, var_1, var_2
            )
            new_size = os.path.getsize(new_path)
            print_output(original_size, new_size, "PNG→JPG", os.path.basename(new_path))

        else:  # invalid file type
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
        time.sleep(2)

        # 输入文件名
        pyperclip.copy(new_file_name)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.3)

        # 打开文件类型下拉框
        pyautogui.hotkey("alt", "t")
        time.sleep(0.3)

        # 选择JPEG类型
        pyautogui.press("down", presses=1, interval=0.3)  # 呼出下拉栏
        time.sleep(0.5)
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

    if conversion_method == METHOD_PILLOW and file_type == "jpg":
        return pillow_jpg(file_path)
    elif conversion_method == METHOD_PILLOW and file_type == "png":
        return pillow_png(file_path)
    elif conversion_method == METHOD_MSPAINT and file_type == "jpg":
        return mspaint_jpg(file_path)
    elif conversion_method == METHOD_MSPAINT:
        return mspaint_png(file_path)
    else:
        raise ValueError(
            f"allocate_conversion_method() 无法判定: file_path={file_path}"
        )

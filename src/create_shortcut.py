# -*- coding: utf-8 -*-
"""在桌面创建带图标的快捷方式"""
import os
import sys
import subprocess

PROJ_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BAT_PATH = os.path.join(PROJ_ROOT, "start.bat")
ICO_PATH = os.path.join(PROJ_ROOT, "data", "dl_helper.ico")
DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")

def generate_icon():
    """生成一个简洁的 DL 图标 (32x32 RGBA .ico)"""
    import struct

    width, height = 32, 32
    pixels = []
    # 深蓝背景 + 白色字母 "DL"
    for y in range(height):
        for x in range(width):
            # 圆角矩形背景
            cx, cy = width // 2, height // 2
            in_bg = True
            if x < 2 or x > width - 3 or y < 2 or y > height - 3:
                in_bg = (x >= 1 and x <= width - 2 and y >= 1 and y <= height - 2)
                corners = [(1, 1), (1, height - 2), (width - 2, 1), (width - 2, height - 2)]
                if (x, y) in corners:
                    in_bg = False
            if in_bg:
                r, g, b, a = 59, 130, 246, 255  # 蓝色
            else:
                r, g, b, a = 0, 0, 0, 0  # 透明

            # 绘制字母 D
            d_zone = (7 <= x <= 11 and 10 <= y <= 22) or (12 <= x <= 14 and (y == 10 or y == 22)) or (x == 15 and 11 <= y <= 21)
            if 7 <= x <= 15 and 10 <= y <= 22 and d_zone:
                r, g, b = 255, 255, 255

            # 绘制字母 L
            if 18 <= x <= 19 and 10 <= y <= 22:
                r, g, b = 255, 255, 255
            if 18 <= x <= 24 and 21 <= y <= 22:
                r, g, b = 255, 255, 255

            pixels.append((r, g, b, a))

    # 构造 ICO (BMP internally)
    bmp_data = bytearray()
    bmp_data += struct.pack("<I", 40)          # header size
    bmp_data += struct.pack("<i", width)       # width
    bmp_data += struct.pack("<i", height * 2)  # height (ICO 用双倍)
    bmp_data += struct.pack("<H", 1)           # planes
    bmp_data += struct.pack("<H", 32)          # bpp
    bmp_data += struct.pack("<I", 0)           # compression
    bmp_data += struct.pack("<I", 0)           # image size (can be 0 for BI_RGB)
    bmp_data += struct.pack("<i", 0)           # x pixels per meter
    bmp_data += struct.pack("<i", 0)           # y pixels per meter
    bmp_data += struct.pack("<I", 0)           # colors used
    bmp_data += struct.pack("<I", 0)           # important colors

    for y in range(height - 1, -1, -1):
        for x in range(width):
            r, g, b, a = pixels[y * width + x]
            bmp_data += struct.pack("BBBB", b, g, r, a)

    and_mask = bytearray((width * height) // 8)
    bmp_data += and_mask

    ico_data = bytearray()
    ico_data += struct.pack("<HHH", 0, 1, 1)          # reserved, type=ICO, count=1
    bmp_size = len(bmp_data)
    total_size = 6 + 16 + bmp_size
    ico_data += struct.pack("<BBBBHHII", width, height, 0, 0, 1, 32, bmp_size, 22)

    with open(ICO_PATH, "wb") as f:
        f.write(ico_data + bmp_data)
    print(f"  图标已生成: {ICO_PATH}")


def create_shortcut():
    """使用 PowerShell 创建桌面快捷方式"""
    shortcut_path = os.path.join(DESKTOP, "DL查询助手.lnk")
    ps_script = f"""
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{BAT_PATH}"
$Shortcut.IconLocation = "{ICO_PATH}"
$Shortcut.WorkingDirectory = "{PROJ_ROOT}"
$Shortcut.Description = "深度学习查询助手 - 函数用法查询工具"
$Shortcut.Save()
Write-Host "快捷方式已创建: {shortcut_path}"
"""
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_script],
        capture_output=True, text=True
    )
    print(result.stdout.strip())
    if result.returncode != 0:
        print(result.stderr.strip())
    return result.returncode == 0


if __name__ == "__main__":
    print("正在创建桌面快捷方式...")
    if not os.path.exists(ICO_PATH):
        generate_icon()
    else:
        print(f"  图标已存在: {ICO_PATH}")
    create_shortcut()
    print("\n完成！桌面已生成 'DL查询助手' 快捷方式，双击即可启动。")

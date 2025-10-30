import time
import threading
from pywinauto import Application
import pytesseract
import cv2
import numpy as np
from PIL import Image, ImageGrab
import pyautogui
import os
import pyperclip

# 配置Tesseract路径（如果需要）
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # 根据实际路径调整

# 公众号列表
public_accounts = ["西安交通大学团委"]
# 关键词列表
keywords = ["集体活动"]

# 全局变量用于停止程序
stop_program = False

def capture_screen(region=None):
    """截取屏幕指定区域"""
    img = ImageGrab.grab(bbox=region)
    return img

def preprocess_image(img):
    """预处理图像以提高OCR准确性"""
    img_np = np.array(img)
    gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    return Image.fromarray(thresh)

def extract_text_from_image(img):
    """从图像提取文本"""
    text = pytesseract.image_to_string(img, lang='chi_sim')
    return text

def check_keywords(text, keywords):
    """检查文本中是否包含关键词"""
    for keyword in keywords:
        if keyword in text:
            return True, keyword
    return False, None

def click(x, y):
    rect = current_window.rectangle()
    pyautogui.click(rect.left + x, rect.top + y)

def move_to(x, y):
    rect = current_window.rectangle()
    pyautogui.moveTo(rect.left + x, rect.top + y)

def monitor_esc_key():
    """持续监控ESC键的线程函数"""
    import keyboard
    global stop_program
    def on_esc_press(event):
        if event.name == 'esc':
            print("检测到ESC键按下，程序停止。")
            stop_program = True
            os._exit(0)  # 强制退出程序
    keyboard.on_press(on_esc_press)
    while not stop_program:
        time.sleep(0.1)


def main():
    global current_window, stop_program
    # 等待用户
    input("请确保微信已启动并登录，按Enter键开始运行脚本：")

    # 启动监控线程
    monitor_thread = threading.Thread(target=monitor_esc_key)
    monitor_thread.daemon = True
    monitor_thread.start()

    # 连接到已运行的微信进程
    pyautogui.hotkey('ctrl', 'alt', 'w')
    try:
        app = Application(backend="uia").connect(title_re="微信")
        # 获取所有微信窗口，选择主窗口
        current_window = app.windows(title_re="微信")[0]
        if current_window:
            print("成功连接到微信")
        else:
            print("未找到微信窗口")
            return
    except Exception as e:
        print(f"无法连接到微信: {e}")
        return

    for account in public_accounts:
        if stop_program:
            break
        try:
            current_window.set_focus()
            # 打开搜一搜
            click(70, 650)
            time.sleep(1)
            pyautogui.hotkey('ctrl', 'alt', 'w')
            pyautogui.hotkey('ctrl', 'alt', 'w')  # 关闭微信主窗口 
            time.sleep(0.5)
            # 搜索公众号
            app = Application(backend="uia").connect(title_re="微信")
            current_window = app.windows(title_re="微信")[0]  # 转移到搜一搜窗口
            current_window.set_focus()
            move_to(200, 200)
            pyperclip.copy(account)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.1)
            pyautogui.press('enter')
            print(f"搜索公众号 {account}")
            time.sleep(2)
            # 进入公众号
            click(570, 610)

            current_window = app.window(title_re="公众号")

            # 浏览文章：从上至下寻找最近的推文
            for i in range(5):  # 尝试滚动5次
                # 截取公众号页面推文区域
                rect = current_window.rectangle()
                region = (rect.left + 100, rect.top + 200, rect.right - 100, rect.bottom - 100)
                img = capture_screen(region)
                processed_img = preprocess_image(img)
                text = extract_text_from_image(processed_img)

                # 检查是否找到推文（简单检查文本长度）
                if len(text.strip()) > 10:
                    # 假设第一个推文在固定位置，点击进入
                    pyautogui.click(rect.left + 200, rect.top + 250)  # 调整坐标
                    time.sleep(2)

                    # 进入文章后，全选文本
                    pyautogui.hotkey('ctrl', 'a')
                    time.sleep(0.5)
                    pyautogui.hotkey('ctrl', 'c')
                    time.sleep(0.5)

                    # 获取剪贴板内容
                    article_text = pyperclip.paste()

                    # 检索关键词
                    found, keyword = check_keywords(article_text, keywords)
                    if found:
                        print(f"在公众号 {account} 的文章中找到关键词 '{keyword}'")
                        break  # 找到后停止

                # 向下滚动
                pyautogui.scroll(-200, x=rect.left + 200, y=rect.top + 300)
                time.sleep(1)

        except Exception as e:
            print(f"处理公众号 {account} 时出错: {e}")

    # 不关闭微信
    # app.kill()

if __name__ == "__main__":
    main()

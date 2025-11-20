import time
import threading
from pywinauto import Application
import pyautogui
import os
import pyperclip

# 公众号列表
public_accounts = [
    "英仔爱心社", 
    "西交体育",
    "西交体操",
    "西安交通大学团委",
    "西安交通大学仲英书院",
    "西安交通大学团委青发中心",
    "XJTU学生社团指导中心",
    "西安交通大学学生会",
    "西安交通大学南洋书院",
    "西安交通大学电气工程学院",
    "西安交通大学勤工助学",
    "西安交通大学钱学森学院",
    "西安交通大学励志书院",
    "西安交通大学彭康书院",
    "西安交通大学彭康书院团委",
]
# 关键词列表
keywords = [
    "集体活动", 
    "竞赛",
]
# 每个公众号中尝试点击文章的次数
search_count = 5

# 全局变量用于停止程序
stop_program = False

def click_window(x, y):
    rect = current_window.rectangle()
    # 允许用负数从另一边定位
    if x < 0:
        x = rect.right + x
    if y < 0:
        y = rect.bottom + y
    pyautogui.click(rect.left + x, rect.top + y)

def click_center_line(y):
    # 允许用负数从另一边定位
    if y < 0:
        y = rect.bottom + y
    rect = current_window.rectangle()
    pyautogui.click((rect.left + rect.right) / 2, rect.top + y)

def check_keywords(text, keywords):
    """检查文本中是否包含关键词"""
    for keyword in keywords:
        if keyword in text:
            return True, keyword
    return False, None

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
    input("请确保微信已登录，搜一搜未打开，按Enter键开始运行脚本：")

    # 启动监控线程
    monitor_thread = threading.Thread(target=monitor_esc_key)
    monitor_thread.daemon = True
    monitor_thread.start()

    # 连接到已运行的微信进程
    pyautogui.hotkey('ctrl', 'alt','shift', 'w')
    try:
        app = Application(backend="uia").connect(title_re="微信")
        # 获取所有微信窗口，选择主窗口
        current_window = app.window(title_re="微信")
        if current_window:
            print("成功连接到微信")
        else:
            print("未找到微信窗口")
            return
    except Exception as e:
        print(f"无法连接到微信: {e}")
        return
    
    current_window.set_focus()
    # 打开搜一搜
    click_window(70, 650)
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'alt','shift', 'w')
    pyautogui.hotkey('ctrl', 'alt','shift', 'w')  # 关闭微信主窗口 

    app = Application(backend="uia").connect(title_re="微信")
    current_window = app.window(title_re="微信")  # 转移到搜一搜窗口
    current_window.set_focus()

    for account in public_accounts:
        if stop_program:
            break
        try:
            # 搜索公众号
            move_to(200, 200)
            pyperclip.copy(account)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.1)
            pyautogui.press('enter')
            print(f"搜索公众号 {account}")
            time.sleep(2)
            # 进入公众号
            click_center_line(610)

            current_window = app.window(title_re="公众号")
            time.sleep(1)

            # 浏览文章：从上至下寻找最近的推文
            for _ in range(search_count):  # 尝试点击并滚动
                click_center_line(600)  # 进入推文
                time.sleep(1)

                # 进入文章后，全选文本
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.hotkey('ctrl', 'c')
                time.sleep(0.1)

                # 获取剪贴板内容
                article_text = pyperclip.paste()

                # 检索关键词
                found, keyword = check_keywords(article_text, keywords)
                if found:
                    print(f"在公众号 {account} 的文章中找到关键词 '{keyword}'")
                else:
                    print("未检索到关键词")
                    pyautogui.hotkey('ctrl', 'w')

                current_window.set_focus()  # 返回公众号页面
                rect = current_window.rectangle()

                # 向下滚动
                pyautogui.scroll(-100, x=(rect.left+rect.right)/2, y=(rect.top+rect.bottom)/2)
                time.sleep(0.1)

        except Exception as e:
            print(f"处理公众号 {account} 时出错: {e}")

        # 返回搜一搜
        current_window = app.window(title_re="微信")
        current_window.set_focus()
        # 搜索框焦点
        click_window(260, 50)
        click_center_line(200)

    print("检索完毕")

if __name__ == "__main__":
    main()

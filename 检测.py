import pyautogui
import pygetwindow as gw
import time
import sys

def send_wechat_message_relative(friend_name, message):
    """
    使用相对坐标给指定微信好友发送消息
    :param friend_name: 微信好友的备注或昵称
    :param message: 要发送的消息内容
    """
    
    # 1. 激活微信窗口
    wechat_windows = gw.getWindowsWithTitle('微信')
    if not wechat_windows:
        print("未找到微信窗口，请确保微信已登录并打开。")
        sys.exit()
    
    wechat_win = wechat_windows[0]
    if wechat_win.isMinimized:
        wechat_win.restore()
    wechat_win.activate()
    time.sleep(0.5)  # 等待窗口激活

    # 2. 计算相对坐标（需要你先校准这些坐标）
    # 获取窗口的左上角坐标
    left = wechat_win.left
    top = wechat_win.top
    width = wechat_win.width
    height = wechat_win.height
    
    print(f"窗口位置: 左{left}, 上{top}, 宽{width}, 高{height}")
    
    # 3. 定义相对坐标（这些值需要根据你的微信界面进行调整）
    # 搜索按钮的相对坐标（通常在左上角）
    search_button_rel_x = 0.05  # 窗口宽度的5%处
    search_button_rel_y = 0.05  # 窗口高度的5%处
    
    # 搜索输入框的相对坐标
    search_input_rel_x = 0.15   # 窗口宽度的15%处
    search_input_rel_y = 0.08   # 窗口高度的8%处
    
    # 发送按钮区域的相对坐标（聊天输入框）
    send_area_rel_x = 0.65      # 窗口宽度的65%处
    send_area_rel_y = 0.85      # 窗口高度的85%处

    # 4. 转换为绝对坐标
    search_button_x = left + int(width * search_button_rel_x)
    search_button_y = top + int(height * search_button_rel_y)
    
    search_input_x = left + int(width * search_input_rel_x)
    search_input_y = top + int(height * search_input_rel_y)
    
    send_area_x = left + int(width * send_area_rel_x)
    send_area_y = top + int(height * send_area_rel_y)

    # 5. 执行自动化流程
    try:
        # 点击搜索按钮/区域
        pyautogui.click(search_button_x, search_button_y)
        time.sleep(0.5)
        
        # 在搜索框输入好友名称
        pyautogui.click(search_input_x, search_input_y)  # 确保搜索框获得焦点
        time.sleep(0.2)
        pyautogui.hotkey('ctrl', 'a')  # 全选现有内容（如果有）
        pyautogui.press('backspace')   # 删除
        pyautogui.typewrite(friend_name)
        time.sleep(1)  # 等待搜索结果
        
        # 按回车选择第一个搜索结果
        pyautogui.press('enter')
        time.sleep(1)  # 等待聊天窗口打开
        
        # 点击发送区域并输入消息
        pyautogui.click(send_area_x, send_area_y)
        time.sleep(0.2)
        pyautogui.typewrite(message)
        time.sleep(0.5)
        
        # 发送消息
        pyautogui.press('enter')
        
        print(f"✓ 消息已发送给 {friend_name}")
        
    except Exception as e:
        print(f"✗ 发送失败: {e}")

# 坐标校准工具函数
def calibrate_coordinates():
    """
    用于校准相对坐标的辅助函数
    运行这个函数来找到正确的相对坐标值
    """
    wechat_windows = gw.getWindowsWithTitle('微信')
    if not wechat_windows:
        print("请先打开微信")
        return
    
    wechat_win = wechat_windows[0]
    wechat_win.activate()
    time.sleep(1)
    
    print("=== 坐标校准模式 ===")
    print("将鼠标移动到目标位置，按Ctrl+C获取坐标")
    print("窗口信息:", f"左{wechat_win.left}, 上{wechat_win.top}, 宽{wechat_win.width}, 高{wechat_win.height}")
    
    try:
        while True:
            x, y = pyautogui.position()
            # 计算相对坐标（相对于微信窗口）
            rel_x = (x - wechat_win.left) / wechat_win.width
            rel_y = (y - wechat_win.top) / wechat_win.height
            
            print(f"绝对坐标: ({x}, {y}) | 相对坐标: ({rel_x:.3f}, {rel_y:.3f})")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n校准结束")

if __name__ == "__main__":
    # 使用方法1: 校准坐标（取消注释运行）
    # calibrate_coordinates()
    
    # 使用方法2: 发送消息
    target_friend = "文件传输助手"  # 测试时建议先用文件传输助手
    message_to_send = f"自动发送测试 - {time.strftime('%H:%M:%S')}"
    
    send_wechat_message_relative(target_friend, message_to_send)
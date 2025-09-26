import pyautogui
import pygetwindow as gw
import time
import sys
import psutil
import subprocess

# -------------------------- 配置区（仅需校准后修改！）--------------------------
WECHAT_PATH = r"D:\天帝殿\Weixin.exe"
TARGET_FRIEND = "杨正宗"
TEST_FRIEND = "杨正宗"
MESSAGE_CONTENT = f"自动发送成功！时间：{time.strftime('%Y-%m-%d %H:%M:%S')}"

# 相对坐标（需校准后替换）
RELATIVE_COORDS = {
    "search_btn": (0.147, 0.055),    # 搜索框0.147 0.055 0.409 0.7283
    "search_input":(0.147, 0.055),  # 搜索输入框
    "send_area": (0.409, 0.728),     # 消息输入框
    "send_btn": (0.92, 0.85)       # 备用发送按钮
}
# --------------------------------------------------------------------------------------

def kill_wechat():
    """关闭微信残留进程"""
    print("=== 1. 清理微信残留进程 ===")
    for proc in psutil.process_iter(['name', 'pid']):
        if proc.info['name'] in ['WeChat.exe', 'WeChatApp.exe']:
            try:
                proc.kill()
                print(f"✅ 关闭微信进程（PID: {proc.info['pid']}）")
            except Exception as e:
                print(f"⚠️  忽略进程清理错误：{str(e)}")
    time.sleep(3)

def start_wechat():
    """启动微信并等待登录"""
    print("\n=== 2. 启动微信 ===")
    kill_wechat()
    try:
        subprocess.Popen(WECHAT_PATH)
        print(f"✅ 微信已启动（路径：{WECHAT_PATH}）")
        print("📱 请在40秒内用手机扫码登录微信...")
        time.sleep(40)
        return True
    except FileNotFoundError:
        print(f"❌ 启动失败：微信路径错误（当前：{WECHAT_PATH}）")
        return False
    except Exception as e:
        print(f"❌ 启动异常：{str(e)}")
        return False

def get_wechat_window(try_start=True):
    """获取微信窗口（修复：增加多轮查找，避免句柄失效）"""
    max_retry = 3  # 最多重试3次查找窗口
    retry_count = 0
    while retry_count < max_retry:
        wechat_windows = gw.getWindowsWithTitle('微信')
        if wechat_windows:
            # 过滤掉最小化/不可见的窗口
            valid_windows = [w for w in wechat_windows if not w.isMinimized and w.visible]
            if valid_windows:
                return valid_windows[0]
            else:
                print(f"⚠️  微信窗口已找到，但处于最小化/不可见状态，尝试恢复...")
                wechat_windows[0].restore()
                time.sleep(1)
                retry_count += 1
        else:
            print(f"⚠️  第{retry_count+1}次未找到微信窗口")
            retry_count += 1
            time.sleep(2)
    
    # 多次查找失败后，尝试自动启动
    if try_start:
        print("❌ 多次查找失败，尝试自动启动微信...")
        if start_wechat():
            return get_wechat_window(try_start=False)  # 启动后不再递归尝试
    return None

def activate_window(win):
    """修复：替换窗口激活方式（用pyautogui点击标题栏，避免句柄无效）"""
    if not win:
        return False
    try:
        # 1. 先尝试恢复最小化窗口
        if win.isMinimized:
            win.restore()
            time.sleep(0.5)
        # 2. 计算标题栏坐标（窗口左上角向右50px，向下15px，避免点击关闭按钮）
        title_bar_x = win.left + 50
        title_bar_y = win.top + 15
        # 3. 模拟点击标题栏激活窗口
        pyautogui.click(title_bar_x, title_bar_y)
        time.sleep(1)
        print(f"✅ 窗口激活成功（点击标题栏：({title_bar_x}, {title_bar_y})）")
        return True
    except Exception as e:
        print(f"⚠️  窗口激活失败，尝试备用方式：{str(e)}")
        # 备用：用pygetwindow的set_foreground（部分环境可用）
        try:
            win.set_foreground()
            time.sleep(1)
            print("✅ 备用激活方式成功")
            return True
        except Exception as e2:
            print(f"❌ 备用激活也失败：{str(e2)}")
            return False

def calibrate_coordinates():
    """坐标校准工具（修复：用新的窗口激活方式）"""
    print("\n" + "="*60)
    print("=== 微信坐标校准工具 ===")
    print("="*60)
    
    # 获取并激活窗口
    wechat_win = get_wechat_window()
    if not wechat_win:
        print("❌ 无法获取微信窗口，校准失败")
        return
    if not activate_window(wechat_win):
        print("⚠️  窗口未成功激活，可能影响校准精度")
    
    # 窗口基础参数
    win_left = wechat_win.left
    win_top = wechat_win.top
    win_width = wechat_win.width
    win_height = wechat_win.height
    
    print(f"\n📌 微信窗口信息：")
    print(f"   位置：左上角({win_left}, {win_top}) | 大小：{win_width}×{win_height}px")
    print(f"\n📝 校准步骤：")
    print(f"   1. 鼠标移到目标控件（搜索框/消息输入框）")
    print(f"   2. 按 Ctrl+C 记录相对坐标")
    print(f"   3. 将坐标填入代码 RELATIVE_COORDS")
    print("\n开始校准（每1秒刷新）...")
    print("-"*60)
    
    try:
        while True:
            mouse_x, mouse_y = pyautogui.position()
            # 计算相对坐标
            rel_x = round((mouse_x - win_left) / win_width, 3)
            rel_y = round((mouse_y - win_top) / win_height, 3)
            # 实时打印（覆盖上一行）
            print(f"\r当前位置：绝对({mouse_x}, {mouse_y}) | 相对({rel_x}, {rel_y}) | 按Ctrl+C结束", end="")
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n\n✅ 校准完成！请替换 RELATIVE_COORDS：")
        print(f'RELATIVE_COORDS = {{')
        print(f'    "search_btn": ({rel_x}, {rel_y}),    # 搜索框')
        print(f'    "search_input": ({rel_x}, {rel_y}),  # 搜索输入框')
        print(f'    "send_area": (x, y),                 # 消息输入框（重新校准）')
        print(f'    "send_btn": (x, y)                   # 发送按钮（重新校准）')
        print(f'}}')

def send_wechat_message(friend_name, message, is_test=True):
    """发送消息（修复：使用新的窗口激活逻辑）"""
    print("\n" + "="*60)
    print(f"=== {'测试模式' if is_test else '正式模式'}：发送到「{friend_name}」 ===")
    print("="*60)
    
    # 1. 获取并激活窗口
    wechat_win = get_wechat_window()
    if not wechat_win:
        print("❌ 无微信窗口，退出")
        sys.exit()
    if not activate_window(wechat_win):
        print("⚠️  窗口未激活，可能导致点击失效")
    
    # 2. 计算坐标
    win_left = wechat_win.left
    win_top = wechat_win.top
    win_width = wechat_win.width
    win_height = wechat_win.height
    
    def get_abs_pos(pos_key):
        """相对坐标转绝对坐标"""
        rel_x, rel_y = RELATIVE_COORDS[pos_key]
        return (int(win_left + win_width * rel_x), int(win_top + win_height * rel_y))
    
    search_btn_pos = get_abs_pos("search_btn")
    search_input_pos = get_abs_pos("search_input")
    send_area_pos = get_abs_pos("send_area")
    
    print(f"\n📊 坐标信息：")
    print(f"   搜索框：{search_btn_pos} | 消息输入框：{send_area_pos}")
    
    # 3. 执行发送流程
    try:
        # 步骤1：点击搜索框
        print(f"\n🔍 步骤1：点击搜索框（{search_btn_pos}）")
        pyautogui.click(search_btn_pos)
        time.sleep(0.8)
        
        # 步骤2：清空搜索框
        print(f"🗑️  步骤2：清空搜索框")
        pyautogui.click(search_input_pos)
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        time.sleep(0.3)
        
        # 步骤3：输入好友昵称
        print(f"📝 步骤3：输入「{friend_name}」")
        pyautogui.typewrite(friend_name, interval=0.12)
        time.sleep(1.8)
        
        # 步骤4：打开聊天窗
        print(f"🪟 步骤4：打开聊天窗口")
        pyautogui.press('enter')
        time.sleep(2)
        
        # 步骤5：输入并发送消息
        print(f"✏️  步骤5：输入消息")
        pyautogui.click(send_area_pos)
        time.sleep(0.5)
        pyautogui.typewrite(message, interval=0.08)
        time.sleep(1)
        
        print(f"🚀 步骤6：发送消息")
        pyautogui.press('enter')
        time.sleep(1.5)
        
        print(f"\n🎉 发送成功！")
        print(f"   接收人：{friend_name} | 内容：{message}")
    
    except pyautogui.FailSafeException:
        print(f"\n❌ 中断：触发安全机制（鼠标移到屏幕角落）")
    except Exception as e:
        print(f"\n❌ 发送失败：{str(e)}")
        print(f"💡 建议：1. 重新校准坐标 2. 确保微信未被遮挡")
        traceback.print_exc()

# -------------------------- 主入口 --------------------------
if __name__ == "__main__":
    import traceback  # 延迟导入，避免校准阶段未用到时报错
    print("="*70)
    print("=== 微信自动发送工具（修复句柄无效版）===")
    print("="*70)
    print("操作模式：")
    print("  1. 校准坐标（首次必选）")
    print("  2. 测试发送（文件传输助手）")
    print("  3. 正式发送（.杨正宗）")
    print("="*70)
    
    choice = input("请输入编号（1/2/3）：").strip()
    if choice == "1":
        calibrate_coordinates()
    elif choice == "2":
        send_wechat_message(TEST_FRIEND, MESSAGE_CONTENT, is_test=True)
    elif choice == "3":
        confirm = input(f"⚠️  即将发送给「{TARGET_FRIEND}」，继续？（y/n）：").lower()
        if confirm == "y":
            send_wechat_message(TARGET_FRIEND, MESSAGE_CONTENT, is_test=False)
        else:
            print("✅ 已取消")
    else:
        print("❌ 无效输入，需输入1/2/3")
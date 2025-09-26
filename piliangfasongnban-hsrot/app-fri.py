import pyautogui
import pygetwindow as gw
import time
import sys
import os
from PIL import Image
import pyperclip
import importlib.util
import psutil
from pywinauto import Application
from pywinauto.findwindows import ElementNotFoundError

class WeChatAuto:
    def __init__(self, wechat_path="D:\\天帝殿\\Weixin\\Weixin.exe"):
        self.template_path = "wechat_templates"
        self.wechat_path = wechat_path
        self.create_template_dir()
        # 检查必要的库是否安装
        self.check_dependencies()
        # 配置pyautogui
        pyautogui.PAUSE = 0.5  # 每个操作后的暂停时间
        pyautogui.FAILSAFE = True  # 启用安全模式
        
    def check_dependencies(self):
        """检查必要的依赖库是否安装"""
        required_libs = {
            "cv2": "opencv-python",
            "pygetwindow": "pygetwindow",
            "pyautogui": "pyautogui"
        }
        
        missing = []
        for lib, pkg in required_libs.items():
            if importlib.util.find_spec(lib) is None:
                missing.append(pkg)
                
        if missing:
            print(f"缺少必要的库，请先安装：")
            print(f"pip install {' '.join(missing)}")
            sys.exit(1)
            
        # 特别检查OpenCV是否可用
        self.opencv_available = importlib.util.find_spec("cv2") is not None
            
    def create_template_dir(self):
        """创建模板图片目录"""
        if not os.path.exists(self.template_path):
            os.makedirs(self.template_path)
            print(f"已创建模板目录: {self.template_path}")
            print("请将截取的微信界面元素图片放入此目录")
            
    def take_screenshot(self, region_name, region=None):
        """截取指定区域的屏幕截图，用于制作模板"""
        try:
            if region:
                # 确保区域有效
                screen_width, screen_height = pyautogui.size()
                if (region[0] + region[2] > screen_width or 
                    region[1] + region[3] > screen_height):
                    print("警告：截图区域超出屏幕范围，将截取全屏")
                    screenshot = pyautogui.screenshot()
                else:
                    screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()
                
            filename = f"{self.template_path}/{region_name}.png"
            screenshot.save(filename)
            print(f"已保存截图: {filename}")
            return filename
        except Exception as e:
            print(f"截图失败: {e}")
            return None
    
    def locate_element(self, template_name, confidence=0.8, retry_times=3, grayscale=True):
        """使用图像识别定位元素，增加兼容性处理"""
        template_file = f"{self.template_path}/{template_name}.png"
        
        if not os.path.exists(template_file):
            print(f"模板文件不存在: {template_file}")
            return None
            
        # 根据OpenCV是否安装调整参数
        kwargs = {"grayscale": grayscale}
        if self.opencv_available:
            kwargs["confidence"] = confidence
            
        for i in range(retry_times):
            try:
                # 先尝试定位全屏
                element_location = pyautogui.locateOnScreen(template_file, **kwargs)
                
                # 如果全屏没找到，尝试只在微信窗口内搜索
                if not element_location:
                    wechat_windows = gw.getWindowsWithTitle('微信')
                    if wechat_windows:
                        wechat_win = wechat_windows[0]
                        region = (wechat_win.left, wechat_win.top, 
                                 wechat_win.width, wechat_win.height)
                        element_location = pyautogui.locateOnScreen(
                            template_file, 
                            region=region,** kwargs
                        )
                
                if element_location:
                    print(f"✓ 成功定位 {template_name}")
                    return element_location
                else:
                    print(f"第 {i+1} 次尝试定位 {template_name} 失败")
                    time.sleep(1)
            except Exception as e:
                print(f"定位 {template_name} 时出错: {e}")
                time.sleep(1)
                
        print(f"✗ 无法定位 {template_name}，请检查模板图片")
        return None
    
    def click_element(self, template_name, confidence=0.8, offset_x=0, offset_y=0, rel_x=0.5, rel_y=0.5):
        """定位并点击元素"""
        element = self.locate_element(template_name, confidence)
        if element:
            # 计算点击位置
            click_x = element.left + int(element.width * rel_x) + offset_x
            click_y = element.top + int(element.height * rel_y) + offset_y
            # 移动到位置再点击，增加可视性
            pyautogui.moveTo(click_x, click_y, duration=0.2)
            pyautogui.click()
            time.sleep(0.5)
            return True
        return False

    def kill_wechat(self):
        
        """关闭所有微信进程，确保干净启动"""
        import psutil
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] in ['WeChat.exe', 'WeChatApp.exe']:
                try:
                    proc.kill()
                    print(f"已关闭微信进程（PID: {proc.info['pid']}）")
                except Exception as e:
                    print(f"忽略进程关闭错误：{str(e)}")
        time.sleep(3)  # 延长等待，确保进程完全退出

    def activate_wechat(self, wait_login_time=3):
        """使用pywinauto通过控件激活微信窗口，支持启动新实例"""
        try:
            # 尝试连接已运行的微信
            try:
                app = Application(backend="uia").connect(title="微信", class_name="Qt51514QWindowIcon")
                main_window = app.window(title="微信", class_name="Qt51514QWindowIcon")
                main_window.wait("ready", timeout=10)
                main_window.set_focus()
                print("已连接并激活现有微信窗口")
                return True
            except:
                print("未找到运行中的微信，尝试启动新实例")
                # 先确保所有微信进程已关闭
                self.kill_wechat()
                # 启动新微信实例
                app = Application(backend="uia").start(self.wechat_path)
                print(f"请在{wait_login_time}秒内完成微信登录（扫码/手机确认）...")
                time.sleep(wait_login_time)
                
                # 连接到新启动的微信窗口
                main_window = app.window(title="微信", class_name="Qt51514QWindowIcon")
                main_window.wait("ready", timeout=15)
                main_window.set_focus()
                print("微信窗口已启动并激活")
                return True
        except ElementNotFoundError:
            print("错误：未找到微信窗口（可能版本或路径变化）")
            return False
        except Exception as e:
            print(f"激活微信窗口时出错: {e}")
            return False
    
    def search_and_open_chat(self, friend_name):
        """搜索并打开指定好友的聊天窗口，增加多种搜索方式"""
        # 尝试点击搜索图标
        if not self.click_element("search_icon"):
            # 尝试不同的搜索快捷键
            print("尝试使用搜索快捷键 Ctrl+F")
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(1)
            
            # 如果还不行，尝试点击窗口顶部
            if not self.locate_element("message_input"):
                print("尝试点击窗口顶部激活搜索")
                wechat_win = gw.getWindowsWithTitle('微信')[0]
                pyautogui.click(wechat_win.left + 100, wechat_win.top + 30)
                time.sleep(1)
                pyautogui.hotkey('ctrl', 'f')
                time.sleep(1)
        
        # 输入好友名称
        try:
            # 清空搜索框
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace')
            time.sleep(0.5)
            
            # 输入好友名称
            pyperclip.copy(friend_name)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(2)  # 等待搜索结果
            
            # 尝试多种方式选择好友
            # 1. 按回车
            pyautogui.press('enter')
            time.sleep(1)
            
            # 检查是否成功打开
            if self.locate_element("message_input", confidence=0.7):
                print("✓ 成功打开聊天窗口")
                return True
                
            # 2. 如果回车不行，尝试按向下箭头再回车
            print("尝试另一种方式打开聊天窗口")
            pyautogui.press('down')
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(1.5)
            
            if self.locate_element("message_input", confidence=0.7):
                print("✓ 成功打开聊天窗口")
                return True
            else:
                print("✗ 可能未成功打开聊天窗口")
                return False
        except Exception as e:
            print(f"搜索好友时出错: {e}")
            return False
    
    def send_message(self, message):
        """在已打开的聊天窗口中发送消息"""
        # 确保输入框被激活
        if not self.click_element("message_input"):
            # 尝试直接点击窗口底部区域
            print("尝试直接点击输入区域")
            wechat_win = gw.getWindowsWithTitle('微信')[0]
            pyautogui.click(wechat_win.left + 200, wechat_win.top + wechat_win.height - 100)
            time.sleep(0.5)
        
        try:
            # 清除可能存在的文本
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace')
            time.sleep(0.2)
            
            # 输入消息
            pyperclip.copy(message)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(1)  # 增加等待时间，确保粘贴完成
            
            # 发送消息 - 尝试多种方式
            if self.click_element("send_button", confidence=0.7):
                time.sleep(0.5)
            else:
                # 如果发送按钮没找到，用回车发送
                print("尝试用回车键发送消息")
                pyautogui.press('enter')
                
            time.sleep(1)
            print("✓ 消息发送完成")
            return True
        except Exception as e:
            print(f"发送消息时出错: {e}")
            return False
    
    def send_wechat_message(self, friend_name, message):
        """主函数：发送微信消息"""
        print(f"开始发送消息给 {friend_name}...")
        
        # 激活微信窗口
        if not self.activate_wechat():
            return False
        
        # 搜索并打开聊天窗口
        if not self.search_and_open_chat(friend_name):
            return False
        
        # 发送消息
        if not self.send_message(message):
            return False
        
        print(f"✓ 成功发送消息给 {friend_name}")
        return True
    
    def create_templates(self):
        """辅助函数：创建模板图片，增加指导信息"""
        print("\n=== 微信界面元素模板创建向导 ===")
        print("请按照提示操作，确保微信窗口可见且未被遮挡")
        print("将鼠标移动到目标位置中央，然后按回车")
        
        input("1. 将鼠标移动到【搜索图标】上（通常在微信窗口顶部），按回车...")
        pos = pyautogui.position()
        search_region = (pos[0]-20, pos[1]-20, 40, 40)
        self.take_screenshot("search_icon", search_region)
        
        input("2. 将鼠标移动到【消息输入框】内（底部输入区域），按回车...")
        pos = pyautogui.position()
        input_region = (pos[0]-50, pos[1]-15, 100, 30)  # 更大的区域，提高识别率
        self.take_screenshot("message_input", input_region)
        
        input("3. 将鼠标移动到【发送按钮】上（输入框旁边），按回车...")
        pos = pyautogui.position()
        send_region = (pos[0]-20, pos[1]-20, 40, 40)
        self.take_screenshot("send_button", send_region)
        
        print("\n✓ 模板创建完成！现在可以运行自动化了。")
        print("如果后续识别失败，请重新运行此向导更新模板\n")

    def send_batch_messages(self, friend_list, message):
        """批量发送消息给好友列表中的所有好友"""
        print(f"\n=== 开始批量发送消息 ===")
        print(f"目标好友数量: {len(friend_list)}")
        print(f"发送内容: {message}\n")
        
        # 先激活微信窗口
        if not self.activate_wechat():
            print("批量发送失败：无法激活微信窗口")
            return False
            
        success_count = 0
        fail_list = []
        
        for index, friend_name in enumerate(friend_list, 1):
            print(f"\n--- 正在处理第 {index}/{len(friend_list)} 位好友：{friend_name} ---")
            
            try:
                # 搜索并打开聊天窗口
                if not self.search_and_open_chat(friend_name):
                    fail_list.append(friend_name)
                    continue
                
                # 发送消息
                if self.send_message(message):
                    success_count += 1
                    print(f"✅ 已发送给 {friend_name}")
                else:
                    fail_list.append(friend_name)
                    print(f"❌ 发送给 {friend_name} 失败")
                
                # 每发送3个消息后休息一下，避免操作过于频繁
                if index % 3 == 0:
                    print("稍作休息，避免操作过于频繁...")
                    time.sleep(5)
                    
            except Exception as e:
                fail_list.append(friend_name)
                print(f"❌ 处理 {friend_name} 时出错: {str(e)}")
                # 出错后尝试重新激活微信窗口
                self.activate_wechat()
        
        # 输出批量发送结果
        print("\n=== 批量发送完成 ===")
        print(f"总发送: {len(friend_list)} 个")
        print(f"成功: {success_count} 个")
        print(f"失败: {len(fail_list)} 个")
        
        if fail_list:
            print("发送失败的好友列表:")
            for name in fail_list:
                print(f"  - {name}")
                
        return success_count > 0

def read_friend_list(file_path="friends.txt"):
    """从文件读取好友名单"""
    if not os.path.exists(file_path):
        print(f"好友名单文件 {file_path} 不存在，创建默认文件")
        # 创建默认好友文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("仙尊\n")
            f.write("慢点宝宝[猪头]\n")
            f.write("宝宝[猪头]\n")
        print(f"请编辑 {file_path} 文件添加你的好友名单（每行一个好友）")
        return []
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            # 读取并过滤空行和注释行
            friends = [
                line.strip() 
                for line in f.readlines() 
                if line.strip() and not line.strip().startswith("#")
            ]
        print(f"成功从 {file_path} 读取 {len(friends)} 个好友")
        return friends
    except Exception as e:
        print(f"读取好友名单失败: {e}")
        return []

def main():
    try:
        wechat = WeChatAuto()
        
        # 检查必要的模板文件
        required_templates = ["search_icon.png", "message_input.png", "send_button.png"]
        existing_templates = []
        
        if os.path.exists(wechat.template_path):
            existing_templates = os.listdir(wechat.template_path)
            
        missing_templates = [t for t in required_templates if t not in existing_templates]
        
        # 如果缺少模板，创建模板
        if missing_templates:
            print(f"检测到缺少以下模板文件: {', '.join(missing_templates)}")
            wechat.create_templates()
            # 创建模板后询问是否立即发送消息
            answer = input("是否立即发送消息？(y/n)：")
            if answer.lower() != 'y':
                return
        
        
        # 读取好友列表
        friend_list = read_friend_list()
        if not friend_list:
            # 如果没有读取到好友列表，询问是否手动输入
            answer = input("未读取到好友列表，是否手动输入单个好友？(y/n)：")
            if answer.lower() == 'y':
                target_friend = input("请输入好友名称：")
                friend_list = [target_friend]
            else:
                print("程序退出")
                return
        # target_friend = "仙尊"  # 修改为你要发送的好友名称

        # 发送消息
        message = f"这是一条通过图像识别自动发送的消息\n时间：{time.strftime('%Y-%m-%d %H:%M:%S')}"
        # 输入发送消息
        message = input("\n请输入要发送的消息内容（直接回车使用默认消息）：")
        if not message.strip():
            message = f"这是一条批量发送的消息\n时间：{time.strftime('%Y-%m-%d %H:%M:%S')}"
        print(f"\n准备发送的消息内容:\n{message}\n")

        # 选择发送模式
        print(f"\n即将向以下 {len(friend_list)} 个好友发送消息：")
        for name in friend_list:
            print(f"  - {name}")
        print(f"\n消息内容：\n{message}")
        
        confirm = input("\n确认发送？(y/n)：")
        if confirm.lower() != 'y':
            print("已取消发送")
            return
        
        # 执行批量发送
        if len(friend_list) == 1:
            # 单个好友发送
            success = wechat.send_wechat_message(friend_list[0], message)
        else:
            # 批量发送
            success = wechat.send_batch_messages(friend_list, message)
            
        # success = wechat.send_wechat_message(target_friend, message)
        
        if success:
            print("🎉 消息发送成功！")
        else:
            print("❌ 消息发送失败，请检查：")
            print("1. 微信是否已登录并打开")
            print("2. 模板图片是否准确（可删除wechat_templates文件夹重新创建）")
            print("3. 好友名称是否正确")
            
    except Exception as e:
        print(f"程序运行出错: {e}")

if __name__ == "__main__":
    main()

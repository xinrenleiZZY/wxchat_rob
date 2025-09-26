import time
import psutil
from pywinauto import Application

def main():
    print("=== 微信控件探测工具 ===")
    
    # 1. 先关闭所有微信进程（避免多窗口干扰）
    print("正在关闭所有微信进程...")
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'WeChat.exe':
            try:
                proc.kill()
                print(f"已关闭微信进程（PID: {proc.pid}）")
            except Exception as e:
                print(f"关闭进程时忽略错误：{str(e)}")
    time.sleep(2)  # 等待进程完全关闭
    
    # 2. 配置微信路径（已替换为你的微信路径，无需修改）
    wechat_path = r"D:\天帝殿\Weixin\Weixin.exe"
    print(f"\n即将启动微信，路径：{wechat_path}")
    
    # 3. 启动微信
    try:
        app = Application(backend="win32").start(wechat_path)
        print("微信已启动，请在 30 秒内完成扫码/确认登录...")
        time.sleep(30)  # 留足时间登录
    except Exception as e:
        print(f"启动微信失败：{str(e)}")
        return
    
    # 4. 定位微信主窗口（通过固定类名精准匹配）
    try:
        # 微信PC端主窗口的固定类名：WeChatMainWndForPC
        main_window = app.window(class_name="WeChatMainWndForPC")
        if not main_window.exists(timeout=10):
            print("未找到微信主窗口（可能登录未完成或版本不兼容）")
            return
        
        # 激活窗口，确保控件可识别
        main_window.set_focus()
        time.sleep(2)
        print("\n=== 成功识别微信主窗口，以下是完整控件列表 ===")
        
        # 5. 分类打印关键控件（输入框、按钮、好友列表项）
        print("\n【1. 输入框控件（Edit）- 搜索框/消息框通常在这里】")
        edit_controls = main_window.Edit.children()
        if edit_controls:
            for i, edit in enumerate(edit_controls):
                # 打印输入框的索引、位置、当前内容
                rect = edit.rectangle()
                content = edit.window_text() or "（空）"
                print(f"  Edit{i}: 位置={rect.left},{rect.top} - {rect.right},{rect.bottom} | 内容='{content}'")
        else:
            print("  未找到任何输入框控件")
        
        print("\n【2. 按钮控件（Button）- 发送按钮通常在这里】")
        button_controls = main_window.Button.children()
        if button_controls:
            for i, btn in enumerate(button_controls):
                # 打印按钮的索引、位置、文本（如“发送”）
                rect = btn.rectangle()
                text = btn.window_text() or "（无文本）"
                print(f"  Button{i}: 位置={rect.left},{rect.top} - {rect.right},{rect.bottom} | 文本='{text}'")
        else:
            print("  未找到任何按钮控件")
        
        print("\n【3. 列表项控件（ListItem）- 好友/聊天列表通常在这里】")
        list_item_controls = main_window.ListItem.children()
        if list_item_controls:
            # 只显示前10个（避免输出过长），包含你的好友“.杨正宗”会在这里出现
            for i, item in enumerate(list_item_controls[:10]):
                rect = item.rectangle()
                name = item.window_text() or "（无名）"
                print(f"  ListItem{i}: 位置={rect.left},{rect.top} - {rect.right},{rect.bottom} | 名称='{name}'")
            if len(list_item_controls) > 10:
                print(f"  ... 还有 {len(list_item_controls)-10} 个列表项未显示")
        else:
            print("  未找到任何列表项控件")
        
        print("\n【4. 主窗口基本信息】")
        print(f"  窗口标题：{main_window.window_text()}")
        print(f"  窗口类名：{main_window.class_name()}")
        print(f"  窗口位置：{main_window.rectangle()}")
        
    except Exception as e:
        print(f"\n探测控件时出错：{str(e)}")
        # 出错时打印所有顶层控件，辅助排查
        print("\n当前顶层控件列表（辅助排查）：")
        main_window.print_control_identifiers(depth=1)

if __name__ == "__main__":
    main()
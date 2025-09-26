import time
import psutil
from pywinauto import Application
from pywinauto.findwindows import ElementNotFoundError

# -------------------------- 配置区（无需修改，已匹配你的环境）--------------------------
FRIEND_NAME = ".杨正宗"  # 你的好友昵称（与微信完全一致）
MESSAGE = "最终测试：已适配Qt51514QWindowIcon窗口"  # 发送内容
WECHAT_PATH = r"D:\天帝殿\Weixin\Weixin.exe"  # 你的微信路径
# --------------------------------------------------------------------------------------

def kill_wechat():
    """彻底关闭微信进程（包括后台进程）"""
    for proc in psutil.process_iter(['name', 'pid']):
        if proc.info['name'] in ['WeChat.exe', 'WeChatApp.exe']:
            try:
                proc.kill()
                print(f"已关闭微信进程（PID: {proc.info['pid']}）")
            except Exception as e:
                print(f"忽略进程关闭错误：{str(e)}")
    time.sleep(3)  # 延长等待，确保进程完全退出

def deep_traverse_controls(control, depth=0, target_controls=None):
    """深度递归遍历所有控件，确保穿透到最底层"""
    if target_controls is None:
        target_controls = {
            "search": None,    # 搜索框（第一个Edit）
            "msg": None,       # 消息框（第二个Edit）
            "send": None,      # 发送按钮（含“发送”文本）
            "friend": None     # 目标好友（匹配FRIEND_NAME）
        }
    edit_count = [0]  # 用列表存计数（避免局部变量问题）

    def traverse(child, current_depth):
        try:
            # 获取控件核心属性
            ctrl_type = child.control_type
            ctrl_name = child.window_text().strip()
            indent = "  " * current_depth

            # 1. 识别Edit控件（区分搜索框和消息框）
            if ctrl_type == "Edit":
                edit_count[0] += 1
                if edit_count[0] == 1 and not target_controls["search"]:
                    target_controls["search"] = child
                    print(f"{indent}✅ 找到搜索框（Edit）")
                elif edit_count[0] == 2 and not target_controls["msg"]:
                    target_controls["msg"] = child
                    print(f"{indent}✅ 找到消息输入框（Edit）")

            # 2. 识别发送按钮（含“发送”文本，兼容“发送(S)”）
            elif ctrl_type == "Button" and "发送" in ctrl_name:
                target_controls["send"] = child
                print(f"{indent}✅ 找到发送按钮（文本：{ctrl_name}）")

            # 3. 识别目标好友（完全匹配昵称，避免误判）
            elif ctrl_type == "ListItem" and ctrl_name == FRIEND_NAME:
                target_controls["friend"] = child
                print(f"{indent}✅ 找到目标好友：{ctrl_name}")

            # 递归遍历子控件（即使已找到部分控件，仍继续遍历确保完整）
            for grandchild in child.children():
                traverse(grandchild, current_depth + 1)

        except Exception as e:
            # 忽略个别控件的访问错误（如权限限制）
            pass

    traverse(control, depth)
    return target_controls

def send_message():
    # 1. 启动干净的微信实例
    kill_wechat()
    print(f"\n启动微信：{WECHAT_PATH}")
    app = Application(backend="uia").start(WECHAT_PATH)
    print("请在30秒内完成微信登录（扫码/手机确认）...")
    time.sleep(30)  # 留足登录时间

    try:
        # 2. 定位微信顶层窗口（精准匹配你的Class Name）
        main_window = app.window(
            class_name="Qt51514QWindowIcon",
            title="微信"
        )
        # 等待窗口就绪（关键：确保窗口完全加载）
        main_window.wait("ready", timeout=15)
        main_window.set_focus()
        print("\n✅ 微信窗口已激活（Class: Qt51514QWindowIcon）")

        # 3. 定位核心Weixin窗格（第一个Weixin窗格为内容区）
        print("\n正在查找Weixin窗格...")
        weixin_panes = main_window.child_windows(
            control_type="Pane",
            title="Weixin"
        )
        if not weixin_panes:
            print("❌ 未找到Weixin窗格，退出")
            return
        core_pane = weixin_panes[0]
        # 等待窗格加载（避免控件未渲染）
        core_pane.wait("visible", timeout=10)
        print("✅ 找到核心Weixin窗格，开始深度遍历控件...")

        # 4. 深度遍历所有子控件（穿透到最底层）
        target_controls = deep_traverse_controls(core_pane)

        # 5. 检查是否缺失关键控件
        missing = [k for k, v in target_controls.items() if not v]
        if missing:
            print(f"❌ 缺失关键控件：{', '.join(missing)}")
            # 打印已找到的列表项，辅助核对好友昵称
            if not target_controls["friend"]:
                print("\n已找到的所有列表项（用于核对昵称）：")
                def print_all_listitems(child):
                    try:
                        if child.control_type == "ListItem" and child.window_text().strip():
                            print(f"  - {child.window_text().strip()}")
                        for gc in child.children():
                            print_all_listitems(gc)
                    except:
                        pass
                print_all_listitems(core_pane)
            return

        # 6. 执行发送操作（每步加等待，避免操作过快）
        print("\n=== 开始执行发送流程 ===")
        # 搜索框输入好友昵称
        target_controls["search"].click_input()
        time.sleep(1.5)  # 等待搜索框激活
        target_controls["search"].type_keys(FRIEND_NAME, pause=0.1)  # 慢输入，避免漏字符
        time.sleep(2)    # 等待搜索结果加载

        # 点击好友打开聊天窗口
        target_controls["friend"].click_input(double=True)  # 双击确保打开
        time.sleep(1.5)

        # 输入消息
        target_controls["msg"].click_input()
        time.sleep(1)
        target_controls["msg"].type_keys(MESSAGE, pause=0.05)
        time.sleep(1)

        # 点击发送
        target_controls["send"].click_input()
        time.sleep(1)
        print(f"\n🎉 发送成功！已向【{FRIEND_NAME}】发送消息：\n{MESSAGE}")

    except ElementNotFoundError:
        print("❌ 错误：未找到指定窗口/控件（可能微信版本或路径变化）")
    except Exception as e:
        print(f"\n❌ 发送过程出错：{str(e)}")
        # 打印详细错误信息，便于排查
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== 微信自动发送脚本（最终适配版）===")
    send_message()
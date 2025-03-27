# wdapy
[![PyPI](https://img.shields.io/pypi/v/wdapy?color=blue)](https://pypi.org/project/wdapy/)

[English](README.md)

遵循 <https://github.com/appium/WebDriverAgent/blob/master/CHANGELOG.md> 中的 WDA API

## 环境要求
Python 3.7+

> 运行单元测试需要 Python 3.8+

## 安装
```bash
pip3 install wdapy

# 可选
# 当 WDA 无响应时，支持使用 tidevice 启动 WDA
pip3 install tidevice[openssl]
```

## 使用方法

创建客户端实例
```python
import wdapy

# 基于项目: https://github.com/appium/WebDriverAgent
c = wdapy.AppiumClient()
# 或者
c = wdapy.AppiumClient("http://localhost:8100")
# 或者
c = wdapy.AppiumUSBClient("00008101-001234567890ABCDEF")
# 或者 (仅当只有一台设备连接时有效)
c = wdapy.AppiumUSBClient()

# 基于项目: https://github.com/codeskyblue/WebDriverAgent
# 支持快速点击和滑动
c = wdapy.NanoClient("http://localhost:8100")
c = wdapy.NanoUSBClient()
```

调用 WDA 方法

```python
print(c.request_timeout) # 显示请求超时时间 (默认 120 秒)
c.request_timeout = 60 # 修改为 60 秒

print(c.scale) # 2 或 3
print(c.window_size()) # (宽度, 高度)
print(c.debug) # 输出 True 或 False (默认 False)
c.debug = True

c.app_start("com.apple.Preferences")
c.app_terminate("com.apple.stocks")
c.app_state("com.apple.mobilesafari")
c.app_list() # 类似 app_current

c.app_current()
# 输出示例
# <AppInfo name='', process_arguments={'env': {}, 'args': []}, pid=6170, bundle_id='com.netease.SnailReader'>

# 将当前应用置于后台 2 秒，然后返回前台
c.deactivate(2.0)

c.alert.exists # 布尔值
c.alert.buttons()
c.alert.accept()
c.alert.dismiss()
c.alert.click("接受")

c.open_url("https://www.baidu.com")

# 剪贴板功能仅在 WebDriverAgent 应用在前台时有效
c.app_start("com.facebook.WebDriverAgentRunner.xctrunner")
c.set_clipboard("foo")
c.get_clipboard() # 输出: foo

c.is_locked() # 布尔值
c.unlock()
c.lock()
c.homescreen()
c.shutdown() # 关闭 WebDriverAgent

c.send_keys("foo")
c.send_keys("\n") # 模拟回车键

# 似乎缺少 c.get_clipboard()
c.screenshot() # PIL.Image.Image
c.screenshot().save("screenshot.jpg")

c.get_orientation()
# PORTRAIT | LANDSCAPE (竖屏 | 横屏)

c.window_size() # 宽度, 高度
print(c.status_barsize) # (宽度, 高度)
print(c.device_info()) # (时区, 当前位置, 型号等)
print(c.battery_info()) # (电量, 状态)

print(c.sourcetree())

c.press_duration(name="power_plus_home", duration=1) # 截屏
# 待添加更多方法

c.volume_up()
c.volume_down()

# 点击坐标 x:100, y:200
c.tap(100, 200)

# 关闭键盘
# 通过点击键盘按钮关闭，默认按钮名称为 ["前往", "发送", "Send", "Done", "Return"]
c.keyboard_dismiss(["Done", "Return"])
```

触摸操作

```python
# 模拟向右滑动，持续 1000 毫秒
from wdapy.actions import TouchActions, PointerAction
finger1 = TouchActions.pointer("finger1", actions=[
    PointerAction.move(200, 300),
    PointerAction.down(),
    PointerAction.move(50, 0, duration=1000, origin=Origin.POINTER),
    # 等同于
    # PointerAction.move(250, 300, duration=1000, origin=Origin.VIEWPORT),
    PointerAction.up(),
])
c.touch_perform([finger1])

# 模拟两指外扩
finger2 = TouchActions.pointer("finger2", actions=[
    PointerAction.move(150, 300),
    PointerAction.down(),
    PointerAction.move(-50, 0, duration=1000, origin=Origin.POINTER),
    PointerAction.up(),
])
c.touch_perform([finger1, finger2])
```

## 重大变更

在 WDA 7.0 和 wdapy 1.0 中已移除

```
from wdapy import Gesture, GestureOption as Option
c.touch_perform([
    Gesture("press", Option(x=100, y=200)),
    Gesture("wait", Option(ms=100)), # ms 应大于 17
    Gesture("moveTo", Option(x=100, y = 100)),
    Gesture("release")
])
```


## 如何贡献
假设你想添加一个新方法

- 第一步，在 README.md 和 README_CN.md 中添加方法用法
- 在 tests/ 目录下添加单元测试
- 在 `## 贡献者` 部分添加你的名字

本仓库通过 GitHub Actions 发布。
代码管理员只需要通过 `git tag $VERSION` 和 `git push --tags` 创建版本
GitHub Actions 将构建 targz 和 wheel 并发布到 https://pypi.org

## 贡献者

- [codeskyblue](https://github.com/codeskyblue)
- [justinxiang](https://github.com/Justin-Xiang)

## 替代方案
- https://github.com/openatx/facebook-wda

## 许可证
[MIT](LICENSE)
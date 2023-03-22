# wdapy
[![PyPI](https://img.shields.io/pypi/v/wdapy?color=blue)](https://pypi.org/project/wdapy/)

[中文](README_CN.md)

## Requires
Python 3.7+

> Run unittest require py 3.8+

## Installation
```bash
pip3 install wdapy

# Optional
# Support launch WDA with tidevice when WDA is dead
pip3 install tidevice[openssl]
```

## Usage

Create Client instance
```python
import wdapy

# Based on project: https://github.com/appium/WebDriverAgent
c = wdapy.AppiumClient()
# or
c = wdapy.AppiumClient("http://localhost:8100")
# or
c = wdapy.AppiumUSBClient("00008101-001234567890ABCDEF")
# or (only works when only one device)
c = wdapy.AppiumUSBClient()

# Based on project: https://github.com/codeskyblue/WebDriverAgent
# with fast touch and swipe
c = wdapy.NanoClient("http://localhost:8100")
c = wdapy.NanoUSBClient()
```

Call WDA method

```python
print(c.request_timeout) # show request timeout (default 120s)
c.request_timeout = 60 # change to 60

print(c.scale) # 2 or 3
print(c.window_size()) # (width, height)
print(c.debug) # output True or False (default False)
c.debug = True

c.app_start("com.apple.Preferences")
c.app_terminate("com.apple.stocks")
c.app_state("com.apple.mobilesafari")
c.app_list() # like app_current

c.app_current()
# Output example
# <AppInfo name='', process_arguments={'env': {}, 'args': []}, pid=6170, bundle_id='com.netease.SnailReader'>

# put current app to background 2 seconds and put back to foreground
c.deactivate(2.0)

c.alert.exists # bool
c.alert.buttons()
c.alert.accept()
c.alert.dismiss()
c.alert.click("Accept")

c.open_url("https://www.baidu.com")

# clipboard only works when WebDriverAgent app in foreground
c.app_start("com.facebook.WebDriverAgentRunner.xctrunner")
c.set_clipboard("foo")
c.get_clipboard() # output: foo

c.is_locked() # bool
c.unlock()
c.lock()
c.homescreen()
c.shutdown() # shutdown WebDriverAgent

c.send_keys("foo")
c.send_keys("\n") # simulator enter

# seems missing c.get_clipboard()
c.screenshot() # PIL.Image.Image
c.screenshot().save("screenshot.jpg")

c.get_orientation()
# PORTRAIT | LANDSCAPE

c.window_size() # width, height
print(c.status_barsize) # (width, height)
print(c.device_info()) # (timeZone, currentLocation, model and so on)
print(c.battery_info()) # (level, state)

print(c.sourcetree())

c.press_duration(name="power_plus_home", duration=1) #take a screenshot
# todo, need to add more method

c.volume_up()
c.volume_down()

# tap x:100, y:200
c.tap(100, 200)

# dismiss keyboard
# by tap keyboard button to dismiss, default keyNames are ["前往", "发送", "Send", "Done", "Return"]
c.keyboard_dismiss(["Done", "Return"])
```

## How to contribute
Assume that you want to add a new method

- First step, add method usage to README.md
- Define types in _types.py (if necessary)
- Add unit test in under direction tests/
- Add your name in the section `## Contributors`

The repo is distributed by github actions.
The code master just need to create a version through `git tag $VERSION` and `git push --tags`
Github actions will build targz and wheel and publish to https://pypi.org

## Contributors

- [codeskyblue](https://github.com/codeskyblue)
- [justinxiang](https://github.com/Justin-Xiang)

## LICENSE
[MIT](LICENSE)

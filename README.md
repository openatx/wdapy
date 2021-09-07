# wdapy
[![PyPI](https://img.shields.io/pypi/v/wdapy?color=blue)](https://pypi.org/project/wdapy/)

[中文](README_CN.md)

## Installation
```bash
pip3 install wdapy
```

## Usage

Create Client instance
```python
import wdapy

c = wdapy.AppiumClient()
# or
c = wdapy.AppiumClient("http://localhost:8100")
```

Call WDA method

```python
print(c.scale) # 2 or 3
print(c.window_size()) # (width, height)

c.screenshot().save("screenshot.jpg")

print(c.device_info()) # (timeZone, currentLocation, model and so on)

print(c.battery_info()) # (level, state)

print(c.sourcetree())

print(c.status_barsize) # (width, height)
# todo, need to add more method
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

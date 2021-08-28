# wdapy
[![PyPI](https://img.shields.io/pypi/v/wdapy?color=blue)](https://pypi.org/project/wdapy/)

[中文](README_CN.md)

## Installation
```bash
pip3 install wdapy
```

## Usage

```python
import wdapy

c = wdapy.AppiumClient()
st = c.status()
print(st.ip)
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

## LICENSE
[MIT](LICENSE)

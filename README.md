# wdapy
[![PyPI](https://img.shields.io/pypi/v/wdapy)](https://pypi.org/project/wdapy/)

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
中文版

- 第一步先改README文档，将新增加的方法的用法写到其中。
- 定义的类型放在 _types.py目录中，所有复杂的结构都需要定义一个类型。
- 增加完方法之后，需要在tests目录下把单测也写了。
- 最后在Contributors下面增加自己的名字

## Contributors

- github.com/codeskyblue

## LICENSE
[MIT](LICENSE)

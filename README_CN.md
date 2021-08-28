# wdapy
[![PyPI](https://img.shields.io/pypi/v/wdapy?color=blue)](https://pypi.org/project/wdapy/)

[English Version](README.md)

## 依赖
Python3.7+

## 安装
```bash
pip3 install wdapy
```

## 使用

```python
import wdapy

c = wdapy.AppiumClient()
st = c.status()
print(st.ip)
```

## 如何参与贡献

如果你计划新增一个方法进来

- 第一步先改README文档，将新增加的方法的用法写到其中。
- 定义的类型放在 _types.py目录中，所有复杂的结构都需要定义一个类型。
- 在相关文件中（通常来说都是_wdapy.py)增加相应的代码，完成本地的测试
- 增加完方法之后，需要在tests目录下把单测也写了。
- 最后在Contributors下面增加自己的名字

## Contributors

- [codeskyblue](https://github.com/codeskyblue)

## LICENSE
[MIT](LICENSE)

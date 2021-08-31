# wdapy
[![PyPI](https://img.shields.io/pypi/v/wdapy?color=blue)](https://pypi.org/project/wdapy/)

[English Version](README.md)

## 背景
为什么有了 <https://github.com/openatx/facebook-wda> 这个项目了，还要再重写一个项目呢。有几个原因

1. pypi上注册的是facebook-wda这个项目，但是pypi上还有一个wda项目，名叫wda项目的代码太老，经常会导致使用者安装错误。
2. facebook-wda这个项目，一开始的初衷很简单就是写一个Python的库，来方便使用facebook开发的这个WebDriverAgent。没成想，facebook自己先不管WebDriverAgent这个项目了。然后就有很多人fork了这个项目。最出名的应该是appium的fork版本，不过还有很多人自己fork了改进的。这可能就不会有一个标准的wda库了。既要兼容这个，又要兼容那个，导致项目中的代码打了很多补丁，目前看起来真的好丑。
3. facebook-wda这个项目是从python2开始搞的，并没有加入很多的type hint. 导致自动补全的项目不太好。
4. facebook-wda用的人太多了点，然而有些接口我真的是不想要了。删了的话，肯定免不了很多麻烦。既然删不了，那还不如从新开始呢。

那这个wdapy有什么新的特性呢。

1. 发布到pypi的项目名和github上的项目名一致，避免歧义
2. 支持多种版本的WebDriverAgent。所有会有很多的类比如AppiumClient，CodeskyblueClient。这些类都继承自一个基类 CommonClient。一些方法可以重写，比如 tap接口
3. 每个函数都加入自动补全功能。不再是一个dict返回，导致还要看文档才知道返回时啥。另外函数的输入也使用enum进行处理
4. 暴露WDA启动接口出来。这样就能更灵活的适配各种平台
5. 使用mock模块写单测。这样就能在travis之类的持续集成平台上跑测试了。
6. 完善如何贡献代码的文档，有一个标准之后，就可以吸引更多的人加入进来了。另外还会从活跃的用户中选一个合作者进来。这样就算我不在也有人负责bug和feature的跟进。

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

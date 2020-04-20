# 学堂在线视频字幕下载器

## 依赖

```
pip install pathvalidate
pip install requests
```

## 使用方法

```
python main.py
```

此时会提示你输入你的验证信息，请在浏览器中打开你要下载的课程页面，打开你的浏览器的 开发者工具 > 网络 ，刷新，找到任意一个 `GET next.xuetangx.com` 的请求查看信息：

- **Session ID** 在 cookie 中，名字叫 `sessionid`，形如 `ww8nwfwhvu2t6lnku658dsxw3mr44se4`
- **登录号** 在查询参数中，名字叫 `sign`，形如 `THU080910000000`
- **课程编号** 在课程页面路径中，`video` 前面的数字，形如 `2251770`
- **输出目录** 是你计划输出文字的目录，相对于当前目录的路径

```
Please enter your session id: <Session ID>
Please enter your sign id: <登陆号>
Please enter course id: <课程编号>
Please enter output path: <输出目录>
```

全部填写完毕之后即开始自动下载字幕。

## 协议

WTFPL

<a href="http://www.wtfpl.net/"><img
       src="http://www.wtfpl.net/wp-content/uploads/2012/12/wtfpl-badge-4.png"
       width="80" height="15" alt="WTFPL" /></a>

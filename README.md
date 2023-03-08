# 0x01 概述

- 本项目包含**单独的验证码识别模块**、**API化脚本**以及**bp插件化脚本**。重新封装后具有**结果长度、正则判断**以及**重试次数**设置，大大提高识别正确率。且可传入**URL或图片文件流**，增强脚本功能性。

![image](/img/111.png)

- This project includes **separate verification code identification module**, **API script** and **bp plug-in script**. After repackaging, it has **result length, regular judgment** and **retry times** settings, which greatly improves the recognition accuracy. In addition, **URL or picture file stream** can be passed in to enhance script functionality.

# 0x02 环境准备

```
pip install ddddocr
pip install flask
```

# 0x02 文件说明

- 1、**ddddOcr.py**:
```
重新封装的验证码识别模块
```

- 2、**ddddOcrApi.py**:
```
将ddddOcr.py接口API化，支持服务器端启动
（开放公网需要参数host='0.0.0.0'，具体文件内有注释）
```

- 3、**ocrIdentifyBP.py**:
```
根据ddddOcrApi.py开发的burpSuite验证码识别模块
（可以自己魔改不调用API直接调用ddddOcr.py，我懒，等你pull request）
```

# 0x03 ddddOcr.py-验证码识别模块使用

![image](/img/22.png)

- 1、参数简介

| Parameter | Note | Required |
| :----: | :----: | :----: |
| imgUrl | 验证码图片url | imgUrl/imgData |
| imgData | 验证码图片数据流 | imgUrl/imgData |
| saveImg | 是否保存验证码图片在当前目录(默认不保存) | False |
| codeLen | 验证码长度(可不填)用于重新识别提高准确率 | False |
| regular | 正则表达式(可不填)用于重新识别提高准确率 | False |
| maxRetry | 最大重试次数(默认5次)不满足codeLen、regular将重放更新验证码图片 | False |

- 2、identify传输图片数据流识别验证码：
```
import ddddOcr
reqImg = requests.get("https://potato.gold/captcha.html")
reqContentImg = reqImg.content
code = identify(imgData=reqContentImg,saveImg=True,codeLen=5,regular='^[a-z0-9]+$',maxRetry=5)
print(code)
#将code拼接入下一个请求体内发出
```

- 3、identify传输图片URL地址识别验证码：
```
import ddddOcr
code = identify(imgUrl="https://potato.gold/captcha.html",saveImg=True,codeLen=5,regular='^[a-z0-9]+$',maxRetry=5)
print(code)
#将code拼接入下一个请求体内发出
```

# 0x04 ddddOcrApi.py-验证码识别模块API化使用

![image](/img/33.png)

![image](/img/55.png)

- 1、开放公网使用方法（本地启动可忽略）
```
--------------------将代码--------------------
app.run(port=5000,debug=False)
--------------------修改为--------------------
app.run(host='0.0.0.0',port=5000,debug=False)
---------------------------------------------
```

- 2、可自定义认证信息(也可以自行删除认证模块)

![image](/img/44.png)

- 3、启动方式
```
python ddddOcrApi.py
```

# 0x05 ocrIdentifyBP.py-Burp Suite验证码识别插件

    若用自己的接口，记得修改代码中ApiUrl以及头部认证

- 1、导入OCR identify模块

![image](/img/1.png)

- 2、获取验证码图片地址

![image](/img/2.png)

- 3、配置OCR identify模块

![image](/img/3.png)

- 4、选择攻击方式

![image](/img/4.png)

- 5、选择验证码参数使用OCRidentify迭代器

![image](/img/5.png)

![image](/img/6.png)

![image](/img/7.png)

- 6、调整线程数（重点哦）

![image](/img/8.png)

- 7、开始爆破密码

![image](/img/9.png)
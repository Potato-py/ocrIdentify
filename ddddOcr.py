import ddddocr
import re
import requests,base64

# 受制于训练数据集，暂时只能输出小写
# 【parameter】imgUrl-验证码图片url
# 【parameter】imgData-验证码图片数据流
# 【parameter】saveImg-是否保存验证码图片在当前目录(默认不保存)
# 【parameter】codeLen-验证码长度(可不填)用于重新识别提高准确率
# 【parameter】regular-正则表达式(可不填)用于重新识别提高准确率
# 【parameter】maxRetry-最大重试次数(默认5次)不满足codeLen、regular将重放更新验证码图片，若maxRetry=0，将不进行重放
# 【parameter】currentTimes-当前重试次数(不需手动传参)
def identify(imgUrl="",imgData="",saveImg=False,codeLen=0,regular="",maxRetry=5,currentTimes=0):

    try:
        if(imgUrl):
            req = requests.get(imgUrl)
            img_bytes = req.content
        elif(imgData):
            img_bytes = imgData
        else:
            return "[Error]: Need parameter imgUrl/imgData."

        if(saveImg):
            with open('./image.jpg', 'wb') as f:
                f.write(img_bytes)

        ocr = ddddocr.DdddOcr(show_ad=False)
        result = ocr.classification(img_bytes)

        #   长度/正则表达式不满足 将重放调用重新识别
        rule = False if ( (codeLen and len(result)!=codeLen) or (regular and not re.search(regular,result)) ) else True;

        if currentTimes < maxRetry and not rule:
            currentTimes = currentTimes + 1
            return identify(imgUrl,imgData,saveImg,codeLen,regular,maxRetry,currentTimes)
        if not rule:
            return f"[Error]: It has been retried for {maxRetry} times, and the result of how to request length/regularity is not found. You can try to provide the number of retries or change length/regularity!"

        return result
    except Exception as e:
        return "[Error]: "+str(e)
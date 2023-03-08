from flask import Flask,request
import requests,base64
import ddddOcr

app = Flask(__name__)

@app.route("/", methods=['GET','POST'])
def identifyApi():

    if( request.headers.get('Authorization') != "PotatoAuthrization" ):
        return "[Error]: Authorization does not exist!"

    try:
        imgUrl=""
        imgData=""
        if(request.args):
            imgUrl = request.args.get('imgUrl')
            saveImg = True if request.args.get("saveImg") else False
            codeLen = int(request.args.get("codeLen")) if request.args.get("codeLen") else 0
            regular = request.args.get("regular") if request.args.get("regular") else ""
            maxRetry = int(request.args.get("maxRetry")) if request.args.get("maxRetry") else 3
        elif(request.form):
            imgData = base64.b64decode(request.form.get('imgDataB64'))
            saveImg = True if request.form.get("saveImg") else False
            codeLen = int(request.form.get("codeLen")) if request.form.get("codeLen") else 0
            regular = request.form.get("regular") if request.form.get("regular") else ""
            maxRetry = int(request.form.get("maxRetry")) if request.form.get("maxRetry") else 3
        else:
            return "[Error]: Missing parameter. For example：[GET]http://127.0.0.1:5000/?imgUrl=https://potato.gold/captcha.html&codeLen=5&<span></span>regular=^[a-z0-9]%2B$&maxRetry=5<br/>[Post]imgBase64=xxxx&codeLen=5&<span></span>regular=^[a-z0-9]%2B$&maxRetry=5<br/><br/><center style='color:red'> Special symbols need to be url encoded,such as '&'、'+' , and so on...</center>"

        return ddddOcr.identify(imgUrl,imgData,saveImg,codeLen,regular,maxRetry)

    except Exception as e:
        return "[Error]: "+str(e)

if __name__ == '__main__':
    app.run(port=5000,debug=False) # 需要开放公网需要参数host='0.0.0.0'、非服务器开放服务会启动失败
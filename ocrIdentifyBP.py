#coding:utf-8
from burp import IBurpExtender
from burp import IIntruderPayloadGeneratorFactory
from burp import IIntruderPayloadGenerator
from burp import IIntruderPayloadProcessor
from burp import ITab

from javax import swing,imageio
from java.awt import Color,Font,Insets,FlowLayout,Graphics,Graphics2D,RenderingHints,Shape
import java.util.Base64 as JavaBase64
from java.io import ByteArrayInputStream
from java.awt.event import MouseAdapter,MouseEvent


import threading
import base64
import urllib,urllib2
import ssl
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # 设置系统编码，否则碰到中文的地方都会报错(即使是设置了coding也没用)
context = ssl._create_unverified_context()


Headers = {
    "User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    "Authorization": "PotatoTempAuthrization"
}
HeadersOld = {
    "User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    "Authorization": "PotatoTempAuthrization"
}
ImgUrl = ""
MaxRetry = 4
CodeLen = -1
Regular = ""
ApiUrl = "http://potato.gold:5000/"

class BurpExtender(IBurpExtender, IIntruderPayloadGeneratorFactory, IIntruderPayloadProcessor, ITab):

    #
    # payload生成器等模块注册
    #
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName("OCR identify")
        self._infoInit()
        self._initTab(callbacks)
        callbacks.registerIntruderPayloadGeneratorFactory(self)
        callbacks.registerIntruderPayloadProcessor(self)

    #
    # TabUi绘制
    #
    def getTabCaption(self):
        return "OCR identify"

    def getUiComponent(self):
        return self._toolkitTab

    def _initTab(self, callbacks):
        self._toolkitTab = swing.JTabbedPane()
        self._toolkitTab.addTab("Options", self._mainPanel)
        callbacks.customizeUiComponent(self._toolkitTab)
        callbacks.addSuiteTab(self)

    def _infoInit(self):
        self._mainPanel = swing.JPanel()

        self._mainSettingsLabel = swing.JLabel('Settings')
        self._mainSettingsLabel.setFont(Font(self._mainSettingsLabel.getFont().getFontName(),Font.BOLD,(int(self._mainSettingsLabel.getFont().getSize())+5)))
        self._mainSettingsLabel.setHorizontalAlignment(swing.SwingConstants.LEFT)
        self._mainSettingsLabel.setBounds(40, 35, 168, 20)
        self._mainPanel.add(self._mainSettingsLabel)

        self._mainSettingsTopLabel = swing.JLabel()
        self._mainSettingsTopLabel.setBounds(20,20,380,50)
        self._mainSettingsTopLabel.setBorder(swing.BorderFactory.createLineBorder(Color(0xD6D6D6)))
        self._mainSettingsTopLabel.setOpaque(True)
        self._mainSettingsTopLabel.setBackground(Color(0xF5F5F5))
        self._mainPanel.add(self._mainSettingsTopLabel)

        self._mainURLLabel = swing.JLabel('ImgUrl : ')
        self._mainURLLabel.setHorizontalAlignment(swing.SwingConstants.RIGHT)
        self._mainURLLabel.setForeground(Color(0x797979))
        self._mainURLLabel.setBounds(30, 93, 88, 30)
        self._mainPanel.add(self._mainURLLabel)
        self._mainURL = MyTextField()
        self._mainURL.setBounds(128, 93, 255, 30)
        self._mainPanel.add(self._mainURL)

        self._mainHeadLabel = swing.JLabel('Header : ')
        self._mainHeadLabel.setHorizontalAlignment(swing.SwingConstants.RIGHT)
        self._mainHeadLabel.setForeground(Color(0x797979))
        self._mainHeadLabel.setBounds(30, 136, 88, 30)
        self._mainPanel.add(self._mainHeadLabel)
        self._mainHead = swing.JTextArea()
        self._mainHead.setBounds(128, 136, 255, 130)
        self._mainHead.setLineWrap(True)
        self._mainHead.setWrapStyleWord(True)
        self._mainHead.setBackground(Color(0xFAFAFA))
        self.scrollpane = swing.JScrollPane(self._mainHead)
        self.scrollpane.setBounds(128, 136, 255, 130)
        self.scrollpane.setBackground(Color(0xFAFAFA))
        lineBorder = RoundedBorder(Color(0xEFEFEF),5)
        emptyBorder = swing.BorderFactory.createEmptyBorder(self.scrollpane.getBorder().getBorderInsets(self.scrollpane).top, self.scrollpane.getBorder().getBorderInsets(self.scrollpane).left, self.scrollpane.getBorder().getBorderInsets(self.scrollpane).bottom, self.scrollpane.getBorder().getBorderInsets(self.scrollpane).right)
        self.scrollpane.setBorder(swing.BorderFactory.createCompoundBorder(lineBorder, emptyBorder))
        self._mainPanel.add(self.scrollpane)

        self._mainMaxReLabel = swing.JLabel('MaxRetry : ')
        self._mainMaxReLabel.setHorizontalAlignment(swing.SwingConstants.RIGHT)
        self._mainMaxReLabel.setForeground(Color(0x797979))
        self._mainMaxReLabel.setBounds(30, 280, 88, 30)
        self._mainPanel.add(self._mainMaxReLabel)
        self._mainMaxRe = MyTextField("4")
        self._mainMaxRe.getDocument().addDocumentListener(maxRetryDocumentListener(self))
        self._mainMaxRe.setBounds(128, 280, 255, 30)
        self._mainPanel.add(self._mainMaxRe)

        self._mainLenLabel = swing.JLabel('CodeLen : ')
        self._mainLenLabel.setHorizontalAlignment(swing.SwingConstants.RIGHT)
        self._mainLenLabel.setForeground(Color(0x797979))
        self._mainLenLabel.setBounds(30, 323, 88, 30)
        self._mainPanel.add(self._mainLenLabel)
        self._mainLen = MyTextField()
        self._mainLen.setBounds(128, 323, 255, 30)
        self._mainPanel.add(self._mainLen)

        self._mainRegLabel = swing.JLabel('<html>Regular<br/>-python : </html>')
        self._mainRegLabel.setVerticalAlignment(swing.SwingConstants.TOP)
        self._mainRegLabel.setHorizontalAlignment(swing.SwingConstants.RIGHT)
        self._mainRegLabel.setForeground(Color(0x797979))
        self._mainRegLabel.setBounds(30, 366, 88, 60)
        self._mainPanel.add(self._mainRegLabel)
        self._mainReg = MyTextField()
        self._mainReg.setBounds(128, 366, 255, 30)
        self._mainPanel.add(self._mainReg)

        self._mainFsSave = MyButton('Save',Color(0x5794F2),Color(0x3485FB),5, actionPerformed=self._fsSaveFunc)
        self._mainFsSave.setBounds(275, 409, 110, 23)
        self._mainFsSave.setForeground(Color.WHITE)
        self._mainPanel.add(self._mainFsSave)

        self._mainErrorLabel = swing.JLabel()
        self._mainErrorLabel.setForeground(Color.RED)
        self._mainErrorLabel.setHorizontalAlignment(swing.SwingConstants.CENTER)
        self._mainErrorLabel.setBounds(21, 432, 388, 20)
        self._mainPanel.add(self._mainErrorLabel)

        self._mainAuthorLabel = swing.JLabel('Powdered by Potato')
        self._mainAuthorLabel.setHorizontalAlignment(swing.SwingConstants.CENTER)
        self._mainAuthorLabel.setBounds(41, 484, 368, 20)
        self._mainPanel.add(self._mainAuthorLabel)

        self._mainTopLabel = swing.JLabel()
        self._mainTopLabel.setBounds(20,20,380,444)
        self._mainTopLabel.setBorder(swing.BorderFactory.createLineBorder(Color(0xE5E5E5)))
        self._mainTopLabel.setOpaque(True)
        self._mainTopLabel.setBackground(Color(0xFFFFFF))
        self._mainPanel.add(self._mainTopLabel)

        self._mainTestLabel = swing.JLabel('Test Result')
        self._mainTestLabel.setFont(Font(self._mainTestLabel.getFont().getFontName(),Font.BOLD,(int(self._mainTestLabel.getFont().getSize())+5)))
        self._mainTestLabel.setHorizontalAlignment(swing.SwingConstants.LEFT)
        self._mainTestLabel.setBounds(440, 35, 168, 20)
        self._mainPanel.add(self._mainTestLabel)

        self._mainTestTopLabel = swing.JLabel()
        self._mainTestTopLabel.setBounds(420,20,250,50)
        self._mainTestTopLabel.setBorder(swing.BorderFactory.createLineBorder(Color(0xD6D6D6)))
        self._mainTestTopLabel.setOpaque(True)
        self._mainTestTopLabel.setBackground(Color(0xF5F5F5))
        self._mainPanel.add(self._mainTestTopLabel)

        self._mainCodeLabel = swing.JLabel('Test Img : ')
        self._mainCodeLabel.setHorizontalAlignment(swing.SwingConstants.RIGHT)
        self._mainCodeLabel.setForeground(Color(0x797979))
        self._mainCodeLabel.setBounds(430, 93, 75, 30)
        self._mainPanel.add(self._mainCodeLabel)
        self._mainCode = swing.JLabel()
        self._mainCode.setBounds(508, 93, 150, 38)
        self._mainCode.setBorder(swing.BorderFactory.createLineBorder(Color(0xE5E5E5)))
        self._mainCode.setOpaque(True)
        self._mainCode.setBackground(Color(0xFAFAFA))
        if(self._mainCode.getBorder()!=None):
            lineBorder = RoundedBorder(Color(0xEFEFEF),5)
            emptyBorder = swing.BorderFactory.createEmptyBorder(self._mainCode.getBorder().getBorderInsets(self._mainCode).top, self._mainCode.getBorder().getBorderInsets(self._mainCode).left, self._mainCode.getBorder().getBorderInsets(self._mainCode).bottom, self._mainCode.getBorder().getBorderInsets(self._mainCode).right)
            self._mainCode.setBorder(swing.BorderFactory.createCompoundBorder(lineBorder, emptyBorder))
        self._mainPanel.add(self._mainCode)

        self._mainCodeDataLabel = swing.JLabel('Test Code : ')
        self._mainCodeDataLabel.setHorizontalAlignment(swing.SwingConstants.RIGHT)
        self._mainCodeDataLabel.setForeground(Color(0x797979))
        self._mainCodeDataLabel.setBounds(430, 144, 75, 30)
        self._mainPanel.add(self._mainCodeDataLabel)
        self._mainCodeData = MyTextField()
        self._mainCodeData.setBounds(508, 144, 60, 30)
        self._mainCodeData.setEditable(False)
        self._mainPanel.add(self._mainCodeData)

        self._mainBottomLabel = swing.JLabel()
        self._mainBottomLabel.setBounds(420,20,250,180)
        self._mainBottomLabel.setBorder(swing.BorderFactory.createLineBorder(Color(0xE5E5E5)))
        self._mainBottomLabel.setOpaque(True)
        self._mainBottomLabel.setBackground(Color(0xFFFFFF))
        self._mainPanel.add(self._mainBottomLabel)

        self._mainPanel.setLayout(None)


    def _fsSaveFunc(self, event):

        global ImgUrl,MaxRetry,CodeLen,ApiUrl,Headers

        if(self._mainLen.getText() and tryInt(self._mainLen.getText())<1):
            self._mainErrorLabel.setText("[Error]: CodeLen can't be less than 0, please enter a value or not!")
            return

        if(":" in self._mainHead.getText()):
            try:
                for Header in self._mainHead.getText().split("\n"):
                    HeadersList = Header.split(':')
                    if("Content-Length" != str(HeadersList[0].strip())):
                        if(len(HeadersList)==2):
                            Headers[str(HeadersList[0].strip())]=str(HeadersList[1].strip())
                        elif(len(HeadersList)==3):
                            Headers[str(HeadersList[0].strip())]=str(HeadersList[1].strip())+str(HeadersList[2].strip())
            except Exception as e:
                print(getTime()+str(e))
                self._mainErrorLabel.setText("[Error]: Header input error, please check! "+str(e))
        else:
            Headers = HeadersOld
            self._mainErrorLabel.setText("[Error]: Header input can be blank, but may cause inconsistent verification codes")

        try:
            if(self._mainMaxRe.getText().strip()!=str(MaxRetry)):
                self._mainMaxRe.setText("0")

            url = str(self._mainURL.getText().strip())
            ImgUrl = url
            Regular = self._mainReg.getText().strip() if self._mainReg.getText().strip() else None
            CodeLen = tryInt(self._mainLen.getText())

            getPayload(self,check=True)

            self._mainErrorLabel.setText("")
            self._mainFsSave.setText("Success")
            self._saveOver()

        except Exception as e:
            print(getTime()+str(e))
            self._mainErrorLabel.setText("[Error]: IMgURL input error, please check! "+str(e))


    def async_call(fn):
        def wrapper(*args, **kwargs):
            threading.Thread(target=fn, args=args, kwargs=kwargs).start()
        return wrapper

    @async_call
    def _saveOver(self):
        time.sleep(1)
        self._mainFsSave.setText("Save")

    #
    # 实现Payload生成器
    #
    def getGeneratorName(self):
        return "OCRindentify"

    def createNewInstance(self, attack):
        return IntruderPayloadGenerator()

    def getProcessorName(self):
        return "OCR"

    def processPayload(self, currentPayload, originalPayload, baseValue):
        payload = currentPayload
        return payload

def getPayload(self,check=False):
    reqImg = urllib2.Request(ImgUrl, headers=Headers)
    try:
        responseImg = urllib2.urlopen(reqImg,context=context)
    except:
        responseImg = urllib2.urlopen(reqImg)
    reqCodeImg = responseImg.code
    if(check and reqCodeImg!=200):
        raise Exception("ocrServerError-ImgUrl Code"+str(reqCodeImg))
    reqContentImg = responseImg.read()

    imgDataB64 = base64.b64encode(reqContentImg)
    wd = {
        "imgDataB64":imgDataB64,
        "maxRetry":str(MaxRetry)
    }
    if(CodeLen>0):
        wd["codeLen"]=str(CodeLen)
    if(Regular):
        wd["regular"]=Regular
    PostData = urllib.urlencode(wd)

    req = urllib2.Request(ApiUrl, data=PostData, headers=Headers)
    try:
        response = urllib2.urlopen(req,context=context)
    except:
        response = urllib2.urlopen(req)
    reqContent = response.read()
    if("[Error]" in reqContent):
        print(getTime()+"[Error]：ocrServerError-"+str(reqContent))
        if(check):
            raise Exception("[Error]：ocrServerError-"+str(reqContent))
    if(check):
        imgBytes = JavaBase64.getDecoder().decode(imgDataB64)
        img = imageio.ImageIO.read(ByteArrayInputStream(imgBytes))
        self._mainCode.setIcon(swing.ImageIcon(img))
        self._mainCodeData.setText(reqContent)
    return reqContent

class MouseAdapterListener (MouseAdapter):
    def __init__(self,lastSelf):
        self.swObj = lastSelf

    def mouseEntered(self, e):
        self.swObj.color = self.swObj.color_enter

    def mouseExited(self, e):
        self.swObj.color = self.swObj.color_initial

    def mouseReleased(self, e):
        self.swObj.color = self.swObj.color_initial

    def mouseClicked(self, e):
        self.swObj.color = self.swObj.color_enter

# maxRetry DocumentListener
class maxRetryDocumentListener(swing.event.DocumentListener):

    def __init__(self,lastSelf):
        self.swObj = lastSelf

    def changedUpdate(self,event):
        pass
    def insertUpdate(self,event):
        self.updateMaxRetryFuc(event)
    def removeUpdate(self,event):
        self.updateMaxRetryFuc(event)

    def updateMaxRetryFuc(self,event):
        global MaxRetry
        doc = event.getDocument()
        strData = doc.getText(0, doc.getLength())
        try:
            if ( int(strData) > 0 ):
                MaxRetry = int(strData)
                self.swObj._mainReg.setEditable(True)
                self.swObj._mainLen.setEditable(True)
                self.swObj._mainReg.setBackground(None)
                self.swObj._mainLen.setBackground(None)
            elif int(strData) == 0:
                MaxRetry = 0
                self.swObj._mainReg.setText("")
                self.swObj._mainLen.setText("")
                self.swObj._mainReg.setEditable(False)
                self.swObj._mainLen.setEditable(False)
                self.swObj._mainReg.setOpaque(True)
                self.swObj._mainLen.setOpaque(True)
                self.swObj._mainReg.setBackground(Color.LIGHT_GRAY)
                self.swObj._mainLen.setBackground(Color.LIGHT_GRAY)
            else:
                MaxRetry = 0
                self.swObj._mainReg.setText("")
                self.swObj._mainLen.setText("")
                self.swObj._mainReg.setEditable(False)
                self.swObj._mainLen.setEditable(False)
                self.swObj._mainReg.setOpaque(True)
                self.swObj._mainLen.setOpaque(True)
                self.swObj._mainReg.setBackground(Color.LIGHT_GRAY)
                self.swObj._mainLen.setBackground(Color.LIGHT_GRAY)
        except: # 存在非数字
            MaxRetry = 0
            self.swObj._mainReg.setText("")
            self.swObj._mainLen.setText("")
            self.swObj._mainReg.setEditable(False)
            self.swObj._mainLen.setEditable(False)
            self.swObj._mainReg.setOpaque(True)
            self.swObj._mainLen.setOpaque(True)
            self.swObj._mainReg.setBackground(Color.LIGHT_GRAY)
            self.swObj._mainLen.setBackground(Color.LIGHT_GRAY)

#
# class payload生成器
#
class IntruderPayloadGenerator(IIntruderPayloadGenerator):
    def __init__(self):
        self._payloadIndex = 0

    def hasMorePayloads(self):    #   判定是否将修改后的请求发送会Intruder模块
        return True

    def getNextPayload(self, baseValue):
        payload = getPayload(self)
        return payload
    def reset(self):
        self._payloadIndex = 0


#
# UI重写JTextField
#
class MyTextField(swing.JTextField):
    def __init__(self,text="",color=Color(0xEFEFEF),radius=5,columns=20):
        self.text = text
        self.color = color
        self.radius = radius
        self.columns = columns
        self.setMargin(Insets(0, 10, 0, 0))

    def MyTextField(self,columns):
        self.columns = columns
        self.setMargin(Insets(0, 20, 0, 0))

    def paintBorder(self,g):
        h = self.getHeight()
        w = self.getWidth()
        g2d = g.create()
        shape = g2d.getClip()
        g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON)
        g2d.setClip(shape)
        g2d.setColor(self.color)
        g2d.drawRoundRect(0, 0, w - 2, h - 2, self.radius, self.radius)
        g2d.dispose()
        self.setBackground(Color(0xFAFAFA))
        super(MyTextField,self).paintBorder(g2d)

    def main(self,args):
        jf = swing.JFrame()
        jf.setDefaultCloseOperation(swing.JFrame.EXIT_ON_CLOSE)
        jf.setSize(300, 200)
        jf.setLayout(FlowLayout())
        text = MyTextField(20)
        jf.add(text)
        jf.setVisible(True)

class RoundedBorder(swing.border.Border):
    color = Color(0x5794F2)
    radius = 10

    def __init__(self,color,radius):
        self.color = color
        self.radius = radius

    def getBorderInsets(self,c):
        return Insets(self.radius+1,self.radius+1,self.radius+1,self.radius+1)

    def isBorderOpaque(self):
        return False

    def paintBorder(self,c,g,x,y,width,height):
        g2d = g.create()
        g2d.setColor(self.color)
        g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON)
        g2d.drawRoundRect(0, 0, c.getWidth() - 1, c.getHeight() - 1, self.radius, self.radius)


class MyButton(swing.JButton):
    def __init__(self,text,color_initial,color_enter,radius,actionPerformed):
        super(MyButton,self).__init__()
        self.text = text
        self.color = color_initial
        self.color_initial = color_initial
        self.color_enter = color_enter
        self.radius = radius
        self.actionPerformed = actionPerformed
        self.setOpaque(False)
        self.setContentAreaFilled(False)
        self.addMouseListener(MouseAdapterListener(self))

    def paintComponent(self,g):
        width = self.getWidth()
        height = self.getHeight()
        g2d = g.create()
        g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING,RenderingHints.VALUE_ANTIALIAS_ON)
        g2d.setColor(self.color)
        g2d.fillRoundRect(0, 0, width - 1, height - 1, self.radius, self.radius)
        super(MyButton,self).paintComponent(g)


def tryInt(str):
    try:
        return int(str)
    except:
        return -1

def getTime():
    return "["+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+"] "
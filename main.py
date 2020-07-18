import sys
import serial
import serial.tools.list_ports
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QTimer
from python_serial import Ui_MainWindow

class Pyqt5_Serial(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        # 初始化配置
        super().__init__()
        self.setupUi(self)
        self.init()
        # 实例化一个串口对象
        self.ser = serial.Serial()
        # 实例化窗口时就对串口进行检测
        self.port_check()

    def init(self):
        # 串口启动/关闭窗口
        self.pushButton.clicked.connect(self.port_open_close)
        # 串口发送窗口
        self.pushButton_4.clicked.connect(self.data_send)
        # 清除接收窗口
        self.pushButton_3.clicked.connect(self.receive_data_clear)
        # 清除发送窗口
        self.pushButton_5.clicked.connect(self.send_data_clear)
        # 开启一个定时器，接收数据
        self.timer = QTimer(self)   # 实例化一个定时器
        self.timer.timeout.connect(self.data_receive)   # 定时处理函数
        # 开启一个定时器，定时发送数据
        self.timer_send = QTimer(self)
        self.timer_send.timeout.connect(self.data_send)
        self.checkBox.stateChanged.connect(self.data_send_timer)
        # 默认串口是等待打开的状态
        self.port_status = True
        # 按键的背景颜色为白色
        self.pushButton.setStyleSheet("background-color: white")
        self.pushButton_3.setStyleSheet("background-color: white")
        self.pushButton_4.setStyleSheet("background-color: white")
        self.pushButton_5.setStyleSheet("background-color: white")

    # 串口检测
    def port_check(self):
        self.com_dict = {}  # 保存串口的字典
        port_list = list(serial.tools.list_ports.comports())    # 将检测到的COM口转换为列表
        self.comboBox.clear()   # 清除“端口号”的存储内容
        for port in port_list:
            self.com_dict["%s" % port[0]] = "%s" % port[1]
            self.comboBox.addItem(port[0])
        if not len(self.com_dict):
            print("Warning: No COM")

    # 串口开启
    def port_open(self):
        self.ser.port = self.comboBox.currentText() # 设置当前COM口的端号
        self.ser.baudrate = int(self.comboBox_2.currentText())  # 设置当前COM口的波特率
        self.ser.bytesize = int(self.comboBox_3.currentText())  # 设置当前COM口的数据位
        self.ser.stopbits = int(self.comboBox_5.currentText())  # 设置当前COM口的停止位
        self.ser.parity = self.comboBox_4.currentText()     # 设置当前COM口的校验位
        try:
            self.ser.open()
        except:
            print("WARNING: Can't open")
            return None
        self.timer.start(2)     # 启动定时器2ms/次
        if self.ser.isOpen():
            self.pushButton.setText("关闭串口")
            self.pushButton.setStyleSheet("background-color: red")
            self.port_status = False

    # 串口关闭
    def port_close(self):
        self.timer.stop()   # 关闭定时器
        try:
            self.ser.close()    # 关闭串口
        except:
            pass
        if not self.ser.isOpen():
            self.pushButton.setText("打开串口")
            self.pushButton.setStyleSheet("background-color: white")
            self.port_status = True
        # 恢复窗口的数据
        self.checkBox.setCheckState(False)   # 定时发送的选项恢复
        self.lineEdit.setEnabled(True)  # 将发送时间框正常化
        self.textBrowser.clear()    # 数据接收框数据清除

    def port_open_close(self):
        if self.port_status:
            self.port_open()
        else:
            self.port_close()

    # 串口接收数据
    def data_receive(self):
        try:
            num = self.ser.inWaiting()
        except:
            print("WARNING: Can't waiting")
            self.port_close()
            return None
        if num > 0:  # 有数据
            data = self.ser.read(num)   # 读出数据
            self.textBrowser.insertPlainText(data.decode('iso-8859-1'))     # 转换为unicode字符串后显示
            text_cursor = self.textBrowser.textCursor()     # 获取到光标
            text_cursor.movePosition(text_cursor.End)   # 将光标移动到底部
            self.textBrowser.setTextCursor(text_cursor) # 更新光标到底部
        else:
            pass

    # 串口发送数据
    def data_send(self):
        if self.ser.isOpen():
            input_s = self.textEdit.toPlainText()  # 获取发送框的数据
            if input_s != '':   # 非空字符
                input_s = (input_s + '\r\n').encode('utf-8')    # 字符转换为UTF-8字符类型
                self.ser.write(input_s)     # 发送数据
        else:
            pass

    # 串口定时发送数据
    def data_send_timer(self):
        if self.checkBox.isChecked():   # 定时发送的选项勾中
            self.timer_send.start(int(self.lineEdit.text()))    # 开启每次发送的定时时间
            self.lineEdit.setEnabled(False) # 将发送时间反灰
        else:
            self.timer_send.stop()
            self.lineEdit.setEnabled(True)

    # 清除接收的数据
    def receive_data_clear(self):
        self.textBrowser.clear()

    # 清除发送的数据
    def send_data_clear(self):
        self.textEdit.clear()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Pyqt5_Serial()
    window.show()
    sys.exit(app.exec_())
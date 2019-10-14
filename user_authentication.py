import re, os, sys
import configparser as cp
from requests import get
from time import time, sleep
from md5_sha1 import get_md5, get_sha1
from xencode import get_xencode
from my_base64 import my_encode
from setting import setting
#import fix_qt_import_error
from PyQt5 import QtCore, QtGui, QtWidgets
from window_display import Ui_MainWindow


class Authentication(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.header = {
            'Host': '10.0.0.55',
            'Connection': 'keep-alive',
            'Accept': 'text/javascript, application/javascript, */*',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Referer': 'http://10.0.0.55/srun_portal_pc_yys.php?ac_id=8',
            'Accept-Encoding': 'gzip, deflate'
        }
        self.init_url = 'http://10.0.0.55'
        self.get_challenge_api = 'http://10.0.0.55/cgi-bin/get_challenge'
        self.srun_portal_api = 'http://10.0.0.55/cgi-bin/srun_portal'
        self.n = '200'
        self.type = '1'
        self.ac_id = '8'
        self.enc = 'srun_bx1'
        self.time_at = int(time() * 1000)
        ## get ip address
        print("初始化获取ip")
        init_res = get(self.init_url + '/srun_portal_pc_yys.php?ac_id=8',
                       headers=self.header)
        self.ip = re.search('name="user_ip" value="(.*?)"',
                            init_res.text).group(1)
        print("ip:" + self.ip)
        print("***********************************************")

    def get_chksum(self):
        chkstr = self.token + self.username
        chkstr += self.token + self.hmd5
        chkstr += self.token + self.ac_id
        chkstr += self.token + self.ip
        chkstr += self.token + self.n
        chkstr += self.token + self.type
        chkstr += self.token + self.i
        return chkstr

    def get_info(self):
        info_temp = {
            "username": self.username,
            "password": self.password,
            "ip": self.ip,
            "acid": self.ac_id,
            "enc_ver": self.enc
        }
        i = re.sub("'", '"', str(info_temp))  # " to '
        i = re.sub(" ", '', i)  # delete space
        return i

    def get_token(self):
        ## token 为加密盐值
        get_challenge_params = {
            "callback": "jsonp" + str(self.time_at),
            "username": self.username,
            "ip": self.ip,
        }
        get_challenge_res = get(self.get_challenge_api,
                                params=get_challenge_params,
                                headers=self.header)
        self.token = re.search('"challenge":"(.*?)"',
                               get_challenge_res.text).group(1)
        print("token:"+self.token) 
        return self.token

    def complex_work(self):
        info = my_encode(get_xencode(str(self.get_info()), self.token))
        self.i = "{SRBX1}" + info
        # print(self.i)
        self.hmd5 = get_md5('', self.token)
        self.chksum = get_sha1(self.get_chksum())
        # print('已完成加密')

    def login(self):
        print(self.username)
        print(self.password)
        self.get_token()
        self.complex_work()
        
        srun_portal_params = {
            'callback': 'jsonp' + str(self.time_at + 1),
            'action': 'login',
            'username': self.username,
            'password': '{MD5}' + self.hmd5,
            'ac_id': self.ac_id,
            'ip': self.ip,
            'info': self.i,
            'chksum': self.chksum,
            'n': self.n,
            'type': self.type,
        }
        srun_portal_res = get(self.srun_portal_api,
                              params=srun_portal_params,
                              headers=self.header)
        print(srun_portal_res.text + '\n')
        self.get_error(srun_portal_res.text, 1)

    def logout(self):
        srun_portal_params = {
            'callback': 'jsonp' + str(self.time_at + 1),
            'action': 'logout',
            'username': self.username,
            'ac_id': self.ac_id,
            'n': self.n,
            'type': self.type,
        }
        srun_portal_res = get(self.srun_portal_api,
                              params=srun_portal_params,
                              headers=self.header)
        print(srun_portal_res.text + '\n')
        self.get_error(srun_portal_res.text, -1)

    def get_error(self, res, login):
        if (login == 1):
            if ('"error":"ok"' in res):
                print('登录完毕！')
                self.message = '登录完毕！'
                self.result = 'login_succ'
                return
            elif (('"error":"ip_already_online_error"') in res
                  or ('"ecode":"E2620"' in res)):
                print('无法完成登录, 因为您已经在线了!')
                self.message = '无法完成登录, 因为您已经在线了!'
            elif (('"error":"auth_info_error"' in res)
                  or ('"ecode":"E2531"' in res)):
                print('用户名错误，请修改！')
                self.message = '用户名错误，请修改！'
            elif ('"ecode":"E2553"' in res):
                print('密码错误，请修改！')
                self.message = '密码错误，请修改！'
            else:
                print('登录发生未知错误! 请反馈给我！')
                self.message = '登录发生未知错误! 请反馈给我！'
                sleep(2)
            self.result = 'login_err'
        else:
            if ('"error":"ok"' in res):
                print('下线成功！')
                self.result = 'logout_succ'
                self.message = '下线成功！'
                return
            elif ('"error_msg":"You are not online."' in res):
                print('你还没有登录！')
                self.message = '你还没有登录！'
            else:
                print('注销发生未知错误! 请反馈给我！')
                self.message = '注销发生未知错误! 请反馈给我！'
                sleep(2)
            self.result = 'logout_err'


class Logic(object):
    def __init__(self, ui):
        self.ui = ui
        self.cf = cp.ConfigParser()
        self.cf.read('config.ini')

    def main(self):
        ## setting combobox: 'username'
        # default
        for user in self.cf['User_infos']:
            self.ui.comboBox.insertItem(0, user)
        self.ui.comboBox.setCurrentText(self.cf.get('Setting', 'Last_user'))
        # username changed, so change passwd
        self.ui.comboBox.activated.connect(lambda: setPasswd())

        ## setting lineEdit: 'passwd'
        #default
        def setPasswd():
            try:
                self.ui.lineEdit.setText(
                    self.cf.get('User_infos', self.ui.comboBox.currentText()))
            except:
                pass

        setPasswd()

        ## setting pushButton: 'login' and 'logout'
        self.ui.pushButton.clicked.connect(lambda: self.login_logout('login'))
        self.ui.pushButton_2.clicked.connect(
            lambda: self.login_logout('logout'))

        ## setting radioButton: 'remeber_me'
        self.ui.radioButton.setChecked(
            self.get_bool(self.cf.get('Setting', 'remeber_me')))
        self.ui.radioButton.toggled.connect(
            lambda: refresh_rem(self.ui, self.cf))

        def refresh_rem(ui, cf):
            if ui.radioButton.isChecked() == True:
                cf.set('Setting', 'remeber_me', '1')
            else:
                cf.set('Setting', 'remeber_me', '0')
            cf.write(open("config.ini", 'w'))

    def get_bool(self, str):
        if str == '1':
            return True
        else:
            return False

    def login_logout(self, method):
        ## 判断登录网络服务商
        if self.ui.comboBox_2.currentText() == '校园网':
            domain = '@xiaoyuanwang'
        elif self.ui.comboBox_2.currentText() == '中国移动':
            domain = '@yidong'
        else:
            domain = '@liantong'
        ## 开始登录
        self.au = Authentication(self.ui.comboBox.currentText() + domain,
                                 self.ui.lineEdit.text())

        if method == 'login':
            self.au.login()
        else:
            self.au.logout()

        ## logging user info
        # fill comboBox
        if self.ui.comboBox.currentText() not in self.cf.options('User_infos'):
            self.ui.comboBox.insertItem(0, self.ui.comboBox.currentText())
        # write config.ini
        if (self.au.result == 'login_succ') or (
                self.au.result == 'logout_succ'):
            if self.cf.get('Setting', 'remeber_me') == '1':
                self.cf.set('User_infos', self.ui.comboBox.currentText(),
                            self.au.password)
            elif self.cf.get('Setting', 'remeber_me') == '0':
                self.cf.set('User_infos', self.ui.comboBox.currentText(), '')

            self.cf.set('Setting', 'last_user', self.ui.comboBox.currentText())
            self.cf.write(open("config.ini", 'w'))

        self.log()

    def log(self):
        '''
        显示登陆信息
        '''
        self.ui.textBrowser.append(self.au.message)


def run():
    ## gui界面设置
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    ## 逻辑处理
    logic = Logic(ui)
    logic.main()

    ## 显示和退出gui界面
    MainWindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()

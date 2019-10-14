import configparser as cp
def setting(cf):
     print('请设置您的登录信息: \n')
     print('网络服务商有三种选择')
     print("校园网: 1 , 中国移动: 2 , 中国联通: 3")
     print('*'*60+'\n')
     while(True):
          domain = input('请输入网络服务商(代号): ')
          if domain == '1':
               domain = '@xiaoyuanwang'
               break
          elif domain == '2':
               domain = '@yidong'
               break
          elif domain == '3':
               domain == '@dianxing'
               break
          else: print('请您确认后重新输入！')
     username = input('请输入用户名(学号): ')
     password = input('请输入密码: ')

     cf.set('Infos', 'username', username)
     cf.set('Infos', 'password', password)
     cf.set('Infos', 'domain', domain)
     cf.set('Default', 'first_time', '0')
     cf.write(open('config.ini', "w"))

if __name__ == '__main__':
     setting()

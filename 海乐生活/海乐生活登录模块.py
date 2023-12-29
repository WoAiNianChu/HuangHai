import json
import glob
import requests
from prettytable import PrettyTable

# 登录模块的代码
headers = {
    'User-Agent': "okhttp/3.14.9",
    'Connection': "Keep-Alive",
    'Accept-Encoding': "gzip",
    'Content-Type': "application/json"
}

get_code_url = "https://yshz-user.haier-ioc.com/login/getCode?platform=Android"
login_url = "https://yshz-user.haier-ioc.com/login/login?platform=Android"
account_info_url = "https://yshz-user.haier-ioc.com/account/getAccountInfo"

# 获取验证码的函数
def get_verification_code(target_number):
    payload = json.dumps({
        "target": target_number,
        "sendType": 1,
        "method": 1
    })
    response = requests.post(get_code_url, data=payload, headers=headers)
    return response.text

# 使用验证码登录的函数
def login_with_verification_code(account, filename):
    login_type = 2
    authorization_client_type = 9

    while True:  
        # 输入验证码
        verification_code_input = input("请输入验证码：")

        payload = {
            "account": account,
            "verificationCode": verification_code_input,
            "loginType": login_type,
            "authorizationClientType": authorization_client_type
        }

        response = requests.post(login_url, data=json.dumps(payload), headers=headers)
        response_data = response.json()

        if response_data.get('message') == "验证码错误":
            print("验证码错误，请重新输入验证码。")
        elif response_data.get('message') == "success":
            print("登录成功")
            token = response_data.get("data", {}).get("token")
            return token
        else:
            print("其他状态：", response_data.get('message'))
            break
    return None

def fill_new_user_info():
    target_input = input("请输入新用户的手机号：")
    name_input = input("请输入新用户的姓名：")
    filename = f"xyj_{target_input}_info.txt"
    
    # 发送验证码
    get_verification_code(target_input)
    print("验证码已发送，请注意查收。")

    # 使用验证码登录并获取token
    token = login_with_verification_code(target_input, filename)
    
    # 一旦登录成功，创建或打开文件，写入用户信息和token
    if token is not None:
        with open(filename, 'w') as f:
            user_info = {"account": target_input, "name": name_input, "token": token}  # 添加token信息
            json.dump(user_info, f)
        print(f"新用户 {name_input} 已添加。")
    
    return target_input, name_input, token, filename

def main():
    info_files = glob.glob('xyj_*_info.txt')
    users = []
    for filename in info_files:
        with open(filename, 'r') as f:
            try:
                user_info = json.load(f)
                users.append((user_info, filename))
            except json.JSONDecodeError:
                print(f"无效的信息文件：{filename}")
  
    table=PrettyTable(["序号", "手机号", "姓名"])
    for index, (user, _) in enumerate(users, start=1):
        table.add_row([index, user.get('account'), user.get('name')])
    print(table)
  
    choice = input("请输入序号或输入'a'添加新用户：")
    if choice.lower() == 'a':
        fill_new_user_info()
    else:
        selected_user, selected_filename = users[int(choice) - 1]
        token = selected_user.get('token')
        if token:
            headers['authorization'] = token
            response = requests.get(account_info_url, headers=headers).json()
            if response.get('message') == 'success':
                print("登录成功")
            else:
                print("登录失败")
                update_choice = input("是否更新用户信息？(y/n): ")
                if update_choice.lower() == 'y':
                    fill_new_user_info()
        else:
            print("未找到有效的token")
            update_choice = input("是否更新用户信息？(y/n): ")
            if update_choice.lower() == 'y':
                fill_new_user_info()
    
    input("按回车键退出程序...")

if __name__ == "__main__":
    main()

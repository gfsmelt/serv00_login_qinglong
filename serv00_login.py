import os
import paramiko
import requests
from notify import send
from dotenv import load_dotenv
# 加载 .env 环境变量（适用于青龙面板）
load_dotenv()
# ============ 配置部分 ============
# SSH 配置
SSH_HOSTS = os.getenv("SSH_HOST", "").split("\n")  # 服务器IP或域名
SSH_PORTS = os.getenv("SSH_PORT", "\n".join(["22"] * len(SSH_HOSTS))).split("\n")  # SSH端口，默认为22
SSH_USERS = os.getenv("SSH_USER", "").split("\n")  # SSH用户名
SSH_PASSWORDS = os.getenv("SSH_PASS", "").split("\n")  # SSH密码
SSH_COMMANDS = os.getenv("SSH_COMMAND", "\n".join(["pwd"] * len(SSH_HOSTS))).split("\n")  # SSH执行命令

# 网页登录配置
WEB_LOGIN = os.getenv("WEB_LOGIN", "false").lower() == "true"  # 是否进行 Serv00 网页登录
WEB_URL = "https://panel2.serv00.com/login/?next=/"  # Serv00 登录地址
WEB_USERNAME = os.getenv("SERV00_WEB_USER", "")  # Serv00 用户名
WEB_PASSWORD = os.getenv("SERV00_WEB_PASS", "")  # Serv00 密码

# ============ SSH 登录函数 ============
def ssh_connect(host, port, username, password, command):
    """
    通过 SSH 连接服务器并执行命令
    """
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 自动接受主机密钥
        client.connect(hostname=host, port=int(port), username=username, password=password)
        print(f"✅ 成功连接到 {host}:{port}")

        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        if error:
            msg = f"⚠️ 连接 {host} 成功，但执行命令出错：{error}"
        else:
            msg = f"✅ 连接 {host} 成功，执行命令输出：{output}"

        print(msg)
        return msg
    except Exception as e:
        msg = f"❌ 连接 {host} 失败：{e}"
        print(msg)
        return msg
    finally:
        client.close()
        print(f"🔌 {host} 连接已关闭")

# ============ Serv00 网页登录函数 ============
import requests
import os
import re

WEB_URL = "https://panel2.serv00.com/login/?next=/"
LOGIN_URL = "https://panel2.serv00.com/login/"

WEB_USERNAME = os.getenv("SERV00_WEB_USER", "")
WEB_PASSWORD = os.getenv("SERV00_WEB_PASS", "")

def web_login():
    try:
        session = requests.Session()

        # 1. 访问登录页面，获取 CSRF 令牌
        login_page = session.get(WEB_URL, headers={"User-Agent": "Mozilla/5.0"})
        login_page_text = login_page.text

        # 2. 尝试从 HTML 页面提取 CSRF 令牌
        match = re.search(r"name='csrfmiddlewaretoken' value='(.*?)'", login_page_text)
        if match:
            csrf_token = match.group(1)
            print(f"✅ 从 HTML 获取 CSRF 令牌：{csrf_token}")
        else:
            csrf_token = session.cookies.get("csrftoken")
            if csrf_token:
                print(f"✅ 从 Cookie 获取 CSRF 令牌：{csrf_token}")
            else:
                print("❌ 未能获取 CSRF 令牌，可能无法登录")
                return "❌ Serv00 登录失败：未获取 CSRF 令牌"

        # 3. 构造登录数据
        login_data = {
            "username": WEB_USERNAME,
            "password": WEB_PASSWORD,
            "csrfmiddlewaretoken": csrf_token,  # 添加 CSRF 令牌
            "next": "/"
        }

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": WEB_URL,  # 添加 Referer，防止 CSRF 保护
            "Origin": "https://panel2.serv00.com"
        }

        # 4. 发送登录请求
        response = session.post(LOGIN_URL, data=login_data, headers=headers, allow_redirects=True)

        # 5. 检查是否登录成功
        if response.status_code == 200 and "dashboard" in response.text.lower():
            msg = "✅ Serv00 网页登录成功"
        else:
            msg = f"❌ Serv00 网页登录失败，返回页面内容：\n{response.text[:500]}"  # 仅打印前500字符

        print(msg)
        return msg

    except Exception as e:
        msg = f"❌ Serv00 网页登录失败：{e}"
        print(msg)
        return msg

    except Exception as e:
        msg = f"❌ Serv00 网页登录失败：{e}"
        print(msg)
        return msg
      
# ============ 主函数 ============
if __name__ == "__main__":
    msgs = "📢 Serv00 保号任务执行结果：\n"

    # 执行 SSH 登录
    if all([SSH_HOSTS, SSH_USERS, SSH_PASSWORDS]):
        for host, port, user, password, command in zip(SSH_HOSTS, SSH_PORTS, SSH_USERS, SSH_PASSWORDS, SSH_COMMANDS):
            msg = ssh_connect(host, port, user, password, command)
            msgs += msg + "\n"

    # 执行 Serv00 网页登录
    if WEB_LOGIN and WEB_USERNAME and WEB_PASSWORD:
        msg = web_login()
        msgs += msg + "\n"

    # 发送通知
    send("Serv00 保号任务", msgs)

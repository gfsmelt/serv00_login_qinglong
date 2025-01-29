# serv00_login_qinglong
青龙登录serv00，ssh+web，自行设置时间规则
===============
环境变量
SSH_HOST
SSH_PASS
SSH_PORT
SSH_COMMAND  #默认小写pwd
WEB_LOGIN  #默认true
SERV00_WEB_USER
SERV00_WEB_PASS
PUSH_PLUS_TOKEN

================
依赖安装paramiko requests jq python-dotenv 
================
在 Docker 版青龙面板 中，安装 paramiko、requests、jq和 python-dotenv 需要进入容器内部进行操作。
docker exec -it qinglong /bin/sh
pip install paramiko requests python-dotenv jq

##ai自动生成的，有问题问ai,本人啥也不懂

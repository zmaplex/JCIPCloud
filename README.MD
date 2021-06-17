**设计说明**

> 预发布阶段，请勿部署生产环境



**功能说明**

> 系统流程

**部署**

```shell script
# 使用虚拟环境
python3 -m venv dj_venv
# 激活虚拟环境
source dj_venv/bin/activate
# 安装依赖
pip install -r requirements.txt
# 复制并修改配置文件
cp .env.template .env && vim .env
# 迁移数据库
python manage.py makemigrations
python manage.py migrate
# 创建超级用户
python manage.py createsuperuser
# 复制静态资源
python manage.py collectstatic
# 启用
source dj_venv/bin/activate && dj_venv/bin/gunicorn --worker-class=gevent --worker-connections=1000 --workers=3  --bind unix:/var/run/jcpmpay.sock JCPMPay.wsgi:application
```



**nginx 配置参考**
```
    ...
    location / {
      proxy_pass http://unix:/var/run/jcpmpay.sock;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /static {
      autoindex on;
      alias  /your_project_directory/static;
    }
    
    location /media {
      autoindex on;
      alias  /your_project_directory/media;
    }
    ...
```
**待续**

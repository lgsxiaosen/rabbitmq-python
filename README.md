# 使用说明
1. 安装mq，命令启用mq相关插件
    rabbitmq-plugins enable rabbitmq_management rabbitmq_web_stomp rabbitmq_stomp
    rabbitmq_web_stomp运行在15674端口

2. 检查test.py内的配置是否正确

    test.py文件：
    34-35行celery配置
    CELERY_BROKER_URL='amqp://guest:guest@10.237.43.101/net_test',
    CELERY_RESULT_BACKEND='redis://:travelskyopenstackcloud@10.237.43.105:6379/0'

    53-56行mq配置
    # mq configuration
    mq_host = '127.0.0.1'
    mq_port = 5672
    queue = 'push_queue1'

    html/rabbitmq-web-stomp.html文件：
    103行websocket配置stomp服务地址，测试的时候跑在本地127.0.0.1的mq上
    var ws = new WebSocket('ws://127.0.0.1:15674/ws');
    115行websocket配置对应mq队列配置，对应push_queue1这个队列
    client.subscribe("/queue/push_queue1", function(d) {

2. pycharm中运行test.py

3. cmd中进入虚拟环境，在虚拟环境下执行celery worker -l INFO -A test.celery运行celery任务

4. 浏览器直接打开html/rabbitmq-web-stomp.html文件，界面直接订阅读取mq的消息

5. 点击页面发送同步请求按钮，相当于调用后台接口http://127.0.0.1:5002/sync，起送一个发送mq消息的celery任务

6. 等待一会页面会显示对应的mq消息

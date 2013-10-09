            小迈学围棋
            版本：0.0.2

介绍：
    本软件是个人围棋题目训练软件，相关习题及flash 练习程序皆来自网上，如有侵权请联系本人。
    目前版本较低，只适合单人练习，将来会添加练习结果统计功能。

安装：
    1）需要python2.5以上。
    2）如果需要附加的python模块，请自行安装。
    3）无需其他附件。

运行：
    在xp/ubuntu 12.04上测试过，可以运行，其他平台没有测试。
    如果在Windows xp平台，直接双击运行：
        xmgo\server\run.bat
        然后在浏览器中输入http://localhost:9158/
    如果在linux平台，在控制台下运行：
        cd xmgo/server/
        bash ./run.sh
        然后在浏览器中输入http://<linux-ip>:9158/

    当然，如果9158端口在本机被占用，请修改其他端口号, 修改方法如下：
        1) 编辑文件: xmgo\server\conf\websrv.conf
        2) 找到如下行：
           server.socket_port = 9158
        3) 修改合适的端口号后保存文件
        4) 重启该程序。

guohong.xie@gmail.com
2013/09/18

#!/bin/sh
#
# xmgo - this script starts and stops the xmgo daemon
#
# chkconfig:   - 85 15
# description: xmgo chess training  
#              
# processname: xmgo
# config:      /etc/xmgo/xmgo.conf
# pidfile:     /var/run/xmgo.pid

# Source function library.
. /etc/rc.d/init.d/functions

# Source networking configuration.
. /etc/sysconfig/network

# Check that networking is up.
[ "$NETWORKING" = "no" ] && exit 0


lockfile="/var/lock/subsys/xmgo"
pidfile="/var/run/${prog}.pid"

PROG_PATH=/root/xmgo/server

start() {
    echo -n $"Starting $prog: "
    cd ${PROG_PATH}
    python ./xmgo-daemon.py start
    retval=$?
    return $retval
}

stop() {
    echo -n $"Stopping $prog: "
    cd ${PROG_PATH}
    curl http://localhost:9158/priv?cmd=shutdown
    retval=$?
    return $retval
}

restart() {
    stop
    start
}

reload() {
    echo -n $"Reloading $prog: "
    killproc -p $pidfile $prog -HUP
    echo
}

case "$1" in
    start)
        start && exit 0
        ;;
    stop)
        stop || exit 0
        ;;
    restart)
        restart 
        ;;
    status)
        ;;
    *)
        echo $"Usage: $0 {start|stop|status|restart}"
        exit 2
esac


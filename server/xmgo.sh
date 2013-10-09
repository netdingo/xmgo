#!/bin/sh
### BEGIN INIT INFO
# Provides:          xmgo.sh
# Required-Start:    $local_fs 
# Required-Stop:     $local_fs 
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts xmgo daemon
# Description:       starts xmgo daemon with python
### END INIT INFO

PROG_PATH=/root/xmgo/server
do_start()
{
    cd ${PROG_PATH}
    python ./xmgo-daemon.py start
}
do_stop()
{
    cd ${PROG_PATH}
    wget http://localhost:9158/priv?cmd=shutdown
}

case "$1" in
start)
do_start
;;
stop)
do_stop
;;
*)
echo "useage:xmgo-daemon.py {start|stop}"
exit 1
;;
esac

exit 0

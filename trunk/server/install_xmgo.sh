#!/bin/sh
PROG_PATH=/root/xmgo/server
INIT_PATH=/etc/init.d
SCRIPT=xmgo.sh
cp -f ${PROG_PATH}/$SCRIPT ${INIT_PATH}
chmod +x ${INIT_PATH}/$SCRIPT
[ ${INIT_PATH}/$SCRIPT ] && update-rc.d $SCRIPT defaults

#!/bin/sh
PROG_PATH=/root/xmgo/server
INIT_PATH=/etc/init.d
SCRIPT=xmgo.sh
UBUNTU_SCRIPT=$SCRIPT
REDHAT_SCRIPT=xmgo-redhat.sh
issue=/etc/issue

function install_redhat(){
    if chkconfig --list $SCRIPT; then
       service $SCRIPT stop;
       chkconfig --del $SCRIPT;
    fi
    cp -f ${PROG_PATH}/$REDHAT_SCRIPT ${INIT_PATH}/$SCRIPT
    chmod +x ${INIT_PATH}/$SCRIPT
    chkconfig --add $SCRIPT
    chkconfig --level 2345 $SCRIPT on
}

function check_release(){
    for rel in 'redhat' 'centos' 'fedora'; do
       if grep -i $rel $issue > /dev/null; then
          echo 'redhat';
          return;
       fi
    done
    if grep -i 'ubuntu' $issue > /dev/null; then
        echo 'ubuntu';
    else 
        echo 'unknown'
    fi
}

release=$(check_release)
if [ $release = 'redhat' ]; then
    install_redhat;
elif [ $release = 'ubuntu' ]; then
    cp -f ${PROG_PATH}/$UBUNTU_SCRIPT ${INIT_PATH}/$SCRIPT
    chmod +x ${INIT_PATH}/$SCRIPT
    [ ${INIT_PATH}/$SCRIPT ] && update-rc.d $SCRIPT defaults
else
   echo "unknown linux release!"
fi


#!/bin/bash

COMMAND="systemctl status $1 -n0"
STATUS=3
OUTPUT=`$COMMAND 2>&1`; EXITCODE=$?; [ "$EXITCODE" -eq 0 ] && STATUS=0 || STATUS=2
RESULT=`$COMMAND 2>&1|egrep 'Active|Main PID'|tr -d '\n'`
case $STATUS in
        0) echo "OK - `echo $RESULT`";;
        2) echo "CRITICAL - `echo $RESULT`";;
        *) echo "UNKNOWN - `echo $RESULT`";;
esac
exit $STATUS


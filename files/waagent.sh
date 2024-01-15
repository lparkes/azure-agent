#!/bin/sh

# PROVIDE: waagent
# REQUIRE: sshd dhcpcd

. /etc/rc.subr

name="waagent"
rcvar="${name}"
pidfile="/var/run/waagent.pid"
command="@PREFIX@/sbin/${name}"
command_interpreter=@PYTHON@
command_args="-start"

load_rc_config $name
run_rc_command "$1"

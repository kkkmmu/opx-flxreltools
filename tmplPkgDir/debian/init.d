#!/bin/sh
### BEGIN INIT INFO
# Provides:          flexswitch
# Required-Start:    $local_fs $network $remote_fs $syslog
# Required-Stop:     $local_fs $network $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: <Network Software>
# Description:       <Protocols , ASIC Manager and other infrastructure components for making a white box switch work>
### END INIT INFO

# Author: Hari <hari@snaproute.com>

# Do NOT "set -e"

# PATH should only include /usr/ if it runs after the mountnfs.sh script
#
# Function that starts the daemon/service
#
do_start()
{
	/opt/flexswitch/flexswitch --op=start
}

#
# Function that stops the daemon/service
#
do_stop()
{
	/opt/flexswitch/flexswitch --op=stop
}

#
# Function that checks daemon/service
#
#
# Function that sends a SIGHUP to the daemon/service
#
do_reload() {
	do_stop
	do_start
}

case "$1" in
  start)
	do_start
	;;
  stop)
	do_stop
	;;
  restart|force-reload)
	do_stop
	do_start
	;;
  *)
	#echo "Usage: $SCRIPTNAME {start|stop|restart|reload|force-reload}" >&2
	echo "Usage: $SCRIPTNAME {start|stop|status|restart|force-reload}" >&2
	exit 3
	;;
esac

:

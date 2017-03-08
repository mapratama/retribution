#!/bin/bash
 
HOST=localhost
USER=root
PASSWORD=root
OPTS="-aoCm --auto-repair"
PART=${1:-$[`date +%u`-1]}
PERIOD=${2:-7}
me=`dirname $0`/`basename $0`
 
# Uncomment to silence the script
#exec >/dev/null
 
mysqloptimize $OPTS --user=$USER \
    --password=$(grep "^ *PASSWORD=" $me | head -1 | cut -d= -f2-) \
    --databases mysql `mysqlshow \
            --user=$USER \
            --password=$(grep "^ *PASSWORD=" $me | head -1 | cut -d= -f2-) |
            tail -n +4 |
            grep '^| [^ ]' |
            gawk -v d=$PART -v mod=$PERIOD -- \
                '{ if (((NR - 1) % mod) == d) print $2; }'`
 
# End of file.

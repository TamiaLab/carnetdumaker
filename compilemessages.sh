#!/usr/bin/env bash

here=`pwd`
echo Compile .mo in root
python $here/manage.py compilemessages

for d in apps/*/ ; do
    if [[ $d != *"__pycache__"* ]]
    then
        echo Compile .mo in $d
        (cd $d && python $here/manage.py compilemessages)
    fi
done

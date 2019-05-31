#!/bin/bash

export PATH=$PATH:/usr/cachesys/bin
export LD_LIBRARY_PATH=/lib64:/home/webreg/cachesys/bin

envdir=/home/webreg/env/
projectdir=/home/webreg/webreg/webreg/

$envdir/bin/python $projectdir/manage.py loadspecialists skc
$envdir/bin/python $projectdir/manage.py loadspecialists kb42

$envdir/bin/python $projectdir/manage.py loadavailspecialists skc patient_writer
$envdir/bin/python $projectdir/manage.py loadavailspecialists kb42 patient_writer

$envdir/bin/python $projectdir/manage.py loadavailservices skc patient_writer
$envdir/bin/python $projectdir/manage.py loadavailservices kb42 patient_writer

$envdir/bin/python $projectdir/manage.py loadtimetable skc
$envdir/bin/python $projectdir/manage.py loadtimetable kb42



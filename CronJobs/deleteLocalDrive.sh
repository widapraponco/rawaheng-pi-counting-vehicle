#!/usr/bin/env bash
SUBSTRACT=$1" days ago"
echo $SUBSTRACT
FOLDER="/home/pi/drive/"`date +%Y/%-m/%-d --date="$SUBSTRACT"`
echo "delete "$FOLDER
rm -r $FOLDER 
#echo $DAY_NUM

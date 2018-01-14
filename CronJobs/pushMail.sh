#!/usr/bin/env bash
# upload to drive first before push mail
FOLDER="/home/pi/drive/"`date +%Y/%-m/%-d`
#LINK=`drive url $FOLDER` && echo $LINK &&
#python /home/pi/Projects/flask-video-streaming/smtp_manager.py widapraponco02@gmail.com --link "$LINK"
#arif.p213@gmail.com --cc trianalestari063@gmail.com --bcc
PROJECT="/home/pi/Projects/flask-video-streaming/"

echo "y" | drive share -type anyone -with-link $FOLDER && 
LINK=`drive url $FOLDER` && 
python $PROJECT/smtp_manager.py arif.p213@gmail.com --cc trianalestari063@gmail.com --bcc widapraponco@live.com --link "$LINK" && 
python $PROJECT/data_manager.py json calculate
#echo "y" | drive push $FOLDER

import smtplib
import csv
import time
import os
import argparse
from _global import get_saving_dir
from data_manager import JSONDataManager

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

parser = argparse.ArgumentParser()
parser.add_argument("to", help="destination address for this mail will be sent")
parser.add_argument("--csv", help="optional csv file, if is not defined will get the last csv file")
parser.add_argument("--row", help="optional select row to be sent, if not defined will be sent all row ex: 2 4 means 2 to 4 row", nargs='+')
parser.add_argument("--link", help="optional link to add at the end of this mail")
parser.add_argument("--cc", help="mail cc, add space to more cc", nargs='+')
parser.add_argument("--bcc", help="mail bcc, add space to more bcc", nargs='+')
parser.add_argument("--flag", help="active summary mail to be sent", nargs='?', default=False)
args = parser.parse_args()

#if args.flag:
#   print (args.flag)

if not args.to:
   print "no address destination"
   exit(0)

file_dir = args.csv
if not args.csv:
   file_dir = get_saving_dir()+"/"+"data.csv"

if not os.path.exists(file_dir):
   print str(file_dir+" file not found in your directory, please use full directory")

#mail to in every 8 hours
SUBJECT = "Laporan Otomatis Berkala Deteksi Kendaraan Rawaheng"
if args.flag:
   SUBJECT = "Rekapitulasi Data"
from_addr = 'sitamoto.device01@gmail.com'
to_addr = args.to

cc = []
cc_str = ''
if args.cc:
   cc = args.cc
   for i, c in enumerate(cc):
     if i > 0:
        cc_str += ','
     cc_str += c

#print (cc_str)

bcc = []
bcc_str = ''
if args.bcc:
   bcc = args.bcc
   for i, b in enumerate(bcc):
     if i > 0:
        bcc_str += ','
     bcc_str += b

#Open the csv file
reader = csv.reader(open(file_dir))
jsonData = JSONDataManager()
#write the HTML in string
#msg_body = "<title>Laporan Berkala Tambang Batu Rawaheng</title>"
msg_body = "<body><p>"+jsonData.get_last_mail()+"-"+time.strftime('%A %B, %d %Y %H:%M:%S')+"</p>"
if args.flag:
   msg_body = "<body><p>"+time.strftime('%A %B, %d %Y %H:%M:%S')+"</p>"

msg_body += "<table style='border: 1px solid black;'>"

#start from data not header
start_row = 1
end_row = len(reader)
if args.row is not None:
   start_row = args.row[0]
   end_row = args.row[1]
else:
   rows = jsonData.get_row()
   start_now = rows[0]
   end_row = rows[1]

big_count = 0
small_count = 0

#write header
header = ["no", "date", "category"]
msg_body += "<tr>"
for h in header:
    msg_body+="<th>"+h.upper()+"</th>"
msg_body += "</tr>"

for i, row in enumerate(reader):
    if i < 1 or (i < start_row or  i >= end_row):
       continue
 
    if start_row%2 :
       msg_body += '<tr style="background-color: grey;">'
    else:
       msg_body += '<tr style="background-color: white;">'

    for j, column in enumerate(row):
        if i < 1: #header
           msg_body += "<th>"+column.upper()+"</th>"
        else:
           if column == 'big':
              big_count += 1
           elif column == 'small':
              small_count += 1

           msg_body += '<td>' + column + '</td>'

    msg_body += "</tr>"

msg_body += "</table><br>"
msg_body += "<p>Total tipe big:"+big_count+"<p><br>"
msg_body += "<p>Total tipe small:"+small_count+"<p><br>"
#video link here
if args.link is not None: 
   msg_body += "<p>berikut tautan gambar kendaraan dan video pada tanggal ini di laman google drive: "+args.link+"</body>"

#print (msg_body)
msg_part = MIMEText(msg_body, 'html')

message = MIMEMultipart('alternative')
message['Subject'] = SUBJECT
message['To'] = to_addr
message['Cc'] = cc_str
message['Bcc'] = bcc_str
message.attach(msg_part)

to_addrs = [to_addr] + cc + bcc
#try:
server = smtplib.SMTP('smtp.gmail.com', 587)
server.ehlo()
server.starttls()
#server.connect('smtp.gmail.com', 25)
server.login(from_addr, "epllcsrivawsgzqm")
server.sendmail(from_addr,to_addrs, message.as_string())
print ('email sent')
server.close()
#except:
#   print ('failed to send mail')

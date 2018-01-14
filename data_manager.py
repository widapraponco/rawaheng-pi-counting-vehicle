import json
import io
import sys
try:
   to_unicode = unicode
except NameError:
   to_unicode = str

import os, errno
from _global import *

#if len(sys.argv) < 3 and sys.argv[1] == 'json':
#   print(len(sys.argv))
#   print ("json reset")

#if len(sys.argv) < 7 and sys.argv[1] == 'csv':
   #print (len(sys.argv))
#   print ("csv <FILE_DIR> -update <COLUMN_NAME> <REPLACE_DATA> <NEW_DATA>")

if len(sys.argv) > 2 and sys.argv[1] == 'json' and sys.argv[2] == 'reset-all':
   with open('/home/pi/Projects/flask-video-streaming/counter.json', 'r+') as jsonfile:
        data = json.load(jsonfile)
        data["big"]["total"] = 0
        data["small"]["total"] = 0
        data["big"]["inaday"]["total"] = 0
        data["big"]["inaday"]["report"] = 0
        data["small"]["inaday"]["total"] = 0
        data["small"]["inaday"]["report"] = 0
        jsonfile.seek(0)
        json.dump(data, jsonfile)
        jsonfile.truncate()
        print(data)

if len(sys.argv) > 2 and sys.argv[1] == 'json' and sys.argv[2] == 'reset-day':
   with open('/home/pi/Projects/flask-video-streaming/counter.json', 'r+') as jsonfile:
        data = json.load(jsonfile)
        data["big"]["inaday"]["total"] = 0
        data["big"]["inaday"]["report"] = 0
        data["small"]["inaday"]["total"] = 0
        data["small"]["inaday"]["report"] = 0
        jsonfile.seek(0)
        json.dump(data, jsonfile)
        jsonfile.truncate()
        print(data)

if len(sys.argv) > 2 and sys.argv[1] == 'json' and sys.argv[2] == 'calculate':
   with open('/home/pi/Projects/flask-video-streaming/counter.json', 'r+') as jsonfile:
        data = json.load(jsonfile)
        big_inaday = data["big"]["inaday"]
        small_inaday = data["small"]["inaday"]

        if len(sys.argv) > 3 and sys.argv[3] == 'day':
           data["big"]["total"]+=big_inaday["total"]
           data["small"]["total"]+=small_inaday["total"]
           #reset inaday total
           big_inaday["total"] = 0
           small_inaday["total"] = 0
        else:
           small_inaday["total"] += small_inaday["report"]
           big_inaday["total"] += big_inaday["report"]
           #reset inaday report
           small_inaday["report"] = 0
           big_inaday["report"] = 0

        jsonfile.seek(0)
        json.dump(data, jsonfile)
        jsonfile.truncate()
        print(data)

if len(sys.argv) > 6 and sys.argv[1] == 'csv' and sys.argv[3] == '-update':
   csv_file = sys.argv[2]
   column_name = sys.argv[4]
   replace_data = sys.argv[5]
   new_data = sys.argv[6]

   with open(csv_file, 'r') as csvfile, tempfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        reader = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for row in reader:
            if row[column_name] == replace_data:
               print('updating row', row[column_name])
               row[column_name] = new_data

            row = {'no': row['no'], 'tanggal': row['tanggal'], 'tipe': row['tipe'], 'tautan gambar': row['tautan gambar']}
            writer.writerow(row)
        shutil.move(tempfile.name, self.dataFile)

class JSONDataManager():
      def __init__(self):
          self.dataFile = '/home/pi/Projects/flask-video-streaming/counter.json'
          if not os.path.exists(self.dataFile): 
             data = {"metadata": {"last_mail": "0"}, "big": {"inaday": {"total": 0, "report":0}, "total": 0}, "small": {"inaday":{"total": 0, "report":0}, "total": 0}}
             with open(self.dataFile,'w') as outfile:
                  json.dump(data, outfile)
                  #outfile.write(str(data))

      def get_row(self):
          row = []
          print(self.dataFile)
          with open(self.dataFile) as jsonfile:
                  data = json.load(jsonfile)
                  start_row = data["big"]["inaday"]["total"] + data["small"]["inaday"]["total"]
                  if start_row == 0:
                     start_row = 1
                  end_row = start_row + (data["big"]["inaday"]["report"]+data["small"]["inaday"]["report"])
                  row = [start_row, end_row]
          return row

      def get_total(self, jsonobj=None):
          count = 0
          with open(self.dataFile) as feedjson:
               data = json.load(feedjson)
               big_total = data["big"]["total"] + data["big"]["inaday"]["total"] + data["big"]["inaday"]["report"]
               small_total = data["small"]["total"] + data["small"]["inaday"]["total"] + data["small"]["inaday"]["report"]
               if jsonobj is None:
                  count = big_total + small_total
               else:
                  if jsonobj == "big":
                     count = big_total
                  else:
                     count = small_total

          return count

      def get_total_inaday(self, jsonobj=None):
          count = 0
          with open(self.dataFile) as feedjson:
               data = json.load(feedjson)
               big_total = data["big"]["inaday"]["total"] + data["big"]["inaday"]["report"]
               small_total = data["small"]["inaday"]["total"] + data["small"]["inaday"]["report"]
               if jsonobj is None:
                  count = big_total + small_total
               else:
                  if jsonobj == "big":
                     count = big_total
                  else:
                     count = small_total

          return count
      
      def get_last_mail(self):
          last_mail = ""
          print(self.dataFile)
          with open(self.dataFile) as feedjson:
               data = json.load(feedjson)
               last_mail = data["metadata"]["last_mail"]

          return last_mail

      def set_init_last_mail(self):
          with open(self.dataFile,'r+') as feedjson:
               data = json.load(feedjson)
               #print(data)
               data["metadata"]["last_mail"]= get_current_timestamp_str("%Y/%m/%d %H:%M:%S")
               feedjson.seek(0)
               json.dump(data, feedjson)
               feedjson.truncate()
      
      def counting(self, tipe, adder = 1):
          with open(self.dataFile, 'r+') as feedjson:
               data = json.load(feedjson)
               json_obj = "small"
               if tipe == 1:
                  json_obj = "big"
               count = data[json_obj]["inaday"]["total"]+data[json_obj]["inaday"]["report"]
               #print("counter_before"+count)
               count = count + adder
               #print("counter_after:"+count)
               data[json_obj]["inaday"]["report"] = count
               #print(str(count)) 
               feedjson.seek(0) 
               json.dump(data, feedjson)
               feedjson.truncate()
               #feedjson.write(str(data))
          return 0
          
      def add_data(self, jsondata):
          with open(self.dataFile, 'w', 'utf-8') as feedsjson:
               feedsjson.append(jsondata)
               json.dump(data, feedsjson)
          
import csv
import os, errno
from _global import *

class CSVDataManager():
      def __init__(self):
          self.dataFile = get_saving_dir()+"/"+'data.csv'
          #check csv file existence
          isExist = os.path.exists(self.dataFile)

          with open(self.dataFile, 'a') as csvfile:
               fieldnames = ['no', 'tanggal', 'tipe']
               self.writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
               self.reader = csv.DictWriter(csvfile, fieldnames=fieldnames)
               if not isExist:
                  self.writer.writeheader()

      def add_row(self, vehicle):
          with open(self.dataFile, 'a') as csvfile:
               fieldnames = ['no', 'tanggal', 'tipe']
               self.writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
               self.writer.writerow({'no': str(vehicle.order), 'tanggal': str(vehicle.timestamp), 'tipe': str(vehicle.type)})
      
      def update_row(vehicle):
          with open(self.dataFile, 'r') as csvfile, tempfile:
               for row in self.reader:
                   if row['no'] == str(vehicle.order):
                      print('updating row', row['id'])
                      row['tautan gambar'] = vehicle.picture_link

                   row = {'no': row['no'], 'tanggal': row['tanggal'], 'tipe': row['tipe'], 'tautan gambar': row['tautan gambar']}
                   self.writer.writerow(row)
          shutil.move(tempfile.name, self.dataFile)

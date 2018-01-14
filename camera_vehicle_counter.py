import cv2
import math
import numpy as np
import os
from base_camera import BaseCamera
from helper import Helper, Centroid
from _global import *
from data_manager import JSONDataManager

from vehicle_counter import VehicleCounter

class Camera(BaseCamera):
    #video_source = 0
    # Colours for drawing on processed frames
    DIVIDER_COLOUR = (255, 255, 0)
    BOUNDING_BOX_COLOUR = (255, 0, 0)
    CENTROID_COLOUR = (0, 0, 255)

    car_counter = None

    def set_video_source(self, source):
        print("set source")
        self.video_source = source

    def get_counter_inaday(self):
        if self.car_counter is not None:
             return self.car_counter.jsonData.get_total_inaday()
        
        return 0

    def get_counter(self):
        if self.car_counter is not None:
             return self.car_counter.jsonData.get_total()

    def frames(self):
        jsonData = JSONDataManager()
        jsonData.set_init_last_mail()
        camera = cv2.VideoCapture(0) #"/home/pi/drive/2018/1/13/video_12.avi")
        #camera.set(3, 1920)
        #camera.set(4, 1080)
        if not camera.isOpened():
           os.system('sudo reboot')
           raise RuntimeError('Could not start camera.')

        fourcc = cv2.VideoWriter_fourcc(*'DIVX')

        while True:
            ret, frame = camera.read()
            if ret:
               height = frame.shape[0]
               length = frame.shape[1]
               break
            else:
               print ('no frame')

        #capture line
        DIVIDER1 = (DIVIDER1_A, DIVIDER1_B) = ((length // 5, height//2-30), (length - (length//5), height//2-30))
        #counter line 
        DIVIDER2 = (DIVIDER2_A, DIVIDER2_B) = ((50, height//5-20), (length // 6, 30))
        DIVIDER3 = (DIVIDER3_A, DIVIDER3_B) = ((70, height//4), (length // 2, 40))
        DIVIDER4 = (DIVIDER4_A, DIVIDER4_B) = ((70, height//4 + 30), (length//2 + 100, height//4+10))
        #DIVIDER5 = (DIVIDER5_A, DIVIDER5_B) = ((int(length / 3), 250), (int(length / 3), 140))
        #DIVIDER6 = (DIVIDER6_A, DIVIDER6_B) = ((int(length / 5 * 4), 250), (int(length / 5 * 4), 140))

        bg_subtractor = cv2.createBackgroundSubtractorMOG2()
        #car_counter = None

        now = get_server_time()
        directory = get_saving_dir()
        output_name = self.get_video_output_dir()
        out = cv2.VideoWriter(output_name, fourcc, 20.0, (640,480))

        while True:
            # read current frame
            ret, img = camera.read()
            if ret:
               normal_image = img.copy()
               # img = cv2.resize(img, (480, 640))
               # check if the time not the same folder
               if directory != get_saving_dir():
                  out.release()
                  directory = get_saving_dir()
                  output_name = self.get_video_output_dir() 
                  out = cv2.VideoWriter(output_name, fourcc, 20.0, (640,480))

               if self.car_counter is None:
                   self.car_counter = VehicleCounter(img.shape[:2], DIVIDER1, DIVIDER2, DIVIDER3, DIVIDER4) #, DIVIDER2, DIVIDER3, DIVIDER4, DIVIDER5, DIVIDER6)

               # Camera.process_frame(img, DIVIDER1, DIVIDER2, DIVIDER3, DIVIDER4, DIVIDER5, DIVIDER6) 
               
               #capture line
               cv2.line(img, DIVIDER1_A, DIVIDER1_B, self.DIVIDER_COLOUR, 1)
               cv2.putText(normal_image, ("%s" % get_current_timestamp_str('%Y-%m-%d %H:%M:%S %Z')), (20, 20)
                  , cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 2)
               cv2.putText(img, ("%s" % get_current_timestamp_str('%Y-%m-%d %H:%M:%S %Z')), (20, 20)
                  , cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 2)
               
               #counter line
               cv2.line(img, DIVIDER2_A, DIVIDER2_B, (0, 0, 255), 1)
               cv2.line(img, DIVIDER3_A, DIVIDER3_B, (0, 0, 255), 1)
               cv2.line(img, DIVIDER4_A, DIVIDER4_B, (0, 0, 255), 1)
               #cv2.line(img, DIVIDER4_A, DIVIDER4_B, self.DIVIDER_COLOUR, 1)
               #cv2.line(img, DIVIDER5_A, DIVIDER5_B, self.DIVIDER_COLOUR, 1)
               #cv2.line(img, DIVIDER6_A, DIVIDER6_B, self.DIVIDER_COLOUR, 1)

               fg_mask = bg_subtractor.apply(img, None, 0.01)
               fg_mask = self.filter_mask(fg_mask)

               matches = self.detect_vehicles(fg_mask)
               
               #prevent to much record and big data
               #if len(matches) > 0:
               #   out.write(normal_image)
               out.write(normal_image)
               
               for(i, match)in enumerate (matches):
                     centroid = match
                     #mark the bounding box and the centroid to be processed
                     cv2.circle(img, (centroid.x, centroid.y), 2, Camera.CENTROID_COLOUR, -1)
                     
               last_count = self.get_counter(self)
               self.car_counter.update_count(matches, last_count, img, normal_image)
          
               # encode as a jpeg image and return it
               yield cv2.imencode('.jpg', img)[1].tobytes()
            else :
               break

    def get_video_output_dir():
        directory = get_saving_dir()
        fd = len([f for f in os.listdir(directory)
               if f.endswith('.avi') and os.path.isfile(os.path.join(directory,f))])
        return directory+"/"+"video_"+str(fd)+".avi"

    def detect_vehicles(fg_mask):

        MIN_CONTOUR_WIDTH = 100
        MIN_CONTOUR_HEIGHT = 20

        #find contours of any vehicles in the image
        image,contours,hierarchy = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        matches = []
        centroid_aftercal = []
        
        for (i, contour) in enumerate(contours):
             #print contour
             (x, y, w, h) = cv2.boundingRect(contour)
             contour_valid = (w >= MIN_CONTOUR_WIDTH) and (h >= MIN_CONTOUR_HEIGHT)

             if not contour_valid:
                continue
           
             centroid = Helper.get_centroid(x,y,w,h)
             matches.append(centroid)

        #print(matches)
        centroid_combined = Helper.combined_nearby_centroid(matches)
        for entry in centroid_combined:
             tempx = []
             tempy = []
             temph = 0
             tempw = 0
             for centroid in entry:
                  tempx.append(centroid.x)
                  tempy.append(centroid.y)
                  temph += centroid.h
                  tempw += centroid.w
                  
             new_centroid = Centroid(sum(tempx)//len(tempx), sum(tempy)//len(tempy), tempw, temph)
             centroid_aftercal.append(new_centroid)
             #centroid_aftercal.append((sum(tempx)//len(tempx), sum(tempy)//len(tempy)))

        return centroid_aftercal

    def filter_mask(fg_mask):
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
        #fill any small holes
        closing = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)
	#dilate to merge adjacent blobs
        dilation = cv2.dilate(opening, kernel, iterations = 2)
        return dilation

    def process_frame(processed, divider1, divider2, divider3, divider4, divider5, divider6) :
        cv2.line(processed, divider1[0][0], divider1[0][1], Camera.DIVIDER_COLOUR, 1)
        #cv2.line(processed, Camera.DIVIDER2_A, Camera.DIVIDER2_B, Camera.DIVIDER_COLOUR, 1)
        #cv2.line(processed, Camera.DIVIDER3_A, Camera.DIVIDER3_B, Camera.DIVIDER_COLOUR, 1)
        #cv2.line(processed, Camera.DIVIDER4_A, Camera.DIVIDER4_B, Camera.DIVIDER_COLOUR, 1)
        #cv2.line(processed, Camera.DIVIDER5_A, Camera.DIVIDER5_B, Camera.DIVIDER_COLOUR, 1)
        #cv2.line(processed, Camera.DIVIDER6_A, Camera.DIVIDER6_B, Camera.DIVIDER_COLOUR, 1)

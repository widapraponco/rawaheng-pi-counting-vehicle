import logging
import math
import cv2
import numpy as np
from data_manager import CSVDataManager, JSONDataManager

from enum import Enum

from _global import *

# ============================================================================

CAR_COLOURS = [ (0,0,255), (0,106,255), (0,216,255), (0,255,182), (0,255,76)
    , (144,255,0), (255,255,0), (255,148,0), (255,0,178), (220,0,255) ]

# ============================================================================

# OUTPUT_DIR = "vehicleImages/"

class VehicleType(Enum):
    small = 1
    big = 2

class Vehicle(object):
    def __init__(self, id, centroid):
        self.id = id
        self.name = "Vehicle_"+str(id)
        self.order = 0
        self.timestamp = 0
        self.plate_number = "NA"
        self.file_name = "vehicle"
        self.picture_link = "http://localhost"
 
        self.positions = [(centroid.x, centroid.y)] #[position]
        self.frames_since_seen = 0
        self.counted1 = False
        self.counted2 = False
        self.counted3 = False
        self.counted4 = False
        self.counted5 = False
        self.counted6 = False

        self.height = centroid.h
        self.width = centroid.w
        
        #define big or small vehicle here
        self.type = VehicleType.small.name
        if self.width > 100 or self.height > 200:
           self.type = VehicleType.big.name

    def add_position(self, new_position):
        self.positions.append(new_position)
        self.frames_since_seen = 0

    def draw(self, output_image):
        car_colour = CAR_COLOURS[self.id % len(CAR_COLOURS)]
        for point in self.positions:
            cv2.circle(output_image, point, 2, car_colour, -1)
            cv2.polylines(output_image, [np.int32(self.positions)]
                , False, car_colour, 1)

    def get_image(self, width, height, output_image, drawRect = False):
        latest_position = self.positions[len(self.positions)-1]
        x = latest_position[0] - (width//2)
        y = latest_position[1] - (height//2)

        vehicle_image = output_image[y:y+height, x:x+width] 
        
        #draw rect
        if drawRect:
           cv2.rectangle(output_image, (x,y), (x+width, y+height), (0,255,0), 2)
           cv2.putText(output_image, ("%s" % self.type), (x, y)
                  , cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1)
        return vehicle_image

    def draw_rect(self, width, height, output_image):
        #center = self.positions[len(self.positions)-1]
        #x = center[0] - (width//2)
        #y = center[1] - (height//2)
        #roi_vehicle = output_image[x:y, width:height]
        #cv2.rectangle(output_image, (x,y), (x+width,y+height), (0,255,0), 2)
        self.get_image(self.width, self.height, output_image, True)
    
    def save_picture(self, name, width, height, output_image):
        #global OUTPUT_DIR
        # save to system backup folder
        self.file_name = name+".jpg"
        directory = get_saving_dir()
        out = directory+"/"+self.file_name
        #img = self.get_image(self.width, self.height, output_image)
        cv2.imwrite(out, output_image) 

# ============================================================================

class VehicleCounter(object):
    def __init__(self, shape, divider1, divider2 = [(0,0), (0,0)], divider3 = [(0,0), (0,0)], divider4 = [(0,0), (0,0)], divider5 = [(0,0), (0,0)], divider6  = [(0,0), (0,0)]):
        #initialize data manager
        self.data_manager = CSVDataManager()
        self.jsonData = JSONDataManager()

        #self.height, self.width = shape

        self.divider1a_x, self.divider1a_y = divider1[0][0], divider1[0][1]
        self.divider1b_x, self.divider1b_y = divider1[1][0], divider1[1][1]
        self.divider2a_x, self.divider2a_y = divider2[0][0], divider2[0][1]
        self.divider2b_x, self.divider2b_y = divider2[1][0], divider2[1][1]
        self.divider3a_x, self.divider3a_y = divider3[0][0], divider3[0][1]
        self.divider3b_x, self.divider3b_y = divider3[1][0], divider3[1][1]
        self.divider4a_x, self.divider4a_y = divider4[0][0], divider4[0][1]
        self.divider4b_x, self.divider4b_y = divider4[1][0], divider4[1][1]
        self.divider5a_x, self.divider5a_y = divider5[0][0], divider5[0][1]
        self.divider5b_x, self.divider5b_y = divider5[1][0], divider5[1][1]
        self.divider6a_x, self.divider6a_y = divider6[0][0], divider6[0][1]
        self.divider6b_x, self.divider6b_y = divider6[1][0], divider6[1][1]
        
        self.vehicles = []
        self.next_vehicle_id = 0
        self.vehicle_count1 = 0
        self.vehicle_count2 = 0
        self.vehicle_count3 = 0
        self.vehicle_count4 = 0
        self.vehicle_count5 = 0
        self.vehicle_count6 = 0
        self.max_unseen_frames = 3

    def renew_csv(self):
        self.data_manager = CSVDataManager()

    @staticmethod
    def get_vector(a, b):
        """Calculate vector (distance, angle in degrees) from point a to point b.
        Angle ranges from -180 to 180 degrees.
        Vector with angle 0 points straight down on the image.
        Values increase in clockwise direction.
        """
        dx = float(b[0] - a[0])
        dy = float(b[1] - a[1])

        distance = math.sqrt(dx**2 + dy**2)

        if dy > 0:
            angle = math.degrees(math.atan(-dx/dy))
        elif dy == 0:
            if dx < 0:
                angle = 90.0
            elif dx > 0:
                angle = -90.0
            else:
                angle = 0.0
        else:
            if dx < 0:
                angle = 180 - math.degrees(math.atan(dx/dy))
            elif dx > 0:
                angle = -180 - math.degrees(math.atan(dx/dy))
            else:
                angle = 180.0        

        return distance, angle 


    @staticmethod
    def is_valid_vector(a):
        distance, angle = a
        #threshold_distance = max(10.0, -0.008 * angle**2 + 0.4 * angle + 25.0)
        #return (distance <= threshold_distance)
        return distance <= 45

    def update_vehicle(self, vehicle, matches):
        # Find if any of the matches fits this vehicle
        for i, match in enumerate(matches):
            centroid = match
            #vector = self.get_vector(vehicle.positions[-1], centroid)
            vector = self.get_vector(vehicle.positions[-1], (centroid.x, centroid.y))
            if self.is_valid_vector(vector):
                vehicle.add_position((centroid.x, centroid.y))
                return i

        # No matches fit...        
        vehicle.frames_since_seen += 1

        return None


    def update_count(self, matches, last_count, output_image = None, normal_image = None):

        # First update all the existing vehicles
        for vehicle in self.vehicles:
            i = self.update_vehicle(vehicle, matches)
            if i is not None:
                del matches[i]

        # Add new vehicles based on the remaining matches
        for match in matches:
            centroid = match
            new_vehicle = Vehicle(self.next_vehicle_id, centroid)
            self.next_vehicle_id += 1
            self.vehicles.append(new_vehicle)

        # Count any uncounted vehicles that are past the divider
        for vehicle in self.vehicles:
            #vehicle from top to down
            #counter line
            if not vehicle.counted1 and len(vehicle.positions) > 1:
                line_y_last = (vehicle.positions[-1][0]-self.divider2a_x)/(self.divider2b_x-self.divider2a_x)*(self.divider2b_y - self.divider2a_y)+self.divider2a_y
                line_y_last2 = (vehicle.positions[-2][0]-self.divider2a_x)/(self.divider2b_x-self.divider2a_x)*(self.divider2b_y - self.divider2a_y)+self.divider2a_y
                #through the line
                vehicle.counted1 = (vehicle.positions[-1][1] > line_y_last and vehicle.positions[-2][1] < line_y_last2)
               
            #if not vehicle.counted1 and len(vehicle.positions) > 1:
                #cek counter line 2
                if not vehicle.counted1:
                   line_y_last = (vehicle.positions[-1][0]-self.divider3a_x)/(self.divider3b_x-self.divider3a_x)*(self.divider3b_y - self.divider3a_y)+self.divider3a_y
                   line_y_last2 = (vehicle.positions[-2][0]-self.divider3a_x)/(self.divider3b_x-self.divider3a_x)*(self.divider3b_y - self.divider3a_y)+self.divider3a_y
                   vehicle.counted1 = (vehicle.positions[-1][1] > line_y_last and vehicle.positions[-2][1] < line_y_last2)

                #cek counter line 3
                if not vehicle.counted1:
                   line_y_last = (vehicle.positions[-1][0]-self.divider4a_x)/(self.divider4b_x-self.divider4a_x)*(self.divider4b_y - self.divider4a_y)+self.divider4a_y
                   line_y_last2 = (vehicle.positions[-2][0]-self.divider4a_x)/(self.divider4b_x-self.divider4a_x)*(self.divider4b_y - self.divider4a_y)+self.divider4a_y
                   vehicle.counted1 = vehicle.positions[-1][1] > line_y_last and vehicle.positions[-2][1] < line_y_last2
                      
                #already counted
                if vehicle.counted1:
                   self.vehicle_count1 += 1
                   self.save_to_csv(vehicle, last_count)

            #capture line
            if vehicle.counted1 and len(vehicle.positions) > 1 and (vehicle.positions[-1][0] > self.divider1a_x and vehicle.positions[-1][0] < self.divider1b_x) and vehicle.positions[-1][1] > self.divider1a_y > vehicle.positions[0][1]:
                #save vehicle picture
                now = get_server_time()
                name = str(vehicle.id)+"_H"+str(now.hour)+"M"+str(now.minute)
                
                #frame will be captured
                img_capture = output_image
                if normal_image is not None:
                   img_capture = normal_image
                vehicle.save_picture(name,100,100,img_capture)

            #if not vehicle.counted2 and len(vehicle.positions) > 1 and (vehicle.positions[-1][0] > self.divider2a_x > vehicle.positions[-2][0]) and self.divider2a_y > vehicle.positions[-1][1] > self.divider2b_y:
            #    self.vehicle_count2 += 1
            #    vehicle.counted2 = True
            #if not vehicle.counted3 and len(vehicle.positions) > 1 and (vehicle.positions[-1][0] > self.divider3a_x > vehicle.positions[-2][0]) and self.divider3a_y > vehicle.positions[-1][1] > self.divider3b_y:
            #    self.vehicle_count3 += 1
            #    vehicle.counted3 = True
            #if not vehicle.counted4 and len(vehicle.positions) > 1 and (vehicle.positions[-1][0] < self.divider4a_x < vehicle.positions[-2][0]) and self.divider4a_y > vehicle.positions[-1][1] > self.divider4b_y:
            #    self.vehicle_count4 += 1
            #    vehicle.counted4 = True
            #if not vehicle.counted5 and len(vehicle.positions) > 1 and (vehicle.positions[-1][0] < self.divider5a_x < vehicle.positions[-2][0]) and self.divider5a_y > vehicle.positions[-1][1] > self.divider5b_y:
            #    self.vehicle_count5 += 1
            #    vehicle.counted5 = True
            #if not vehicle.counted6 and len(vehicle.positions) > 1 and (vehicle.positions[-1][0] < self.divider6a_x < vehicle.positions[-2][0]) and self.divider6a_y > vehicle.positions[-1][1] > self.divider6b_y:
            #    self.vehicle_count6 += 1
            #    vehicle.counted6 = True
        # Optionally draw the vehicles on an image
        if output_image is not None:
            for vehicle in self.vehicles:
                vehicle.draw(output_image)
                #add to draw rect
                vehicle.draw_rect(100, 100, output_image)

            #cv2.putText(output_image, ("%02d" % self.vehicle_count1), (42, 10)
            #    , cv2.FONT_HERSHEY_PLAIN, 0.7, (127, 255, 255), 1)
            #cv2.putText(output_image, ("%02d" % self.vehicle_count2), (142, 10)
            #    , cv2.FONT_HERSHEY_PLAIN, 0.7, (127, 255, 255), 1)
            #cv2.putText(output_image, ("%02d" % self.vehicle_count3), (242, 10)
            #    , cv2.FONT_HERSHEY_PLAIN, 0.7, (127, 255, 255), 1)
            #cv2.putText(output_image, ("%02d" % self.vehicle_count4), (342, 10)
            #    , cv2.FONT_HERSHEY_PLAIN, 0.7, (127, 255, 255), 1)
            #cv2.putText(output_image, ("%02d" % self.vehicle_count5), (442, 10)
            #    , cv2.FONT_HERSHEY_PLAIN, 0.7, (127, 255, 255), 1)
            #cv2.putText(output_image, ("%02d" % self.vehicle_count6), (542, 10)
            #    , cv2.FONT_HERSHEY_PLAIN, 0.7, (127, 255, 255), 1)
            #cv2.putText(output_image, ("%02d" % ((self.vehicle_count + self.vehicle_count2) / 2)), (242, 10)
            #    , cv2.FONT_HERSHEY_PLAIN, 0.7, (127, 255, 255), 1)
        # Remove vehicles that have not been seen long enough
        removed = [ v.id for v in self.vehicles
            if v.frames_since_seen >= self.max_unseen_frames ]
        self.vehicles[:] = [ v for v in self.vehicles
            if not v.frames_since_seen >= self.max_unseen_frames ]
        for id in removed:
            break

    def save_to_csv(self, vehicle, last_count):
        #save to csv data
        vehicle.timestamp = get_current_timestamp_str('%Y-%m-%d %H:%M:%S %Z')
        vehicle.order = last_count+1
        self.data_manager.add_row(vehicle)
        self.jsonData.counting(vehicle.type)

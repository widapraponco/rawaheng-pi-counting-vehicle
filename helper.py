import cv2
import numpy as np

class Centroid():
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
#=======================================================================

class Helper():

    @staticmethod
    def get_centroid(x, y, w, h) :
        x1 = int(w/2)
        y1 = int(h/2)

        cx = x1 + x
        cy = y1 + y

        centroid = Centroid(cx, cy, w, h)

        return centroid

    @staticmethod
    def combined_nearby_centroid(centroid_pool):
        centroid_combined = []
        for (i, centroid) in enumerate(centroid_pool):
            flag = 0
            for entry in centroid_combined:
               if centroid in entry:
                   flag = 1
                   break
            if flag == 0:
               centroid_combined.append([centroid])
            for j in range(i, len(centroid_pool)):
               if abs(centroid.x - centroid_pool[j].x) < 100 and abs(centroid.y - centroid_pool[j].y) < 40:    
                   for entry in centroid_combined:
                       if centroid in entry and centroid_pool[j] not in entry:
                           entry.append(centroid_pool[j])
        return centroid_combined

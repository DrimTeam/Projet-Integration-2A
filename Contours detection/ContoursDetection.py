#!/usr/bin/env python
import cv2, sys
import numpy as np
import math

class ContoursDetection:
    def __init__(self):
        self.camera_port = 1
        self.cam = cv2.VideoCapture(self.camera_port)
        self.zoneDePassagePolygone = None
        self.prisonPolygone = None
        self.yellow = (0,150,255)
        self.black = (0,0,0)

    def seuilbas(x):
        pass # Fait rien 20% commentaire valide
    def seuilHaut(x):
        pass # Ne pas oublier UML pour ces fonctions
    def houghLines(x):
        pass
    def houghCircleParam1(x):
        pass
    def houghCircleParam2(x):
        pass

    # Assigner la zone de passage et la prison
    def assignZonePassageOrJail(self, principalsZones, img):

        if len(principalsZones) == 2:
            zone1 = principalsZones[0]
            zone2 = principalsZones[1]
            areaZone1 = abs(zone1[3][0][0] - zone1[0][0][0]) * abs(zone1[3][0][1] - zone1[2][0][1])
            areaZone2 = abs(zone2[3][0][0] - zone2[0][0][0]) * abs(zone2[3][0][1] - zone2[2][0][1])

            if areaZone1 > areaZone2:
                self.zoneDePassagePolygone = zone1
                print("Zone de passage"+str(areaZone1))
                self.prisonPolygone =zone2
                print("Zone de prison"+str(areaZone2))
                self.drawJailAndZonePassage(self.prisonPolygone, self.zoneDePassagePolygone, img)
            else:
                self.prisonPolygone = zone1
                print("Zone de prison"+str(areaZone1))
                self.zoneDePassagePolygone = zone2
                print("Zone de passage"+str(areaZone2))
                self.drawJailAndZonePassage(self.prisonPolygone, self.zoneDePassagePolygone, img)
        else :
            pass
            #raise Exception('Erreur il y a plus de deux zones principales')

    # Dessine la zone de passage et la prison
    def drawJailAndZonePassage(self, jailPolygon, zonePassage, img):
        cv2.drawContours(img, [zonePassage], -1, (255, 0, 0), 3)
        cv2.drawContours(img, [jailPolygon], -1, (0, 0, 255), 3)

    # Definit si la balle est en prison
    def isBallInJail(self,x,y):
        if not(self.prisonPolygone is None):
            if x > self.prisonPolygone[0][0][0] and x < self.prisonPolygone[2][0][0] and y > self.prisonPolygone[0][0][1] and y < self.prisonPolygone[2][0][1]:
                print("Une balle est en prison")
                return True
            else :
                return False
        return False

    #detection des cercles
    def detectCircle(self,grayImg, img):
        #########
        # Traitement HoughCircles
        ########
        # detect circles in the image
        circles = cv2.HoughCircles(grayImg, cv2.cv.CV_HOUGH_GRADIENT, 1, 20,
                      param1 = cv2.getTrackbarPos('HoughCircleParam1', 'Gray'),
                      param2= cv2.getTrackbarPos('HoughCircleParam2', 'Gray'),
                      minRadius=10,
                      maxRadius=30)

        print circles
        if not(circles is None):
            if len(circles) > 0:
                circles = np.uint16(np.around(circles))
                for i in circles[0,:]:
                    if self.isBallInJail(i[0], i[1]):
                        cv2.circle(img,(i[0],i[1]),2,self.black,3)
                        cv2.circle(img,(i[0],i[1]),i[2],self.black,2)
                    if self.isBallInZoneDePassage(i[0], i[1]):
                        cv2.circle(img,(i[0],i[1]),2,self.yellow,3)
                        cv2.circle(img,(i[0],i[1]),i[2],self.yellow,2)

    #detection des contours
    def detectContours(self,edges, img):

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
        closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

        (cnts, _) = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        total = 0
        rectangles = []
        principalsZones = []

        # loop over the contours
        for c in cnts:
            # approximate the contour
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            # if the approximated contour has four points, then assume that the
            # contour is a book -- a book is a rectangle and thus has four vertices
            if len(approx) == 4 :
                total += 1
                rectangles += [approx]

            # On vide le tableau de zone principales
            principalsZones = []

            # On boucle sur les polygones
            for rect in rectangles:

                # on recupere la largeur du rectangle
                rectWide = abs(rect[3][0][0] - rect[0][0][0])
                if rectWide > 100:
                    # dessiner le polygone
                    largeur = rectWide
                    longueur = abs(rect[3][0][1] - rect[2][0][1])
                    areaIntern = longueur*largeur
                    principalsZones.append(rect)

        print("|-----------------|"+str(len(principalsZones))+" zone detectees |-------------------|")
        self.assignZonePassageOrJail(principalsZones, img)

    # Definit si la balle est dans la zone de passage
    def isBallInZoneDePassage(self,x,y):
        if not(self.zoneDePassagePolygone is None):
            if x > self.zoneDePassagePolygone[0][0][0] and x < self.zoneDePassagePolygone[2][0][0] and y > self.zoneDePassagePolygone[0][0][1] and y < self.zoneDePassagePolygone[2][0][1]:
                print('Une balle est dans la zone de passage')
                return True
            return False
        return False

    def launchVision(self):
        cv2.namedWindow('Gray')
        cv2.resizeWindow('Gray',400,400)
        cv2.createTrackbar('seuilBas', 'Gray', 151, 400, self.seuilbas)
        cv2.createTrackbar('seuilHaut', 'Gray', 61, 400, self.seuilHaut)
        cv2.createTrackbar('HoughLines', 'Gray', 212, 400, self.houghLines)
        cv2.createTrackbar('HoughCircleParam1', 'Gray', 15, 200, self.houghCircleParam1)
        cv2.createTrackbar('HoughCircleParam2', 'Gray', 30, 200, self.houghCircleParam2)

        while (self.cam.isOpened()):
                ########
                # Traitement des polygones
                ########
                ret, img = self.cam.read()
                #img = cv2.imread('plateau.png')
                gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (3,3), 1)
                edges = cv2.Canny(gray, cv2.getTrackbarPos('seuilBas', 'Gray'), cv2.getTrackbarPos('seuilHaut', 'Gray'), apertureSize = 3)

                self.detectContours(edges, img)
                self.detectCircle(gray, img)

                # Show the picture
                #cv2.imshow('detected circles',cimg)
                # show the output image
                #cv2.imshow('circles', img)
                dst = cv2.flip(img,0)
                cv2.imshow('test',dst)
                #cv2.imshow('Gray2', gray)
                cv2.imshow('edges', edges)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        cam.release()
        # Close the windows

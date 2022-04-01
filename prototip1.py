# -*- coding: utf-8 -*-
"""
Created on Fri Jun 25 19:59:58 2021

@author: MAHMUT KARAASLAN
"""

from pymavlink import mavutil
from PIL import Image, ImageDraw
import math
import pygame
from dronekit import connect
import pandas as pd
import time
import serial.tools.list_ports

pygame.init()



class Dial:

   def __init__(self, image, frameImage, x=0, y=0, w=0, h=0):
       
       self.x = x 
       self.y = y
       self.image = image
       self.frameImage = frameImage
       self.dial = pygame.Surface(self.frameImage.get_rect()[2:4])
       self.dial.fill((0,0,0))
       if(w==0):
          w = self.frameImage.get_rect()[2]
       if(h==0):
          h = self.frameImage.get_rect()[3]
       self.w = w
       self.h = h
       self.pos = self.dial.get_rect()
       self.pos = self.pos.move(x, y)


   def rotate(self, image, angle):
      
       tmpImage = pygame.transform.rotozoom(image, angle,1)
       imageCentreX = tmpImage.get_rect()[0] + tmpImage.get_rect()[2]/2
       imageCentreY = tmpImage.get_rect()[1] + tmpImage.get_rect()[3]/2

       targetWidth = tmpImage.get_rect()[2]
       targetHeight = tmpImage.get_rect()[3]

       imageOut = pygame.Surface((targetWidth, targetHeight))
       imageOut.fill((0,0,0))
       imageOut.set_colorkey((0,0,0))
       imageOut.blit(tmpImage,(0,0), pygame.Rect( imageCentreX-targetWidth/2,imageCentreY-targetHeight/2, targetWidth, targetHeight ) )
       return imageOut

   def clip(self, image, x=0, y=0, w=0, h=0, oX=0, oY=0):

       if(w==0):
           w = image.get_rect()[2]
       if(h==0):
           h = image.get_rect()[3]
       needleW = w + 2*math.sqrt(oX*oX)
       needleH = h + 2*math.sqrt(oY*oY)
       imageOut = pygame.Surface((needleW, needleH))
       imageOut.fill((0,0,0))
       imageOut.set_colorkey((0,0,0))
       imageOut.blit(image, (needleW/2-w/2+oX, needleH/2-h/2+oY), pygame.Rect(x,y,w,h))
       return imageOut

   def overlay(self, image, x, y, r=0):

       x -= (image.get_rect()[2] - self.dial.get_rect()[2])/2
       y -= (image.get_rect()[3] - self.dial.get_rect()[3])/2
       image.set_colorkey((0,0,0))
       self.dial.blit(image, (x,y))
       




class Horizon(Dial):

   def __init__(self, x=0, y=0, w=0, h=0):

       self.image = pygame.image.load('resources/horizon_ball.svg')     
       self.frameImage = pygame.image.load('resources/horizon_circle.svg')
       self.maquetteImage = pygame.image.load('resources/horizon_mechanics.png')
       self.new_image= pygame.image.load("resources/horizon_back.svg").convert()
       self.circle=pygame.image.load("resources/fi_circle.svg")
       Dial.__init__(self, self.image, self.frameImage, x, y, w, h)
   def update(self, screen, angleX, angleY):

       angleX %= 360
       angleY %= 360
       if (angleX > 180):
           angleX -= 360 
       if (angleY > 90)and(angleY < 270):
           angleY = 180 - angleY 
       elif (angleY > 270):
           angleY -= 360
       tmpImage = self.clip(self.image,100, (100-angleY), 200, 200)
       tmpImage = self.rotate(tmpImage, angleX)
       newimage = self.rotate(self.new_image, angleX)
       tmp2=self.rotate(self.frameImage , angleX)
       
       self.overlay(newimage, 0,0)
       self.overlay(tmpImage, 0, 0,0) 
       
            
       self.overlay(tmp2, 0,0)
       
       self.overlay(self.maquetteImage, 0,0)
       self.overlay(self.circle, 0,0)
       
       self.dial.set_colorkey((0,0,0))
       screen.blit( pygame.transform.scale(self.dial,(self.w,self.h)), self.pos )

class navigason(Dial):
    
    def __init__(self, x=0, y=0, w=0, h=0):
        self.image = pygame.image.load('resources/heading_yaw.svg')
        self.frameImage = pygame.image.load('resources/fi_circle.svg')
        self.maquetteImage = pygame.image.load('resources/heading_mechanics.svg')
        self.drone=pygame.image.load("resources/dronesb.png")
        Dial.__init__(self, self.image, self.frameImage, x, y, w, h) 
    def update(self, screen, angleX):
        angleX %= 360
        if (angleX > 180):
            angleX -= 360         
        tmpImage = self.rotate(self.image, angleX) 
        dron = self.rotate(self.drone, -angleX) 
        
        
            
        self.overlay(tmpImage, 0, 0)
        self.overlay(self.maquetteImage, 0,0)
        # self.overlay(self.circle, 0,0)
        self.overlay(self.frameImage, 0,0) 
        self.dial.set_colorkey((0,0,0))
        screen.blit( pygame.transform.scale(self.dial,(self.w,self.h)), self.pos )
        return dron
                
class Generic(Dial):

   def __init__(self, x=0, y=0, w=0, h=0):
       self.circle=pygame.image.load("resources/fi_circle.svg")
       self.image = pygame.image.load('resources/fi_needle.svg')
       self.frameImage = pygame.image.load('resources/speed_mechanics.png').convert()
       Dial.__init__(self, self.image, self.frameImage, x, y, w, h)
   def update(self, screen, angleX, image2=0,iconLayer=0):     
       angleX=angleX-90
       ang2 = angleX/10
     
       tmpImage = self.clip(self.image, 0, 0, 0, 0, 0, 0)
       
       tmpImage = self.rotate(tmpImage, angleX)

       
       self.overlay(self.frameImage, 0,0)
              
       if image2:
           tmpImage2 = self.clip(self.image2, 0, 0, 0, 0, 0, 0)
           tmpImage2 = self.rotate(tmpImage2, ang2)
           self.overlay(tmpImage2, 0,0)


       self.overlay(tmpImage, 0, 0)
       self.overlay(self.circle, 0,0)
       self.dial.set_colorkey((0,0,0))
       screen.blit( pygame.transform.scale(self.dial,(self.w,self.h)), self.pos )

class altimeter(Generic):
 
    def __init__(self, x=0, y=0, w=0, h=0):        
        Generic.__init__(self, x, y, w, h)
        self.frameImage = pygame.image.load('resources/altitude_pressure.png')
        self.image2 = pygame.image.load('resources/fi_needle_small.svg')
        self.iconLayer= pygame.image.load('resources/altitude_pressure.png')
    def update(self, screen, angleX):               
        Generic.update(self, screen, angleX,self.image2,self.iconLayer)
  


class Battery(Generic):

   def __init__(self, x=0, y=0, w=0, h=0):

       Generic.__init__(self, x, y, w, h)
       self.frameImage = pygame.image.load('resources/ledgend.png').convert()
   def text_object(self,text,color,size):
        if size=="small":
            textsur=smallfront.render(text,True,color)        
            return textsur,textsur.get_rect()
    
   def update(self, screen, angleX):

       
       text=smallfront.render("Batarya: "+ str(angleX)+"v",True,(255,0,0))
       screen.blit(text,[self.x+(self.w/3),self.y+self.w-5])
       angleX=angleX*10       
       Generic.update(self, screen,angleX+120)



class signal:
 
    def __init__(self,x,y,w,h):
        self.x=x
        self.y=y
        self.w=w
        self.h=h
   
       
    def update(self,screen,rssi):
        if rssi>20:
            pygame.draw.rect(screen,(0,255,0),(self.x,self.y,self.w,self.h))
        else:
            pygame.draw.rect(screen,(255,0,0),(self.x,self.y,self.w,self.h))
        if rssi>40:
            pygame.draw.rect(screen,(0,255,0),(self.x+(self.w+5),self.y-(self.h)/2,self.w,self.h*(1.5)))
            # print("girdi")
        if rssi>60:
            pygame.draw.rect(screen,(0,255,0),(self.x+2*(self.w+5),self.y-(self.h),self.w,self.h*(2)))
        if rssi>80:
            pygame.draw.rect(screen,(0,255,0),(self.x+3*(self.w+5),self.y-(self.h*1.5),self.w,self.h*(2.5)))
       
        text=smallfront.render("Sinyal: "+ str(100)+"%",True,(255,0,0))
        screen.blit(text,[self.x-20,self.y+self.w+10])        


class GPSVis(object):

    def __init__(self, map_path, points):

        self.points = points
        self.map_path = map_path
        self.result_image = Image.open(self.map_path, 'r')
        self.img_points = []
        self.draw = ImageDraw.Draw(self.result_image)

    def update(self,screen,gps_data,surface, color, width=2):
        
        raw_str = pygame.image.tostring(surface, 'RGBA', False)
        im1 = Image.frombytes('RGBA', surface.get_size(), raw_str)
       
        for d in gps_data:
            x1, y1 = self.scale_to_img(d, (self.result_image.size[0], self.result_image.size[1]))
            self.img_points.append((x1, y1))
        
        self.draw.line(self.img_points, fill=color, width=width)
        self.back_im =self.result_image.copy()
        x,y=im1.size
        self.back_im.paste( im1,(x1-int(x/2), y1-int(y/2)),mask=im1)
        
        mode = self.back_im.mode
        size = self.back_im.size
        data = self.back_im.tobytes()       
        py_image = pygame.image.fromstring(data, size, mode)
        screen.blit(py_image,(750,275),pygame.Rect(300,0,1150,720))        
    def scale_to_img(self, lat_lon, h_w):

        old = (self.points[2], self.points[0])
        new = (0, h_w[1])
        y = ((lat_lon[0] - old[0]) * (new[1] - new[0]) / (old[1] - old[0])) + new[0]
        old = (self.points[1], self.points[3])
        new = (0, h_w[0])
        x = ((lat_lon[1] - old[0]) * (new[1] - new[0]) / (old[1] - old[0])) + new[0]

        return int(x), h_w[1] - int(y)        

class DropDown():

    def __init__(self, color_menu, color_option, x, y, w, h, font, main, options):
        self.color_menu = color_menu
        self.color_option = color_option
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.main = main
        self.options = options
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1

    def draw(self, surf):
        pygame.draw.rect(surf, self.color_menu[self.menu_active], self.rect, 0)
        msg = self.font.render(self.main, 1, (0, 0, 0))
        surf.blit(msg, msg.get_rect(center = self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.options):
                rect = self.rect.copy()
                rect.y += (i+1) * self.rect.height
                pygame.draw.rect(surf, self.color_option[1 if i == self.active_option else 0], rect, 0)
                msg = self.font.render(text, 1, (0, 0, 0))
                surf.blit(msg, msg.get_rect(center = rect.center))

    def update(self, event_list):
        mpos = pygame.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)
        
        self.active_option = -1
        for i in range(len(self.options)):
            rect = self.rect.copy()
            rect.y += (i+1) * self.rect.height
            if rect.collidepoint(mpos):
                self.active_option = i
                break

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                elif self.draw_menu and self.active_option >= 0:
                    self.draw_menu = False
                    return self.active_option
        return -1          



                   


class Button:


    def __init__(self,scree, text,  pos, font, bg="black", feedback=""):
        self.x, self.y = pos
        self.font = pygame.font.SysFont("Arial", font)
        if feedback == "":
            self.feedback = "text"
        else:
            self.feedback = feedback
        self.change_text(text, bg)

    def change_text(self, text, bg="black"):

        self.text = self.font.render(text, 1, pygame.Color("White"))
        self.size = self.text.get_size()
        self.surface = pygame.Surface(self.size)
        self.surface.fill(bg)
        self.surface.blit(self.text, (0, 0))
        self.rect = pygame.Rect(self.x, self.y, self.size[0], self.size[1])

    def show(self):
        screen.blit(button1.surface, (self.x, self.y))

    def click(self, event):
        x, y = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                if self.rect.collidepoint(x, y):
                    self.change_text(self.feedback, bg="green")
                    return 1




connected = []
ports = serial.tools.list_ports.comports()
for port, desc, hwid in sorted(ports):
        connected.append(port)
        print("{}: {} [{}]".format(port, desc, hwid))
       
smallfront=pygame.font.SysFont('Times New Roman',20)


screen = pygame.display.set_mode((1900,1000))
screen.fill((50,50,50))

COLOR_INACTIVE = (0, 255, 0)
COLOR_ACTIVE = (0, 255, 255)
COLOR_LIST_INACTIVE = (0, 255, 0)
COLOR_LIST_ACTIVE = (0, 255, 255)

list1 = DropDown(
    [COLOR_INACTIVE, COLOR_ACTIVE],
    [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
    1660, 0, 70, 30, 
    pygame.font.SysFont(None, 15), 
    "Select com", connected)

list2 = DropDown(
    [COLOR_INACTIVE, COLOR_ACTIVE],
    [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
    1735, 0, 70, 30, 
    pygame.font.SysFont(None, 15), 
    "baud", ['1200','2400','4800','9600','19200','38400','57600','111100','115200','500000','625000','921600','1500000'])          
button1 = Button(screen,
"Bağlan",
    (1820, 0),
    font=25,
    bg="Red",
    feedback="Bağlandı")
display_w=1050
display_h=500

size=[display_w,display_h]




             
                
clock=pygame.time.Clock()

   

reklam1=pygame.image.load("resources/1234.png")
reklam2=pygame.image.load("resources/AYBARSV2.png")

programIcon = pygame.image.load('resources/AYBARSv2.png')
pygame.display.set_icon(programIcon)
pygame.display.set_caption('Raclab Aybars')

throttle = Generic(20,0,250,250)
horizon = Horizon(270,0,250,250)
alt=altimeter(520,0,250,250)
nav= navigason(270,250,250,250)
RXbattery = Battery(1400,0,250,250)
sig=signal(1800, 200, 15, 15)
vis = GPSVis(map_path='resources/stad.png',  # Path to map downloaded from the OSM.
              points=(38.01515,32.51049, 38.01340,32.51403))

crashed=False
x_change=0
y_change=0
speed_cursor=0
alti=0
navi=0
batery=0
hearbest=0
i=0
a=100


gps_data=[]

while not crashed:
    event_list = pygame.event.get()
    for event in event_list:
        con=button1.click(event)
            
        if event.type == pygame.QUIT:
            crashed=True      
    if event.type == pygame.KEYDOWN:
        speed_cursor+=2
        if event.key == pygame.K_LEFT:
            x_change += -1
        if event.key == pygame.K_RIGHT:
            x_change += 1
        if event.key == pygame.K_UP:
            y_change+=1
        if event.key == pygame.K_DOWN:
            y_change-=1

    try:
        x_change=vehicle.attitude.roll*55
        y_change=vehicle.attitude.pitch*150
        speed_cursor=vehicle.groundspeed
        alti=vehicle.location.global_relative_frame.alt              
        navi=math.degrees(vehicle.attitude.yaw)
        batery=vehicle.battery.voltage
        hearbest=vehicle.last_heartbeat

        
    except:
        print("Hata")
        
    finally:


        screen.fill((50,50,50))
    
        
        surface=nav.update(screen,navi)
        if len(gps_data) >=1:
            i=i+1
            gps_data.append((vehicle.location.global_frame.lat,vehicle.location.global_frame.lon))        
            vis.update(screen,gps_data[i:i+1],surface, color=(0, 0, 255), width=3)    
    
        if con==1:
            baudr=list2.main
            vehicle = connect(list1.main, wait_ready=True, baud=int(baudr))
            # vehicle = connect('127.0.0.1:14552', wait_ready=True)            
            gps_data.append((vehicle.location.global_frame.lat,vehicle.location.global_frame.lon))
        
        surface=nav.update(screen,navi)


        button1.show()
        sig.update(screen, a)
              
        horizon.update(screen, (x_change),y_change)    
        throttle.update(screen,-(speed_cursor)*2)
        alt.update(screen, -(alti/2))
        RXbattery.update(screen,batery)
        
        
        selected_option = list1.update(event_list)
        if selected_option >= 0:
            list1.main = list1.options[selected_option]
            
        selected_option2 = list2.update(event_list)
        if selected_option2 >= 0:
            list2.main = list2.options[selected_option2]                
        # print(list1.main)        
        # print(list2.main)        
        list1.draw(screen)
        list2.draw(screen)

        screen.blit(reklam2,(0,725))
        screen.blit(reklam1,(300,725))
        pygame.display.update()
        clock.tick(144)    
 
pygame.quit()

vehicle.close()

  


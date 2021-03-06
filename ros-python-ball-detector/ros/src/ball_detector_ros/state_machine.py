#!/usr/bin/env python

#-*- encoding: utf-8 -*-
import sys
import rospy
from std_msgs.msg import String
from sensor_msgs.msg import Image
import cv2
import ball_detector_ros.process_image as bdr_pi

class publisher():
    ''' Publisher class: Handle the publishing of output '''
    def __init__(self):
        self.pub = rospy.Publisher('~position', String, queue_size=100,
                                        latch=False)
        self.pub2 = rospy.Publisher('~event_out', String, queue_size=100,
                                        latch=False)
    def publish_position(self,msg):
        self.pub.publish(msg)

    def publish_event_out(self,msg):
        self.pub2.publish(msg)

class subcriber():
    state = "INIT"
    input_img = Image()
    def __init__(self):
        self.event_in = rospy.Subscriber('~event_in', String, self.event_in_cb)
        # ~input_image, /usb_cam/image_raw
        self.input_image = rospy.Subscriber('~input_image', Image,
                                                self.input_image_cb)

    #Callback function
    def event_in_cb(self, msg):
        if msg.data == 'e_start':   #Switch to start state
            rospy.loginfo("Starting")
            self.state = "PROC"
        elif msg.data == 'e_stop':  #Switch to stop state
            rospy.loginfo("Stoping")
            self.state = "INIT"
        elif msg.data == 'e_trigger':
            rospy.loginfo("Triggering")
            self.state = "TRIG"
        else:
            rospy.loginfo("Waiting")

    def set_state(self, state):
        self.state = state

    def input_image_cb(self, img):  #Get image message from sensor
        self.input_img = img

def run():
    ''' State machine, publisher and subcriber '''
    #Initiate node
    rospy.init_node('ball_detector_node', anonymous=False)
    rospy.loginfo("ball_detector_node is now running")

    #Create publisher, subcriber
    pub = publisher()
    sub = subcriber()

    #Processing loop
    r = rospy.Rate(10)
    while not rospy.is_shutdown():
        if (sub.state == "PROC" or sub.state == "TRIG") and sub.input_img.data: #If in processing state and an image is received
            position_output = bdr_pi.process_image(sub.input_img)               #Run the image processor.
            pub.publish_position(position_output)                               #Publish the String output
            if sub.state == "TRIG":
                sub.set_state("INIT")
            if position_output == "left" or position_output == "right":
                pub.publish_event_out("e_found_ball")
            elif position_output == None:
                pub.publish_event_out("e_no_ball")
        elif sub.state == "INIT":                                       #If in initiate state
            rospy.loginfo("Waiting for e_start")
        r.sleep()





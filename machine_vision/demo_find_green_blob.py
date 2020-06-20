import gc, uos, sys
import machine
from board import board_info
from fpioa_manager import fm
from pye_mp import pye
from Maix import FPIOA, GPIO


import sensor
import image
import lcd
import time

def init():
    global led_w
    global led_r
    global led_g
    global led_b
    global orange_ball_threshold


    #LED INIT
    fm.register(board_info.LED_W, fm.fpioa.GPIO3)
    led_w = GPIO(GPIO.GPIO3, GPIO.OUT)
    led_w.value(1) #RGBW LEDs are Active Low

    fm.register(board_info.LED_R, fm.fpioa.GPIO4)
    led_r = GPIO(GPIO.GPIO4, GPIO.OUT)
    led_r.value(1) #RGBW LEDs are Active Low

    fm.register(board_info.LED_G, fm.fpioa.GPIO5)
    led_g = GPIO(GPIO.GPIO5, GPIO.OUT)
    led_g.value(1) #RGBW LEDs are Active Low

    fm.register(board_info.LED_B, fm.fpioa.GPIO6)
    led_b = GPIO(GPIO.GPIO6, GPIO.OUT)
    led_b.value(1) #RGBW LEDs are Active Low

    #LCD INIT
    lcd.init(freq=15000000)

    #CAMERA INIT
    camera_frequency = 24000000

    #camera_rgb_gain = (10, 5, 0)

    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)

    ## SPECIFIC CAMERA PROPERTY SETTINGS
    #camera_gain = 0
    #camera_contrast = 0
    #camera_brightness = 0
    #camera_saturation = 0
    #if not sensor.set_contrast(camera_contrast):
    #    raise IOError
    #
    #if not sensor.set_brightness(camera_brightness):
    #    raise IOError
    #
    #if not sensor.set_saturation(camera_saturation):
    #    raise IOError


    #sensor.set_auto_gain(0, -1)
    #sensor.set_auto_whitebal(0, camera_rgb_gain)

    sensor.run(1)
    sensor.skip_frames(time = 2000)

    #Processing params
    orange_ball_threshold   = (43, 100, -17, 127, 8, 127)


def numbersClose(a,b,tolerance):
    return (a >= b-tolerance and a <= b+tolerance)

def distance_to_camera(knownWidth, focalLength, perWidth):
    # compute and return the distance from the maker to the camera
    return (knownWidth * focalLength) / perWidth

# MAIN CODE
blob_min_region_len = 20
blob_min_region_len = 20
pingpong_radius = 39.18 #mm
camera_focal = (175*95)/pingpong_radius

init()

# CODE CRASHES DUE TO FRAME BUFFER

while True:
    img = sensor.snapshot()
    ## BLOB
    blobs = img.find_blobs([orange_ball_threshold],pixels_threshold=100,merge=True)
    print(len(blobs))
    if blobs:
        for b in blobs:
            blob_center_rgb = img.get_pixel(b[5], b[6])
            blob_roi = b[0:4]
            # Looks for in bounds size
            if blob_roi[2] > blob_min_region_len and  blob_roi[3] > blob_min_region_len:
                ## RGB with R much greater than B
                if not numbersClose(blob_center_rgb[0],blob_center_rgb[2],50):
                    # Looks for more square regions
                    if numbersClose(b[2],b[3],5):
                        print(blob_roi)
                        # Distance to blob
                        print(distance_to_camera(pingpong_radius,camera_focal,blob_roi[2]))
                        tmp=img.draw_rectangle(b[0:4],color=(0,255,0))
                        tmp=img.draw_cross(b[5], b[6],color=(0,255,0))

                    else:
                        continue
                        #tmp=img.draw_rectangle(b[0:4],color=(255,0,0))
                        #tmp=img.draw_cross(b[5], b[6],color=(255,0,0))
            else:
                continue
                #tmp=img.draw_rectangle(b[0:4],color=(0,0,255))
                #tmp=img.draw_cross(b[5], b[6],color=(0,0,255))
    else:
        print("No blob")

    lcd.display(img)




sensor.shutdown(1)
lcd.deinit()




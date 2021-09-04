#!/bin/bash

raspivid -p 0,0,3840,2160 -t 0 -awb off -awbg 3.0,1.5  -ex fixedfps -ISO 100 -md 1 -fps 30 -ag 1.0 -dg 1 -pf high -lev 4.2 -e -drc off -ss 33000 -w 1920 -h 1080 #-l -o tcp://0.0.0.0:8989 -b 10000000

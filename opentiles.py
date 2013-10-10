#!/usr/bin/env python                                                                                                                                                                                                              
# cb-opentiles:
# A script for tiling window management with Openbox.
# Written for CrunchBang Linux <http://crunchbang.org/>
# by Tyler Pollard
# ----------------------------------------------------------------------
# License:
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#                    Version 2, October 2013
#
# Copyright (C) 2013 Tyler Pollard <https://github.com/projektile>
#
# Everyone is permitted to copy and distribute verbatim or modified
# copies of this license document, and changing it is allowed as long
# as the name is changed.
#
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
#  0. You just DO WHAT THE FUCK YOU WANT TO.
# ----------------------------------------------------------------------

from subprocess import Popen, PIPE, STDOUT
import sys, os, subprocess, re, datetime

p = Popen(['xdotool','getdisplaygeometry'], stdout=PIPE, stderr=STDOUT)
Dimensions = p.communicate()
Dimensions = Dimensions[0].replace('\n', '')
Dimensions = Dimensions.split(' ')
res_width = int(Dimensions[0])
res_height = int(Dimensions[1])
windows = {}

def print_usage():
	print "cb-opentiles: usage:"
	print "  --help		show this message and exit"
	print "  --up       attempt to tile windows evenly"
	print "  --down     attempt to tile more windows on the right"
	print ""
	exit()

def window_id():
	p = Popen(['xdotool', 'getactivewindow'], stdout=PIPE)
	ID = p.communicate()
	ID = int(ID[0])
	p = Popen(['xdotool', 'getwindowpid', str(ID)], stdout=PIPE)
	PID = p.communicate()
	PID = int(PID[0])
	return str(ID)+'-'+str(PID)

def get_desktop_number():
	p = Popen(['wmctrl', '-d'], stdout=PIPE, stderr=STDOUT)
	desktop = p.communicate()
	desktop = str(desktop)
	i = 0
	while i < len(desktop):
		if desktop[i] == "*":
			return desktop[i-3]
			break
		else:
			i = i + 1

def get_windows(desktop_num):
	p = Popen(['wmctrl', '-l', '-G'], stdout=PIPE, stderr=STDOUT)
	windows = p.communicate()
	windows = windows[0].replace('\n', ' \n')
	windows = windows.split('\n')
	tile_list = []
	for i in windows:
		if i[11:13] == " " + desktop_num:
#			print i
			tile_list.append(i[:10])
	return tile_list

def tile_windows(windows, col):
	n = 0
	for i in windows:
		os.system("xdotool windowactivate " + i)
		frac = int(res_height/len(windows))
		if col == 1:
			x = str(int(15))
		elif col == 2:
			x = str(int(res_width/2+15))#*.90
		y = str(int(n*frac+30))
		width = str(int(res_width/2*.98))#*.858
		height = str(frac - 15)
		os.system("wmctrl -r :ACTIVE: -e 1,"+x+","+y+","+width+","+height)
		n = n + 1

def factor_inactive(dimension):
	p = Popen(['wmctrl', '-l', '-G'], stdout=PIPE, stderr=STDOUT)
	windows = p.communicate()
	windows = windows[0].replace('\n', ' \n')
	windows = windows.split('\n')
	inactive_list = []
	for i in windows:
		if i[11:13] == "-1":
			print i
			inactive_list.append(i[24:32])
	for i in inactive_list:
		x = int(i[:4].replace(' ',''))
		y = int(i[4:8].replace(' ',''))
		if dimension == "x":
			if x < y:
				return x
			else:
				continue
		if dimension =="y":
			if x > y:
				return y
			else:
				continue
	return 0

def main():
	if "--up" in sys.argv:
		L_windows = num_windows[:(len(num_windows)/2)]
		R_windows = num_windows[(len(num_windows)/2):]
		tile_windows(L_windows, 1)
		tile_windows(R_windows, 2)
	elif "--down" in sys.argv:
		L_windows = num_windows[:(len(num_windows)/2)+1]
		R_windows = num_windows[(len(num_windows)/2)+1:]
		tile_windows(L_windows, 1)
		tile_windows(R_windows, 2)
	else:
		print_usage()

x_object = int(factor_inactive("x"))
y_object = int(factor_inactive("y")*1.5)
res_width = res_width - x_object
res_height = res_height - y_object

active_desktop = get_desktop_number()
num_windows = get_windows(active_desktop)
ID = window_id()

main()

os.system("xdotool windowactivate " + ID)

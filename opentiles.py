#!/usr/bin/python
# opentiles:
# A script to allow for tiling window management with Openbox.
# by projektile
# ----------------------------------------------------------------------
# License:
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#                    Version 2, October 2013
#
# Copyright (C) 2013 projektile <https://github.com/projektile>
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
import sys, os, subprocess, re

history = '/tmp/cb-opentiles-'+str(os.getuid())

p = Popen(['xdotool','getdisplaygeometry'], stdout=PIPE, stderr=STDOUT)
Dimensions = p.communicate()
Dimensions = Dimensions[0].replace('\n', '')
Dimensions = Dimensions.split(' ')
res_width = int(Dimensions[0])
res_height = int(Dimensions[1])

active_desktop = 0
windows_arr = []
method = 0
columns = 0
ID = 0

useless_gap = 18
x_object = 0
y_object = 0

if os.path.exists(history) == False:
	f = open(history,'w')
	f.close()

def print_usage():
	print "opentiles: usage:"
	print "  --help     show this message and exit"
	print "  --left     tile two window columns"
	print "  --right    tile three window columns"
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

def windows_store(windows):
	os.system('rm /tmp/cb-opentiles-'+str(os.getuid()))
	for i in windows:
		s = i + ' \n'
		f = open(history,'a')
		f.write(s)
	f.close()

def history_lookup():
	f = open(history,'r')
	i = 0
	for line in f:
		z = str(line[:10])
		if z in windows_arr:
			i = i + 1
		else:
			return False
	f.close()
	if i == len(windows_arr):
		return True
	else:
		return False

def windows_assign():
	f = open(history,'r')
	loaded_list = []
	for line in f:
		z = str(line[:10])
		loaded_list.append(z)
	f.close()
	return loaded_list

def get_desktop_number():
	p = Popen(['wmctrl', '-d'], stdout=PIPE, stderr=STDOUT)
	desktop = p.communicate()
	desktop = str(desktop)
	i = 0
	while i < len(desktop):
		if desktop[i] == "*":
			return desktop[i-3]
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
			tile_list.append(i[:10])
	return tile_list

def panel_farside(dimension):
	p = Popen(['wmctrl', '-l', '-G'], stdout=PIPE, stderr=STDOUT)
	windows = p.communicate()
	windows = windows[0].replace('\n', ' \n')
	windows = windows.split('\n')
	panel_list = []
	for i in windows:
		if i[11:13] == "-1":
			panel_list.append(i[14:32])
	for i in panel_list:
		x = int(i[10:14].replace(' ',''))
		y = int(i[14:18].replace(' ',''))
		x_coord = int(i[:4].replace(' ',''))
		y_coord = int(i[4:8].replace(' ',''))
		if dimension == "x":
			if x < y:
				if x_coord > res_width/2:
					return True
				else:
					return False
		if dimension =="y":
			if x > y:
				if y_coord > res_height/2:
					return True
				else:
					return False
	return True

def tile_windows(windows, col):
	n = 0
	for i in windows:
		h_frac = int((res_width/columns)*(col-1)+(useless_gap*.5))
		v_frac = int((n*(res_height/len(windows)))+(useless_gap*.5))
		if panel_farside("x")==False:
			h_frac += x_object
		if panel_farside("y")==False:
			v_frac += y_object
		width = str(int((res_width/columns)-useless_gap))
		height = str(res_height/len(windows)-useless_gap)
		dim_string = str(h_frac)+","+str(v_frac)+","+width+","+height
		os.system("xdotool windowactivate "+i)
		os.system("wmctrl -r :ACTIVE: -e 1,"+dim_string)
		n = n + 1

def factor_inactive(dimension):
	p = Popen(['wmctrl', '-l', '-G'], stdout=PIPE, stderr=STDOUT)
	windows = p.communicate()
	windows = windows[0].replace('\n', ' \n')
	windows = windows.split('\n')
	inactive_list = []
	for i in windows:
		if i[11:13] == "-1":
			inactive_list.append(i[24:32])
	for i in inactive_list:
		x = int(i[:4].replace(' ',''))
		y = int(i[4:8].replace(' ',''))
		if dimension == "x":
			if x < y:
				return x
		if dimension =="y":
			if x > y:
				return y
	return 0

def get_columns(num):
	columns = len(windows_arr)/num
	if len(windows_arr)%num > 0:
		columns = columns + 1
	return columns

def rotate(list, x):
	return list[-x:] + list[:-x]

def tile_method():
	if "--left" in sys.argv:
		if len(windows_arr) == 2:
			return 1
		else:
			return 2
	elif "--right" in sys.argv:
		return 3
	else:
		print_usage()

def main():
	global x_object
	global y_object
	global res_width
	global res_height
	global active_desktop
	global windows_arr
	global method
	global columns
	global ID
	x_object = int(factor_inactive("x"))
	y_object = int(factor_inactive("y"))
	res_width = res_width - x_object
	res_height = res_height - y_object
	active_desktop = get_desktop_number()
	windows_arr = get_windows(active_desktop)
	method = int(tile_method())
	columns = get_columns(method)
	ID = window_id()
	if history_lookup():
		windows_arr = windows_assign()
		windows_arr = rotate(windows_arr, 1)
	window_sets = []*columns
	x = 0
	while x < columns:
		window_sets.append(windows_arr[x*method:((x+1)*method)])
		tile_windows(window_sets[x], x+1)
		x+=1
	windows_store(windows_arr)
	os.system("xdotool windowactivate " + ID)

main()

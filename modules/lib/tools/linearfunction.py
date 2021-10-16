# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Linear function tools """

def get_linear(x1, y1, x2, y2, offset=1000):
	""" Return a and b for ax+b of two points x1,y1 and x2,y2 """
	# If two points distincts
	if x1 != x2:
		# Compute the slope of line
		a = (((y1 - y2)) *offset) // (x1 - x2)
		b = y1*offset - a*x1
	else:
		a = 0
		b = 0
	return a,b,offset

def get_fx(x, linear):
	""" Return the y value of function x """
	a,b,offset = linear
	y = ((a * x) + b)//offset
	return y

def get_fy(y, linear):
	""" Return the x value of function y """
	a,b,offset = linear
	x = ((y*offset) -b)//a
	return x

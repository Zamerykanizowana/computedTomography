import sys
import numpy as np
import math
from skimage import io, draw, img_as_ubyte

def line_to_y_x_list(l):
    return list(zip(l[0], l[1]))

#alfa - angular shift (PL przesuniecie katowe 'szyny' z detektorami)
#gamma - angular span (PL rozpietosc katowa)
#n - number of detector/emitter
def count_pt_for_one_scan(start_angle, gamma, n, r):
	gamma_pi = gamma * np.pi / 180
	gamma_i = gamma/(n-1)
	result_tab = []
	start = start_angle - gamma/2
	result_tab.append(start)
	while n > 1:
		start += gamma_1
		result_tab.append(start)
		print(start)
		n-=1
	start = start_angle - gamma/2

#count_pt_for_one_scan(180, 15, 6)

img_path = sys.argv[1]

img = img_as_ubyte(io.imread(img_path, as_gray=True))

print("---------------------------------------------")
width = len(img[0])
height = len(img)
print("Width of " + img_path + " is: " + str(width))
print("Height of " + img_path + " is: " + str(height))
print("Middle element is " + str(int(width/2)))
sum_det = 0
for ele in img:
	sum_det += ele[int(width/2)]

print("Sum of pixels value for basic detector: " + str(sum_det))
avg=int(sum_det/height)
print("Avg value of pixel for basic detector: " + str(avg))
print("---------------------------------------------")
#coordinates
tmp_tab = draw.line_nd((height/2,-width/2),(-(height-2)/2,(width-2)/2),endpoint=True)

value_tab = line_to_y_x_list(tmp_tab)

tab_len = len(tmp_tab[0])
print(f'tab_len is equal {tab_len}')
#print(tmp_tab)
#in value_tab are tables with coordinates points to count values in the curve
print(value_tab)

#print("---------------------------------------------")

#for ele in value_tab:
#	img[ele[0],ele[1]] = 255
#
#io.imsave(img_path + ".diag.jpg",img)
#print("Img " + img_path + ".diag.jpg" + " saved.")

print("---------------------------------------------")
#width = len(img[0])
#height = len(img)

r = (math.sqrt(width**2+height**2))/2
print("Radius is equil " + str(r))

#point on circle
pt_start = []
pt_stop = []
#angle; 180 == np.pi; 90 == np.pi/2 ect
alfa = np.pi
x_1 = int(r * math.cos(alfa))
y_1 = int(r * math.sin(alfa))
pt_start.append(x_1)
pt_start.append(y_1)
x_2 = int(r * math.cos(alfa-np.pi))
y_2 = int(r * math.sin(alfa-np.pi))
pt_stop.append(x_2)
pt_stop.append(y_2)
print(f'pt_start is equal {pt_start}')
print(f'pt_stop is equal {pt_stop}')

print(type(pt_start))
print(type(pt_stop))

#coordinates
tmp_tab = draw.line_nd(tuple(pt_start),tuple(pt_stop),endpoint=True)

value_tab = line_to_y_x_list(tmp_tab)
tab_len = len(tmp_tab[0])
print(f'tab_len is equal {tab_len}')
#print(tmp_tab)
#in value_tab are tables with coordinates points to count values in the curve
print(value_tab)



print("---------------------------------------------")

print("for example to discuse function to take points")
#coordinates
height = 8
wight = 6
tmp_tab = draw.line_nd((3,-4),(-5,2),endpoint=True)

value_tab = []
tab_len = len(tmp_tab[0])
print(f'tab_len is equal {tab_len}')
#print(tmp_tab)
i = 0
while i < tab_len:
	tmp = []
	tmp.append(tmp_tab[0][i])
	tmp.append(tmp_tab[1][i])
	value_tab.append(tmp)
	i+=1
#value_tab contains tables with coordinates points to count values in the curve
print(value_tab)

#print("---------------------------------------------")

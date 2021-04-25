import sys
import numpy as np
import math
from skimage import io, draw, img_as_ubyte

def line_to_y_x_list(l):
    return list(zip(l[0], l[1]))

def edp_trace(cpfos_output, h, w):
    def __range(v):
        return range(-v//2, v//2)

    y_range = __range(h)
    x_range = __range(w)

    filtered_lines = []

    # Iterating over emitter-detector pairs
    # obtained from the cpfos function.
    # Below is an example of cpfos_output:
    #
    #    y, x
    #     n1      n2      n3
    # [[(3,-4), (4,-3), (5,-2)],
    #  [(-5,2), (-4,3), (-3,4)]]
    #
    # n_x (where x is the number of detectors)
    # are emitter-detector pairs.
    # The upper tuple contains the coordinates
    # of the starting point and the lower tuple
    # contains the coordinates of the end point.

    for ped in zip(cpfos_output[0], cpfos_output[1]):
        line_to_filter = line_to_y_x_list(
                draw.line_nd(ped[0], ped[1], endpoint=True)
        )

        for yx_pair in list(line_to_filter):
            if not yx_pair[0] in y_range or not yx_pair[1] in x_range:
                line_to_filter.remove(yx_pair)

        filtered_lines.append(line_to_filter)

    return filtered_lines

#alfa - angular shift (PL przesuniecie katowe 'szyny' z detektorami)
#gamma - angular span (PL rozpietosc katowa)
#n - number of detector/emitter
def count_pt_for_one_scan(start_angle, gamma, n, r):
	gamma_pi = gamma * np.pi / 180
	gamma_i = gamma/(n-1)
	result_tab_det = []
	result_tab_em = []
	start = start_angle - gamma/2
	stop = start_angle - 180 - gamma/2

	#alfa = np.pi
	#x_1 = int(r * math.cos(alfa))
	#y_1 = int(r * math.sin(alfa))
	#pt_start.append(x_1)
	#pt_start.append(y_1)
	#x_2 = int(r * math.cos(alfa-np.pi))
	#y_2 = int(r * math.sin(alfa-np.pi))
	#pt_stop.append(x_2)
	#pt_stop.append(y_2)

	while n > 0:
		y_1 = int(r * math.sin(math.radians(start)))
		x_1 = int(r * math.cos(math.radians(start)))
		tmp_tab_start = y_1,x_1
		y_2 = int(r * math.sin(math.radians(stop)))
		x_2 = int(r * math.cos(math.radians(stop)))
		tmp_tab_stop = y_2,x_2
		result_tab_det.append(tmp_tab_start)
		result_tab_em.append(tmp_tab_stop)
		start += gamma_i
		stop += gamma_i
		n-=1
	#print(f'result_tab_det is equal {result_tab_det}')
	#print(f'result_tab_em is equal {result_tab_em}')
	return [result_tab_det, result_tab_em]

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

result = count_pt_for_one_scan(180, 8, 5, r)
print(f'result is equal {result}')

#point on circle
pt_start = []
pt_stop = []
#angle; 180 == np.pi; 90 == np.pi/2 ect
alfa = np.pi
x_1 = int(r * math.cos(alfa))
y_1 = int(r * math.sin(alfa))
pt_start.append(y_1)
pt_start.append(x_1)
x_2 = int(r * math.cos(alfa-np.pi))
y_2 = int(r * math.sin(alfa-np.pi))
pt_stop.append(y_2)
pt_stop.append(x_2)
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
width = 6
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

dummy_cpfos = [[(3,-4)],[(-5,2)]]

dummy_edp_trace = edp_trace(dummy_cpfos, height, width)
print(dummy_edp_trace)

#print("---------------------------------------------")

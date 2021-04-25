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


#switch frame of reference (19,-10) --> (0,0)
def signed_trace_to_unsigned_trace(pts_tab_tup, h, w):
	result = []
	for ele in pts_tab_tup:
		y_tmp = abs(ele[0]-(h//2-1))
		x_tmp = ele[1]+w//2
		tmp_tup = y_tmp,x_tmp
		result.append(tmp_tup)
	return result


img_path = sys.argv[1]

img = img_as_ubyte(io.imread(img_path, as_gray=True))

print("---------------------------------------------")
width = len(img[0])
height = len(img)
print("Width of " + img_path + " is: " + str(width))
print("Height of " + img_path + " is: " + str(height))

#io.imsave(img_path + ".diag.jpg",img)
#print("Img " + img_path + ".diag.jpg" + " saved.")
r = (math.sqrt(width**2+height**2))/2
print("radius is equal " + str(r))

result = count_pt_for_one_scan(180, 30, 3, r)
#tmp result for test function signed_trace_to_unsigned_trace
#result = [[(19, -10)],[(-20,9)]]
print(f'result is equal : {result}')

solved = edp_trace(result, height, width)
print(f'solved is equal : {solved}')

print(50*"-")
done = []
for ele in solved:
	done.append(signed_trace_to_unsigned_trace(ele, height, width))
i = 0
while i < len(done):
	print(f'done[{i}] is equal : {done[i]}')
	print(50*"-")
	i += 1

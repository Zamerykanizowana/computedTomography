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
    result_tab_det = []
    result_tab_em = []
    if n > 1:
        gamma_pi = gamma * np.pi / 180
        gamma_i = gamma/(n-1)
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
    else:
        y_1 = int(r * math.sin(math.radians(start_angle)))
        x_1 = int(r * math.cos(math.radians(start_angle)))
        tmp_tab_start = y_1,x_1
        y_2 = int(r * math.sin(math.radians(start_angle-180)))
        x_2 = int(r * math.cos(math.radians(start_angle-180)))
        tmp_tab_stop = y_2,x_2
        result_tab_det.append(tmp_tab_start)
        result_tab_em.append(tmp_tab_stop)
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

#input:
#img:  image to take values from
#pts_tab_tup: tables of tuplas with points counted to take value for detector
def value_for_det_em(img, pts_tab_tup):
    sum = 0
    for ele in pts_tab_tup:
        sum += img[ele[0],ele[1]]
    return sum

class SingleScan:
    def __init__(self, start_angle, span, n, w, h):
        self.radius = (math.sqrt(w**2+h**2))/2
        self.points = count_pt_for_one_scan(
                start_angle, span, n, self.radius
                )
        self.traces = edp_trace(self.points, h, w)
        self.traces_unsigned = [
                signed_trace_to_unsigned_trace(e, h, w) for e in self.traces
                ]

class CTScan:
    def __init__(self, image_path):
        self.input_image = img_as_ubyte(io.imread(image_path, as_gray=True))
        self.width = len(self.input_image[0])
        self.height = len(self.input_image)
        self.radius = (math.sqrt(self.width**2+self.height**2))/2
        self.detector_length = self.height if self.height > self.width else self.width

img_path = sys.argv[1]

print(50*'-')
c = CTScan(img_path)
print(f"Width of {img_path} is: {c.width}")
print(f"Height of {img_path} is: {c.height}")
print(f'Detector lenght is equal: {c.detector_length}')

#io.imsave(img_path + ".diag.jpg",img)
#print("Img " + img_path + ".diag.jpg" + " saved.")
print(f"Radius is equal to {c.radius}")

first_scan = SingleScan(180, 30, 3, c.width, c.height)

print(f'Emitter points: {first_scan.points}')
print(f'Emitter traces: {first_scan.traces}')

print(50*"-")

for trace_num, trace in enumerate(first_scan.traces_unsigned):
    print(f'[{trace_num}]: {trace}')
    print(50*"-")


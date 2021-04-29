import sys
import numpy as np
import math
from skimage import io, draw, img_as_ubyte
from concurrent.futures import ProcessPoolExecutor
from PIL import Image as image

img_path = sys.argv[1]

def sinogram(tab):
    height = len(tab)
    width = len(tab[0].values)

    print(f'{width}x{height}')

    s_arr = np.zeros((height, width), dtype=np.uint8)

    for scan_index, scan in enumerate(tab):
        s_arr[scan_index] = scan.values

    io.imsave(img_path + ".diag.jpg", s_arr)


def line_to_y_x_list(l):
    return list(zip(l[0], l[1]))

def __edp_trace(ped, y_range, x_range):
    line_to_filter = line_to_y_x_list(
            draw.line_nd(ped[0], ped[1], endpoint=True)
            )

    for yx_pair in list(line_to_filter):
        if not yx_pair[0] in y_range or not yx_pair[1] in x_range:
            line_to_filter.remove(yx_pair)

    return line_to_filter

def edp_trace(cpfos_output, h, w):
    def __range(v, c):
        for _ in range(c):
            yield range(-v//2, v//2)

    y_range = __range(h, len(cpfos_output[0]))
    x_range = __range(w, len(cpfos_output[0]))

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

    with ProcessPoolExecutor() as e:
        for r in e.map(__edp_trace, zip(cpfos_output[0], cpfos_output[1]), y_range, x_range):
            filtered_lines.append(r)

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
def value_for_trace(img, pts_tab_tup, det_len):
    sum = 0
    for ele in pts_tab_tup:
        sum += img[ele[0],ele[1]] 
    return sum//det_len

class SingleScan:
    def __init__(self, img, start_angle, span, n, w, h, det_len):
        self.image = img
        self.radius = (math.sqrt(w**2+h**2))/2
        print('calculating points')
        self.points = count_pt_for_one_scan(
                start_angle, span, n, self.radius
                )
        print('calculating traces')
        self.traces = edp_trace(self.points, h, w)
        print('calculating unsigned traces')
        self.traces_unsigned = [
                signed_trace_to_unsigned_trace(e, h, w) for e in self.traces
                ]
        print('calculating values for traces')
        self.values = [value_for_trace(self.image, t, det_len) for t in self.traces_unsigned]

class CTScan:
    def __init__(self, image_path, span, angle_increment, n):
        self.input_image = img_as_ubyte(io.imread(image_path, as_gray=True))
        self.width = len(self.input_image[0])
        self.height = len(self.input_image)
        self.radius = (math.sqrt(self.width**2+self.height**2))/2
        self.detector_length = self.height if self.height > self.width else self.width
        self.span = span
        self.angle_increment = angle_increment
        self.n = n
        self.scans = []

        self.__scan()

    def __scan(self):
        deg = 180

        while deg > 0:
            print(deg)
            self.scans.append(
                    SingleScan(self.input_image, deg, self.span, 
                        self.n, self.width, self.height, self.detector_length
                        )
                    )
            deg -= self.angle_increment


print(50*'-')
c = CTScan(img_path, 90, 2, 180)
print(f"Width of {img_path} is: {c.width}")
print(f"Height of {img_path} is: {c.height}")
print(f'Detector lenght is equal: {c.detector_length}')
print(f"Radius is equal to {c.radius}")

#io.imsave(img_path + ".diag.jpg",c.input_image)

#print(c.scans)
#print(len(c.scans))

for scan in c.scans:
    print(scan.values)


sinogram(c.scans)

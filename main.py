import sys
import numpy as np
import math
from helpers.edp_trace import edp_trace
from skimage import io, draw, img_as_ubyte

img_path = sys.argv[1]

def sinogram_progress(tab, height):
    tmp_height = len(tab)
    width = len(tab[0].values)
    progress = len(tab)*100/height
    print(f'sinogram progress: {progress}%')
    s_arr = np.zeros((height, width), dtype=np.uint8)
    for scan_index, scan in enumerate(tab):
        s_arr[scan_index] = scan.values
    io.imsave(f'/tmp/sinogram_progress_{progress}_percent.jpg', s_arr, check_contrast=False)

def sinogram(tab):
    height = len(tab)
    width = len(tab[0].values)

    print(f'sinogram width x height: {width}x{height}')

    s_arr = np.zeros((height, width), dtype=np.uint8)

    for scan_index, scan in enumerate(tab):
        s_arr[scan_index] = scan.values

    io.imsave(img_path + ".diag.jpg", s_arr)

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
    #print(50*'-')
    #print('Before reversed result_tab_em looks like: ')
    #print(f'result_tab_em is equal {result_tab_em}')
    result_tab_em = reversed(result_tab_em)
    #print('After reversed result_tab_em looks like: ')
    #print(f'result_tab_em is equal {result_tab_em}')
    #print(50*'-')
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
        self.start_angle = start_angle
        print('calculating points')
        self.points = count_pt_for_one_scan(
                start_angle, span, n, self.radius
                )
        print('calculating traces')
        self.traces = edp_trace(self.points, h, w, parallel=True)
        print('calculating unsigned traces')
        self.traces_unsigned = [
                signed_trace_to_unsigned_trace(e, h, w) for e in self.traces
                ]
        print('calculating values for traces')
        self.values = [value_for_trace(self.image, t, det_len) for t in self.traces_unsigned]

    def generate_debug_image(self):
        dbg_img = np.copy(self.image)

        for trace in self.traces_unsigned:
            for trace_y, trace_x in trace:
                dbg_img[trace_y, trace_x] = 255

        io.imsave(f'/tmp/dbg-{self.start_angle}.jpg', dbg_img)

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
        print(f'singoram height is: {180//self.angle_increment}')
        while deg > 0:
            print(deg)
            self.scans.append(
                    SingleScan(self.input_image, deg, self.span,
                        self.n, self.width, self.height, self.detector_length
                        )
                    )
            deg -= self.angle_increment

            self.scans[-1].generate_debug_image()
            if len(self.scans)%10 == 0:
                sinogram_progress(self.scans,  180//self.angle_increment)


print(50*'-')
c = CTScan(img_path, 90, 2, 10)
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

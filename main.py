import sys, subprocess, math, os, click
import numpy as np
from helpers.edp_trace import edp_trace
from skimage import io, draw, img_as_ubyte


def sinogram_progress(tab, height):
    tmp_height = len(tab)
    width = len(tab[0].values)
    progress = int(len(tab)*100/height)
    print(f'sinogram progress: {progress}%')
    s_arr = np.zeros((height, width), dtype=np.uint8)
    for scan_index, scan in enumerate(tab):
        s_arr[scan_index] = scan.values
    io.imsave(f'/tmp/sinogram_progress_{progress}_percent.jpg', s_arr, check_contrast=False)

#def sinogram(tab):
#    height = len(tab)
#    width = len(tab[0].values)
#    print(f'sinogram width x height: {width}x{height}')
#    s_arr = np.zeros((height, width), dtype=np.uint8)
#    for scan_index, scan in enumerate(tab):
#        s_arr[scan_index] = scan.values
#    io.imsave(img_path + ".diag.jpg", s_arr)

#alfa - angular shift (PL przesuniecie katowe 'szyny' z detektorami)
#span - angular span (PL rozpietosc katowa)
#n - number of pairs detector-emitter
#t - type of detector-emitter - True: parallel, False: conical
def count_pt_for_one_scan(start_angle, span, n, r, t):
    def __one_point(angle):
        y = int(r * math.sin(math.radians(angle)))
        x = int(r * math.cos(math.radians(angle)))
        return y,x

    result_tab_det = []
    result_tab_em = []
    if n == 1:
        print('One detector')
        tmp_tab_start = __one_point(start_angle)
        tmp_tab_stop = __one_point(start_angle - 180)
        result_tab_det.append(tmp_tab_start)
        result_tab_em.append(tmp_tab_stop)
    else:
        span_i = span/(n-1)
        start = start_angle - span/2
        stop = start_angle - 180 - span/2
        if t:
            print(f'Parallel scan with {n} detectors')
            while n > 0:
                tmp_tab_start = __one_point(start)
                tmp_tab_stop = __one_point(stop)
                result_tab_det.append(tmp_tab_start)
                result_tab_em.append(tmp_tab_stop)
                start += span_i
                stop += span_i
                n-=1
        else:
            print(f'Conical scan with {n} detectors')
            tmp_tab_start = __one_point(start_angle)
            while n > 0:
                tmp_tab_stop = __one_point(stop)
                result_tab_det.append(tmp_tab_start)
                result_tab_em.append(tmp_tab_stop)
                stop += span_i
                n-=1
    result_tab_em = reversed(result_tab_em)
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
def value_for_trace(img, pts_tab_tup):
    sum = 0
    for ele in pts_tab_tup:
        sum += img[ele[0],ele[1]] 
    return sum//len(pts_tab_tup)

class SingleScan:
    def __init__(self, img, start_angle, span, n, w, h, t):
        #question for Adas: why all parameters are not self? 
#        print(50*'-')
        self.image = img
        self.radius = (math.sqrt(w**2+h**2))/2
        self.start_angle = start_angle
#        print('calculating points')
        self.points = count_pt_for_one_scan(
                start_angle, span, n, self.radius, t
                )
#        print('calculating traces')
        self.traces = edp_trace(self.points, h, w, parallel=True)
#        print('calculating unsigned traces')
        self.traces_unsigned = [
                signed_trace_to_unsigned_trace(e, h, w) for e in self.traces
                ]

#        #needed this stuff it remember myself how it works
#        print(20*'-')
#        for ele_idx, ele in enumerate(self.traces_unsigned):
#            print(f'value of {ele_idx} is {ele}')
#        print(20*'-')

        print('calculating values for traces')
        self.values = [value_for_trace(self.image, t) for t in self.traces_unsigned]

    def generate_debug_image(self, make_gif=True):
        dbg_img = np.copy(self.image)

        for trace in self.traces_unsigned:
            for trace_y, trace_x in trace:
                dbg_img[trace_y, trace_x] = 255

        io.imsave(f'/tmp/dbg-{self.start_angle}.jpg', dbg_img)

        if make_gif and self.start_angle == 10:
            c = subprocess.run("bash -c 'convert -resize 50% -delay 3 -loop 0 dbg-{2..360}.jpg dbg.gif'",
                    shell=True, capture_output=True, cwd='/tmp'
                    )


#t - type of scans (True - parallel, False - conical)
class CTScan:
    def __init__(self, image_path, span, angle_increment, n, t):
        self.input_image_path = image_path
        self.input_image = img_as_ubyte(io.imread(image_path, as_gray=True))
        self.width = len(self.input_image[0])
        self.height = len(self.input_image)
        self.radius = (math.sqrt(self.width**2+self.height**2))/2
        self.span = span
        self.angle_increment = angle_increment
        self.n = n
        self.t = t
        self.start_deg = 180 if t else 360
        self.scans = []
        self.sinogram_dim = (self.start_deg // angle_increment,n)
        print(self.sinogram_dim)
        self.sinogram = np.zeros(self.sinogram_dim, dtype=np.uint8)
        self.ct_result = np.zeros((self.height, self.width), dtype=np.uint8)
        io.imsave(self.input_image_path + ".ct_result.jpg", self.ct_result)

        self.__scan()

    def __scan(self):
        deg = self.start_deg

        while deg > 0:
            print(deg)
            self.scans.append(
                    SingleScan(self.input_image, deg, self.span,
                        self.n, self.width, self.height, self.t
                        )
                    )
            deg -= self.angle_increment

            self.scans[-1].generate_debug_image()

    def make_sinogram(self, save=True):
        for scan_index, scan in enumerate(self.scans):
            self.sinogram[scan_index] = scan.values

        print(self.sinogram)

        if save:
            io.imsave(self.input_image_path + ".diag.jpg", self.sinogram)

    def make_ct(self):
        print(20*'-' + ' start function make_ct ' + 20*'-')
        list = [0] * self.width
        list = [list] * self.height
        max_value = 0
        for idx, scan in enumerate(self.scans):
            for trace_idx, trace in enumerate(scan.traces_unsigned):
                for y, x in trace:
                    list[y][x] += scan.values[trace_idx]
                    tmp_value = list[y][x]
                    if tmp_value > max_value:
                        max_value = tmp_value
#                    if self.ct_result[y,x] > 255:
#                        self.ct_result[y,x] = 255
#        io.imsave(self.input_image_path + ".ct_result.jpg", self.ct_result, check_contrast=False)
        print(10*'-' + ' printed list ' + 10*'-')
        for ele in list:
            print(ele)
        i = 0
        j = 0
        while i < self.height:
            while j < self.width:
                list[i][j] = int(list[i][j]*255/max_value)
                j += 1
            i += 1

        print(10*'-' + ' printed list 0-255 ' + 10*'-')
        for ele in list:
            print(ele)
            
        i = 0
        while i < self.height:
            self.ct_result[i] = list[i]
            i += 1

        io.imsave(self.input_image_path + ".ct_result.jpg", self.ct_result, check_contrast=False)



@click.command()
@click.argument('img_path')
@click.option('--span', default=30)
@click.option('--increment', default=2)
@click.option('--n', default=180)
def main(img_path, span, increment, n):
    print(50*'-')
    
    c = CTScan(image_path=img_path, span=span, angle_increment=increment, n=n, t=True)

    print(f"Width of {img_path} is: {c.width}")
    print(f"Height of {img_path} is: {c.height}")
    print(f"Radius is equal to {c.radius}")

    c.make_sinogram()
    c.make_ct()

if __name__ == '__main__':
    main()

import sys, subprocess, math, os, click, logging
import numpy as np
from helpers.edp_trace import edp_trace
from skimage import io, draw, img_as_ubyte

LOGGER_NAME = 'ct_interactive'

l = logging.getLogger(LOGGER_NAME)

def sinogram_progress(tab, height):
    tmp_height = len(tab)
    width = len(tab[0].values)
    progress = int(len(tab)*100/height)
    l.info(f'sinogram progress: {progress}%')
    s_arr = np.zeros((height, width), dtype=np.uint8)
    for scan_index, scan in enumerate(tab):
        s_arr[scan_index] = scan.values
    io.imsave(f'/tmp/sinogram_progress_{progress}_percent.jpg', s_arr, check_contrast=False)

#def sinogram(tab):
#    height = len(tab)
#    width = len(tab[0].values)
#    l.info(f'sinogram width x height: {width}x{height}')
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
        l.info('One detector')
        tmp_tab_start = __one_point(start_angle)
        tmp_tab_stop = __one_point(start_angle - 180)
        result_tab_det.append(tmp_tab_start)
        result_tab_em.append(tmp_tab_stop)
    else:
        span_i = span/(n-1)
        start = start_angle - span/2
        stop = start_angle - 180 - span/2
        if t:
            l.info(f'Parallel scan with {n} detectors')
            while n > 0:
                tmp_tab_start = __one_point(start)
                tmp_tab_stop = __one_point(stop)
                result_tab_det.append(tmp_tab_start)
                result_tab_em.append(tmp_tab_stop)
                start += span_i
                stop += span_i
                n-=1
        else:
            l.info(f'Conical scan with {n} detectors')
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
    result = np.array(pts_tab_tup)

    result[:,0] = abs(result[:,0]-(h//2-1))
    result[:,1] = result[:,1]+w//2

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
        self.image = img
        self.radius = (math.sqrt(w**2+h**2))/2
        self.start_angle = start_angle
        self.points = count_pt_for_one_scan(
                start_angle, span, n, self.radius, t
                )

        l.info('calculating traces')
        self.traces = edp_trace(self.points, h, w, parallel=True)

        l.info('calculating unsigned traces')
        self.traces_unsigned = [
                signed_trace_to_unsigned_trace(e, h, w) for e in self.traces
                ]
        l.info('finished calculating signed and unsigned traces')

        l.info('calculating values for traces')
        self.values = [value_for_trace(self.image, t) for t in self.traces_unsigned]

    def generate_debug_image(self): 
        dbg_img = np.copy(self.image)

        for trace in self.traces_unsigned:
            for trace_y, trace_x in trace:
                dbg_img[trace_y, trace_x] = 255

        io.imsave(f'/tmp/dbg-{self.start_angle}.jpg', dbg_img)

#t - type of scans (True - parallel, False - conical)
class CTScan:
    def __init__(self, image_path, span, angle_increment, n, t, dbg_image=False):
        self.input_image_path = image_path
        self.input_image = img_as_ubyte(io.imread(image_path, as_gray=True))
        self.dbg_image = dbg_image
        self.width = len(self.input_image[0])
        self.height = len(self.input_image)
        self.radius = (math.sqrt(self.width**2+self.height**2))/2
        self.span = span
        self.angle_increment = angle_increment
        self.n = n
        self.t = t
        self.start_deg = 180 if t else 360
        self.degrees = self.__gen_degrees_lst()
        self.scans = []
        self.sinogram_dim = (len(self.degrees),n)
        l.info(self.sinogram_dim)
        self.sinogram = np.zeros(self.sinogram_dim, dtype=np.uint8)
        self.ct_result = np.zeros((self.height, self.width), dtype=np.uint8)
        io.imsave(self.input_image_path + ".ct_result.jpg", self.ct_result)

        self.__scan()

    def __gen_degrees_lst(self):
        deg = self.start_deg
        degrees = []

        while deg > 0:
            degrees.append(deg)
            deg -= self.angle_increment

        return degrees

    def __scan(self):
        for d in self.degrees:
            l.info(d)
            self.scans.append(
                    SingleScan(self.input_image, d, self.span,
                        self.n, self.width, self.height, self.t
                        )
                    )

            if self.dbg_image:
                self.scans[-1].generate_debug_image()
                if d == self.degrees[-1]:
                    l.info('Saving GIF...')
                    subprocess.run("bash -c 'convert -resize 50% -delay 3 -loop 0 dbg-{2..360}.jpg dbg.gif'",
                            shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd='/tmp'
                            )

    def make_sinogram(self, save=True):
        for scan_index, scan in enumerate(self.scans):
            self.sinogram[scan_index] = scan.values

        if save:
            io.imsave(self.input_image_path + ".diag.jpg", self.sinogram)

    def make_ct(self, save=True):
        tmp_list = np.zeros((self.height, self.width), dtype=np.uint)

        l.info('Start iteration')

        for idx, scan in enumerate(self.scans):
            l.info(f'Processing scan {idx}')
            for trace_idx, trace in enumerate(scan.traces_unsigned):
                # The call below reverses the 'column_stack' result.
                y_tr, x_tr = np.hsplit(trace, 2)
                tmp_list[y_tr, x_tr] += scan.values[trace_idx]

        l.info('Stop iteration')

        max_value = np.amax(tmp_list)

        l.info(f'Max value: {max_value}')

        normalize_func = np.vectorize(lambda e: int(e*255/max_value))

        tmp_list = normalize_func(tmp_list)

        self.ct_result = tmp_list.astype(np.uint8)

        if save:
            io.imsave(self.input_image_path + ".ct_result.jpg", self.ct_result, check_contrast=False)



@click.command()
@click.argument('img_path')
@click.option('--span', default=30)
@click.option('--increment', default=2)
@click.option('--n', default=180)
@click.option('--dbg-image', default=False)
def main(img_path, span, increment, n, dbg_image):
    logging.basicConfig(format="[%(asctime)s] %(levelname)-8s| %(lineno)s >> %(message)s")
    logging.getLogger(LOGGER_NAME).setLevel(logging.DEBUG)
    logging.getLogger('edp_trace').setLevel(logging.DEBUG)
    
    c = CTScan(
            image_path=img_path, 
            span=span, 
            angle_increment=increment, 
            n=n, 
            t=True,
            dbg_image=dbg_image
            )

    l.info(f"Width of {img_path} is: {c.width}")
    l.info(f"Height of {img_path} is: {c.height}")
    l.info(f"Radius is equal to {c.radius}")

    c.make_sinogram()
    c.make_ct()

if __name__ == '__main__':
    main()

import sys, subprocess, math, os, logging
import numpy as np
from .edp_trace import edp_trace
from .dicom import save_dicom as save_dicom_wrapper
from skimage import io, draw, img_as_ubyte

LOGGER_NAME = 'ct'

l = logging.getLogger(LOGGER_NAME)

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
            l.debug(f'Parallel scan with {n} detectors')
            while n > 0:
                tmp_tab_start = __one_point(start)
                tmp_tab_stop = __one_point(stop)
                result_tab_det.append(tmp_tab_start)
                result_tab_em.append(tmp_tab_stop)
                start += span_i
                stop += span_i
                n-=1
        else:
            l.debug(f'Conical scan with {n} detectors')
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

        l.debug('calculating traces')
        self.traces = edp_trace(self.points, h, w, parallel=True)

        l.debug('calculating unsigned traces')
        self.traces_unsigned = [
                signed_trace_to_unsigned_trace(e, h, w) for e in self.traces
                ]
        l.debug('finished calculating signed and unsigned traces')

        l.debug('calculating values for traces')
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
        self.scan_images = []
        self.sinogram_dim = (len(self.degrees),n)
        self.sinogram = np.zeros(self.sinogram_dim, dtype=np.uint8)
        self.ct_result = np.zeros((self.height, self.width), dtype=np.uint8)

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

    def make_sinogram(self, save=True):
        for scan_index, scan in enumerate(self.scans):
            self.sinogram[scan_index] = scan.values

        if save:
            io.imsave(self.input_image_path + ".diag.jpg", self.sinogram)

    def make_ct(self, save=True):
        tmp_list = np.zeros((self.height, self.width), dtype=np.uint)

        for idx, scan in enumerate(self.scans):
            l.info(f'Processing scan {idx}')
            curr_norm_list = np.zeros((self.height, self.width), dtype=np.uint)

            for trace_idx, trace in enumerate(scan.traces_unsigned):
                # The call below reverses the 'column_stack' result.
                y_tr, x_tr = np.hsplit(trace, 2)
                tmp_list[y_tr, x_tr] += scan.values[trace_idx]

            max_value = np.amax(tmp_list)

            if max_value > 0:
                curr_norm_list = np.floor(tmp_list*255/max_value)
            else:
                curr_norm_list = np.copy(tmp_list)

            self.scan_images.append(curr_norm_list.astype(np.uint8))

            if save:
                io.imsave(
                        self.input_image_path + f".{idx}.ct_result.jpg", 
                        curr_norm_list.astype(np.uint8), 
                        check_contrast=False
                        )

    def save_dicom(self, patient_name):
        output_file = self.input_image_path + ".dcm"

        save_dicom_wrapper(
                image_data=self.scan_images[-1].astype(np.uint8),
                output_file=output_file,
                patient_name=patient_name
                )

        return output_file

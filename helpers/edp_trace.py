from skimage import draw
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count

# The 'edp_trace' function works by
# iterating over emitter-detector pairs
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
#
# The '__edp_trace' function is used both
# by the parallel and seqential variant
# of the aforementioned function.
# It draws a line (trace) and filters it so that
# the values are within the provided x and y range.

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

def edp_trace_parallel(cpfos_output, h, w):
    def __range(v, c):
        for _ in range(c):
            yield range(-v//2, v//2)

    y_range = __range(h, len(cpfos_output[0]))
    x_range = __range(w, len(cpfos_output[0]))

    filtered_lines = []


    with ProcessPoolExecutor(max_workers=cpu_count()) as e:
        for r in e.map(__edp_trace, zip(cpfos_output[0], cpfos_output[1]), y_range, x_range):
            filtered_lines.append(r)

    return filtered_lines

def edp_trace_sequential(cpfos_output, h, w):
    def __range(v):
            return range(-v//2, v//2)

    y_range = __range(h)
    x_range = __range(w)

    filtered_lines = []

    for ped in zip(cpfos_output[0], cpfos_output[1]):
        filtered_lines.append(__edp_trace(ped, y_range, x_range)) 

    return filtered_lines

def edp_trace(*args, parallel=True):
    __f = edp_trace_parallel if parallel else edp_trace_sequential
    return __f(*args)

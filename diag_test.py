import sys
import numpy as np
from skimage import io, draw, img_as_ubyte

img_path = sys.argv[1]

img = img_as_ubyte(io.imread(img_path, as_gray=True))

width = len(img[0])
height = len(img)

img_empty = np.zeros((width, height), dtype=np.uint8)

#x1 = 0
#y1 = 0
#x2 = width
#y2 = height
#
#print(x1,y1,x2,y2)
#
#first_diag = draw.line(x1,y1,x2,y2)
#
#print(first_diag)
#
#x1 = 0
#y1 = height
#x2 = width
#y2 = 0
#
#print(x1,y1,x2,y2)
#
#second_diag = draw.line(x1,y1,x2,y2)
#
#img[first_diag[0], first_diag[1]] = 255
#img[second_diag[0], second_diag[1]] = 130


#[y, x] so [0,0] is left bottom corner and [0,max lenght] is right bottom corner

img[10, 10] = 255

io.imsave(img_path+'.diag.jpg', img)

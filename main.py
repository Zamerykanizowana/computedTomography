import sys
import numpy as np
from skimage import io, draw, img_as_ubyte

img_path = sys.argv[1]

img = img_as_ubyte(io.imread(img_path, as_gray=True))

print("---------------------------------------------")
width = len(img[0])
height = len(img)
print("Width of " + img_path + " is: " + str(width))
print("Middle element is " + str(int(width/2)))
sum_det = 0
for ele in img:
	sum_det += ele[int(width/2)]

print("Sum of pixels value for basic detector: " + str(sum_det))
avg=int(sum_det/height)
print("Avg value of pixel for basic detector: " + str(avg))
print("---------------------------------------------")
#possibly coordinates, couse I still don't know how it works :(
tmp_tab = draw.line_nd((0,0),((height-1),(width-1)),endpoint=True)

#print(foo[0][7])
#print(foo[1])
value_tab = []
tab_len = len(tmp_tab[0])
print("tab_len is equil: " + str(tab_len))
i = 0
while i < tab_len:
	tmp = []
	tmp.append(tmp_tab[0][i])
	tmp.append(tmp_tab[1][i])
	value_tab.append(tmp)
	#is in python i++ or just i+=1???
	i+=1
#in value_tab are tables with coordinates points to count values in the curve
print(value_tab)

print("---------------------------------------------")

for ele in value_tab:
	img[ele[0],ele[1]] = 255

io.imsave(img_path + ".diag.jpg",img)
print("Done?")
print("Yes!")

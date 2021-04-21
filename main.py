from skimage import io, img_as_ubyte

dot_path = "images/Kolo.jpg"
ct_path = "images/CT_ScoutView.jpg"

dot_img = img_as_ubyte(io.imread(dot_path, as_gray=True))
ct_img = img_as_ubyte(io.imread(ct_path, as_gray=True))

print("---------------------------------------------")
print("Width of " + dot_path + " is: " + str(len(dot_img[0])))
print("Middle element is " + str(int(len(dot_img[0])/2)))
sum_det = 0
for ele in dot_img:
	sum_det += ele[int(len(dot_img[0])/2)]

print("Sum of pixels value: " + str(sum_det))
avg=int(sum_det/len(dot_img))
print("Avg value of pixel in detector: " + str(avg))

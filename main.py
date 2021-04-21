from skimage import io, img_as_ubyte

dot_path = "images/Kropka.jpg"
ct_path = "images/CT_ScoutView.jpg"

dot_img = img_as_ubyte(io.imread(dot_path, as_gray=True))
ct_img = img_as_ubyte(io.imread(ct_path, as_gray=True))

print(dot_img[250])

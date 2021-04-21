from skimage import io
path = "image/Kropka.jpg"
img = io.imread(path, as_gray=False)
print("Image: " + path)
print(img[250])
print("The end")

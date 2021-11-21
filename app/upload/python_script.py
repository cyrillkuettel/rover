import io
from PIL import Image

full_path = "/home/cyrill/rover/app/upload/image"


# with open(full_path, "wb") as f:
 #   f.write(binaryData)
# img = Image.frombuffer('YUV', (320, 240), binaryData)
# img.save()


imageFileObj = open(full_path, "rb")
imageBinaryBytes = imageFileObj.read()
imageStream = io.BytesIO(imageBinaryBytes)
imageFile = Image.open(imageStream)

print("imageFile.size=%s" % imageFile.size)
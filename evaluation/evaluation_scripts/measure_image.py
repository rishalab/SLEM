import cv2
from PIL import Image

# Global Fallbacks
cv2_512 = cv2.imread('img_512.jpg')
cv2_2048 = cv2.imread('img_2048.jpg')
pil_512 = Image.open('img_512.jpg')
pil_2048 = Image.open('img_2048.jpg')

def cv2_resize_512(img=None): return cv2.resize(cv2_512, (256, 256))
def cv2_resize_2048(img=None): return cv2.resize(cv2_2048, (1024, 1024))
def pil_resize_512(img=None): return pil_512.copy().resize((256, 256))
def pil_resize_2048(img=None): return pil_2048.copy().resize((1024, 1024))
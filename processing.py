import numpy as np
import cv2
import matplotlib.pyplot as plt
from PIL import Image, ImageOps
from scipy import ndimage, misc, signal
import PIL
from skimage.transform import probabilistic_hough_line
from skimage.transform import hough_line, hough_line_peaks
from skimage.feature import canny
from skimage import data
from skimage import feature

def LevelSlicing(im,Lgl,Hgl):
    m = Image.fromarray(im)
    m = m.point(lambda i: 255 if i>=Lgl and i<=Hgl else 0)
    return m

def histogram_cdf(im):
    counts, bins = np.histogram(im, range(257))
    print(counts[40])
    cdf = np.cumsum (counts)
    cdf_ppt = np.floor((cdf/cdf[-1])*100)
    print(bins[:-1] )
    plt.bar(bins[:-1] , counts, width=1, edgecolor='none')
    plt.show()
    plt.plot (bins[:-1], cdf_ppt,color="blue")
    plt.xlim([-0.5, 255.5])
    plt.show()
    return cdf_ppt

def blurImage(im):
    # im = Image.fromarray(im)
    # im = ndimage.median_filter(im, size=5)
    im = cv2.blur(im,(5,5))
    # im = signal.wiener(im)
    # im=cv2.equalizeHist(im)
    return im

def fourierfilter(im):
    n=10
    m=120
    f = np.fft.fft2(im)  
    ft = np.fft.fftshift(f)
    rows, cols = im.shape
    crow,ccol = rows/2 , cols/2

    #highpass
    ft[int(crow)-n:int(crow)+n, int(ccol)-n:int(ccol)+n] = 0

    #lowpass
    mask = np.zeros([rows, cols])
    mask[int(crow)-m:int(crow)+m, int(ccol)-m:int(ccol)+m] = 1
    
    ft = ft*mask    
    f_ishift = np.fft.ifftshift(ft)
    img_back = np.fft.ifft2(f_ishift)
    img_back = np.abs(img_back)
    img_back=denoising(np.array(img_back,dtype=np.uint8))
    showImage(img_back)
    return(img_back)

def denoising(im):
    return cv2.fastNlMeansDenoising(im)

def showImage(equ):
    plt.imshow(equ,cmap="gray")
    plt.show()

def sobel(img):
    sx = ndimage.sobel(img, axis=0, mode='constant')
    sy = ndimage.sobel(img, axis=1, mode='constant')
    sob = np.hypot(sx, sy)
    return sob.astype(np.uint8)

def spacialFilter(img):
    img = ndimage.median_filter(img,size=5)
    img = cv2.blur(img,(5,5))
    # img = signal.wiener(img)/
    return img

def hough_transform(img):
    edges = canny(np.array(img), 2, 1, 25)
    lines = probabilistic_hough_line(edges, threshold=10, line_length=5,
                                 line_gap=3)


    showImage(lines)


def morphoPeration(img):
    kernel = np.ones((3,3),np.uint8)
    # opening = cv2.morphologyEx(img,cv2.MORPH_OPEN,kernel, iterations = 1)
    closing = cv2.morphologyEx(img,cv2.MORPH_CLOSE,kernel, iterations = 1)
    return closing


def foregroundDefect(img):
    #images 0003  0012
    img = cv2.equalizeHist(img)
    img = spacialFilter(img)
    img = denoising(img)
    img = morphoPeration(img)
    img=LevelSlicing(img,220,255)
    showImage(img)

def threadedone():
    img = cv2.imread("0158.jpg", 0)
    # img = cv2.imread("0192.jpg", 0)
    img = signal.wiener(img).astype(np.uint8)
    img = cv2.equalizeHist(img)
    img = spacialFilter(img)
    img = denoising(img)
    img=fourierfilter(img)
    img = morphoPeration(img)
    kernel = np.ones((3,3),np.uint8)
    img = cv2.morphologyEx(img,cv2.MORPH_OPEN,kernel, iterations = 3)
    img = cv2.dilate(img,kernel,iterations=2)
    img = cv2.bitwise_not(img)
    img = cv2.erode(img,kernel,iterations=1)
    img=LevelSlicing(img,220,255)
    # hough_transform(img)
    showImage(img)

def backgroundDefect(img,low_limit=75,high_limit=255,errosion=False):
    # img = cv2.imread("0020.jpg", 0)
    # original_img = cv2.imread("0158.jpg", 0)
    kernel = np.ones((3,3),np.uint8)
    img = signal.wiener(img).astype(np.uint8)
    img = cv2.equalizeHist(img)
    img = spacialFilter(img)
    img = denoising(img)
    img=fourierfilter(img)
    img = morphoPeration(img)
    img = cv2.blur(img,(4,4))
    if errosion:
        img = cv2.morphologyEx(img,cv2.MORPH_OPEN,kernel, iterations = 1)
    img=LevelSlicing(img,low_limit,high_limit)
    showImage(img)

def holes():
    img = cv2.imread("0192.jpg", 0)
    img = signal.wiener(img).astype(np.uint8)
    img = cv2.equalizeHist(img)
    img = spacialFilter(img)
    img = denoising(img)
    img = cv2.blur(img,(5,5))
    img=LevelSlicing(img,0,90)
    showImage(img)

if __name__ == "__main__":
    threadedone()
    img = cv2.imread("0003.jpg",0)
    foregroundDefect(img)
    img = cv2.imread("0012.jpg",0)
    foregroundDefect(img)
    img = cv2.imread("0020.jpg",0)
    backgroundDefect(img,errosion=False)
    img = cv2.imread("0041.jpg",0)
    backgroundDefect(img,75,255,errosion=False)
    img = cv2.imread("0076.jpg",0)
    backgroundDefect(img,75,255,errosion=True)
    img = cv2.imread("0106.jpg",0)
    foregroundDefect(img)
    holes()


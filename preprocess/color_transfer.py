# coding: utf-8

# # Color Transfer
#
# ## Source Image
# ![source](source.jpg)
#
# ## Target Image
# ![target](target.jpg)

# Here, we implement (loosely) the color transfer algorithm in [Color Transfer Between Images](https://www.researchgate.net/publication/220518215_Color_Transfer_between_Images) by Reinhard et al, 2001.
#
# The paper utilizes the L x a x b x color space, the mean and the standard deviation of each of L(lightness), a(red=postive axis, green=negative axis) and b(blue=negative axis, yellow=postive axis) for the transfer of color from source to the target image.
#
# OpenCV respresents iamges in NumPy arrays, but default type is *uint8* datatype. This works in many cases but here the mean and teh standard deviation can be in decimal and negative, therefore to avoid any loss we use float.

# In[1]:

import numpy as np
import cv2
import argparse


# ## Transfer Color
# Input a *source* and *target* image. The color space of *source* image is transferred to the color space of *target* image.

# In[2]:

def color_transfer(source, target):
    # convert color space from BGR to L*a*b color space
    # note - OpenCV expects a 32bit float rather than 64bit
    source = cv2.cvtColor(source, cv2.COLOR_BGR2LAB).astype("float32")
    target = cv2.cvtColor(target, cv2.COLOR_BGR2LAB).astype("float32")

    # compute color stats for both images
    (lMeanSrc, lStdSrc, aMeanSrc, aStdSrc, bMeanSrc, bStdSrc) = image_stats(source)
    (lMeanTar, lStdTar, aMeanTar, aStdTar, bMeanTar, bStdTar) = image_stats(target)

    # split the color space
    (l, a, b) = cv2.split(target)

    # substarct the means from target image
    l -= lMeanTar
    a -= aMeanTar
    b -= bMeanTar

    # scale by the standard deviation
    l = (lStdTar/lStdSrc)*l
    a = (aStdTar/aStdSrc)*a
    b = (bStdTar/bStdSrc)*b

    # add the source mean
    l += lMeanSrc
    a += aMeanSrc
    b += bMeanSrc

    # clipping the pixels between 0 and 255
    l = np.clip(l, 0, 255)
    a = np.clip(a, 0, 255)
    b = np.clip(b, 0, 255)

    # merge the channels
    transfer = cv2.merge([l, a, b])

    # converting back to BGR
    transfer = cv2.cvtColor(transfer.astype("uint8"), cv2.COLOR_LAB2BGR)

    return transfer


# ## Calculating Image Statistics
# The mean and standard deviation of the L, a, b channels of both source and target images.

# In[3]:

def image_stats(image):
    # compute mean and standard deviation of each channel
    (l, a, b) = cv2.split(image)
    (lMean, lStd) = (l.mean(), l.std())
    (aMean, aStd) = (a.mean(), a.std())
    (bMean, bStd) = (b.mean(), b.std())

    return (lMean, lStd, aMean, aStd, bMean, bStd)


# ## Display Images

# In[4]:

def show_image(title, image, width=720):
    r = width/float(image.shape[1])
    dim = (width, int(image.shape[0]*r))
    resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

    cv2.imshow(title, resized)


if __name__ == '__main__':

    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-s", "--source", required = True,
        help = "Path to the source image")
    ap.add_argument("-t", "--target", required = True,
        help = "Path to the target image")
    ap.add_argument("-o", "--output", help = "Path to the output image (optional)")
    args = vars(ap.parse_args())

    source = cv2.imread(args["source"])
    target = cv2.imread(args["target"])

    # transfer of color
    transfer = color_transfer(source, target)

    # check to see if the output image should be saved
    if args["output"] is not None:
        cv2.imwrite(args["output"], transfer)

    # display of image
    show_image("Source", source)
    show_image("Target", target)
    show_image("Transfer", transfer)
    cv2.waitKey(0)

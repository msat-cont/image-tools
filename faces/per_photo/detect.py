#!/usr/bin/env python

import os, sys
import numpy as np
import cv2
#from mahotas.features import lbp_transform # this function is shadowed at __init__ in features
#from mahotas.features import lbp # this function does not take an already lbp_transformed image
import mahotas
from mahotas.features import _lbp
from mahotas.interpolate import shift

IMG_PATH = 'test.jpg'
if 1 < len(sys.argv):
    if sys.argv[1]:
        IMG_PATH = sys.argv[1]
if not os.path.isfile(IMG_PATH):
    sys.stderr.write('image file not found: ' + str(IMG_PATH) + '\n')
    sys.exit(1)

# https://github.com/Itseez/opencv/blob/master/data/haarcascades/haarcascade_frontalface_alt.xml
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml') # looks the most reasonable

def lbp_transform_local(image, radius, points, ignore_zeros=False, preserve_shape=True):

    if ignore_zeros and preserve_shape:
        raise ValueError('mahotas.features.lbp_transform: *ignore_zeros* and *preserve_shape* cannot both be used together')

    image = np.asanyarray(image, dtype=np.float64)
    if image.ndim != 2:
        raise ValueError('mahotas.features.lbp_transform: This function is only defined for two dimensional images')

    if ignore_zeros:
        Y,X = np.nonzero(image)
        def select(im):
            return im[Y,X].ravel()
    else:
        select = np.ravel

    pixels = select(image)
    angles = np.linspace(0, 2*np.pi, points+1)[:-1]
    data = []
    for dy,dx in zip(np.sin(angles), np.cos(angles)):
        data.append(
            select(shift(image, [radius*dy,radius*dx], order=1)))
    data = np.array(data)
    codes = (data > pixels).astype(np.int32)
    codes *= (2**np.arange(points)[:,np.newaxis])
    codes = codes.sum(0)
    codes = _lbp.map(codes.astype(np.uint32), points)
    if preserve_shape:
        codes = codes.reshape(image.shape)
    return codes

def take_hist(codes, points):
    final = fullhistogram(codes.astype(np.uint32))
    codes = np.arange(2**points, dtype=np.uint32)
    iters = codes.copy()
    codes = _lbp.map(codes.astype(np.uint32), points)
    pivots = (codes == iters)
    npivots = np.sum(pivots)
    compressed = final[pivots[:len(final)]]
    compressed = np.append(compressed, np.zeros(npivots - len(compressed)))
    return compressed


fullhistogram = mahotas.histogram.fullhistogram
lbp_transform = lbp_transform_local

img = cv2.imread(IMG_PATH)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.equalizeHist(gray)

# for testing several cellings; has to have even division
cells1 = [
[0, 1, 1, 1, 1, 0],
[1, 4, 4, 4, 4, 1],
[1, 4, 4, 4, 4, 1],
[1, 1, 2, 2, 1, 1],
[1, 2, 2, 2, 2, 1],
[0, 1, 1, 1, 1, 0]
]

cells2 = [
[0, 0, 1, 1, 0, 0],
[0, 4, 4, 4, 4, 0],
[0, 4, 4, 4, 4, 0],
[0, 1, 2, 2, 1, 0],
[0, 1, 1, 1, 1, 0],
[0, 0, 0, 0, 0, 0]
]

cells3 = [
[0, 0, 1, 1, 0, 0],
[0, 2, 2, 2, 2, 0],
[0, 2, 2, 2, 2, 0],
[0, 1, 1, 1, 1, 0],
[0, 1, 1, 1, 1, 0],
[0, 0, 0, 0, 0, 0]
]

cells = cells1

regions = len(cells) # here we expect even regions count

hist_count = 0
hist_count_mul = 0
for cell_row in cells:
    for cell_val in cell_row:
        hist_count_mul += cell_val
        if cell_val:
            hist_count += 1
hist_count = hist_count // 2

# it seems to be better to scale down than to scale up
face_size = 102
#face_size = 120
cell_size = face_size / regions
cell_area = cell_size * cell_size

cell_hist_count = 36 # for 8 points
hist_size = hist_count * cell_hist_count

sum_compare = hist_count_mul * cell_area

faces = face_cascade.detectMultiScale(gray, 1.3, 3) # 3 neighbors seems to work well
print(faces)

hists = []
for (x,y,w,h) in faces:
    hist_full = np.zeros((hist_size,), dtype=np.int32)

    cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
    part = gray[y:(y+h),x:(x+w)]
    part = cv2.resize(part, (face_size,face_size))
    gray_lt = lbp_transform(part, 1, 8, False, True)
    hist_pos = 0
    for hrank in range(regions):
        hstart = cell_size * hrank
        hend = hstart + cell_size
        for wrank in range(regions // 2):
            cell_mul = cells[hrank][wrank]
            if not cell_mul:
                continue

            w1start = cell_size * wrank
            w1end = w1start + cell_size
            w2end = cell_size * (regions - wrank)
            w2start = w2end - cell_size
            box1 = gray_lt[hstart:hend, w1start:w1end]
            box2 = gray_lt[hstart:hend, w2start:w2end]
            hist1 = take_hist(box1.reshape((cell_area,)), 8)
            hist2 = take_hist(box2.reshape((cell_area,)), 8)
            hist_full[hist_pos:(hist_pos+cell_hist_count)] = cell_mul * (hist1 + hist2).astype(np.int32)
            hist_pos += cell_hist_count

    hists.append(hist_full)

print('count of found faces: ' + str(len(hists)))
# to set the distance limit probably to 0.125, definitely not greater than 0.15

if 1 < len(hists):
    for i in range(len(hists)):
        for j in range(i):
            if i == j:
                continue
            hist_diff = hists[i]-hists[j]
            diff = np.sum(np.abs(hists[i]-hists[j]))
            diff_rel = float(diff) / float(sum_compare * 2.0)
            print('i: ' + str(i) + ', j: ' + str(j) + ', diff: ' + str(diff) + ', diff_rel: ' + str(diff_rel))

cv2.imshow('img',img)
for w in range(2):
    cv2.waitKey(0)
cv2.destroyAllWindows()


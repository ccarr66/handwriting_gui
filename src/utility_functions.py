import cv2
import numpy as np
from imutils.contours import sort_contours
import imutils

if __name__ == "__main__":
    raise Exception('Cannot be called as main script')

def get_lines(image, output_images, output_image_labels, show=False):
    """
    :return: list of roi parameters for lines
    """
    # grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    output_images.append(gray.copy())
    output_image_labels.append("Gray")
    if show:
        cv2.imshow('gray', gray)
        cv2.waitKey(0)

    # binary
    ret, thresh = cv2.threshold(gray, 105, 255, cv2.THRESH_BINARY_INV)  # 127 changed to 0
    output_images.append(thresh.copy())
    output_image_labels.append("Thresh")
    if show:
        cv2.imshow('second', thresh)
        cv2.waitKey(0)

    # dilation
    kernel = np.ones((5, 125), np.uint8)
    img_dilation = cv2.dilate(thresh, kernel, iterations=1)
    output_images.append(img_dilation.copy())
    output_image_labels.append("Dilation")
    if show:
        cv2.imshow('dilated', img_dilation)
        cv2.waitKey(0)

    # find contours
    ctrs = cv2.findContours(img_dilation.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    ctrs = imutils.grab_contours(ctrs)

    # sort contours
    sorted_ctrs = sort_contours(ctrs, method="top-to-bottom")[0]
    l_xs = []
    l_ys = []
    l_ws = []
    l_hs = []

    for i, ctr in enumerate(sorted_ctrs):
        # Get bounding box
        x, y, w, h = cv2.boundingRect(ctr)

        # Getting ROI
        roi = image[y:y + h, x:x + w]
        l_xs.append(x)
        l_ys.append(y)
        l_ws.append(w)
        l_hs.append(h)

        lineSegment = cv2.rectangle(image, (x, y), (x + w, y + h), (90, 0, 255), 2)
        output_images.append(lineSegment.copy())
        output_image_labels.append("Line Segment ")

    output_images.append(image.copy())
    output_image_labels.append("Processed Image")
    if show:
        cv2.imshow('marked areas', image)
        cv2.waitKey(0)

    return l_xs, l_ys, l_ws, l_hs
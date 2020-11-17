# import the necessary packages
from tensorflow.keras.models import load_model
from imutils.contours import sort_contours
from utility_functions import *
import numpy as np
import imutils
import cv2

model = None

def modelIsValid(trainedHWModelPath):
    try:
        global model
        model = load_model(trainedHWModelPath)
        return True
    except:
        return False

def analyzeImage(inputImagePath, show = False):

    # load the handwriting OCR model
    print("[INFO] loading handwriting OCR model...")
    #model = load_model(trainedHWModel)
        
    
    output_images = []
    output_image_labels = []

    # load the input image from disk, convert it to grayscale, and blur
    # it to reduce noise
    image = cv2.imread(inputImagePath)  # load image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # converts image to greyscale

    lines = get_lines(image, output_images, output_image_labels, show)
    lx, ly, lw, lh = lines

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)  # blurs image
    output_images.append(blurred)
    output_image_labels.append("Blurred")


    # perform edge detection, find contours in the edge map, and sort the
    # resulting contours from left-to-right
    edged = cv2.Canny(blurred, 30, 150)  # grey-scale, edge-detected image
    output_images.append(edged)
    output_image_labels.append("Edged")
    cnts = [[]] * len(lx)
    space_margin = 0
    for line in range(len(lx)):
        space_margin += lw[line]
        cnts[line] = (cv2.findContours(edged.copy()[ly[line]:ly[line] + lh[line], lx[line]:lx[line] + lw[line]],
                                    cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE))  # creates an array of contours
        cnts[line] = imutils.grab_contours(cnts[line])  # returns array of contours
        cnts[line] = sort_contours(cnts[line], method="left-to-right")[0]  # sorts contours left to right

    space_marign = space_margin / (8 * len(lw))
    print(f'space_marign: {space_marign}')
    # initialize the list of contour bounding boxes and associated
    # characters that we'll be OCR'ing
    chars = []
    spaces = []
    index = 0
    px, py, pw, ph = 0, 0, 0, 0
    skip = False

    # loop over the contours
    for line in range(len(lx)):
        for c in cnts[line]:  # iterates through contours array
            # compute the bounding box of the contour
            (x, y, w, h) = cv2.boundingRect(c)  # bounding box of current contour

            x += lx[line]
            y += ly[line]

            if index != 0:
                if not(px - 15 < x and px + pw + 15 > x + w and py - 15 < y and py + ph + 15 > y + h):
                    skip = False
                    if abs(x - px) >= space_marign:
                        spaces.append(index)
                else:
                    skip = True

            # filter out bounding boxes, ensuring they are neither too small
            # nor too large
            if (5 <= w <= 150) and (20 <= h <= 120) and not skip:

                # extract the character and threshold it to make the character
                # appear as *white* (foreground) on a *black* background, then
                # grab the width and height of the thresholded image
                roi = gray[y:y + h, x:x + w]  # y:y + h, x:x + w is the region of interest returned by cv2.boundingRect()
                thresh = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
                (tH, tW) = thresh.shape

                # if the width is greater than the height, resize along the
                # width dimension
                if tW > tH:
                    thresh = imutils.resize(thresh, width=32)

                # otherwise, resize along the height
                else:
                    thresh = imutils.resize(thresh, height=32)

                # re-grab the image dimensions (now that its been resized)
                # and then determine how much we need to pad the width and
                # height such that our image will be 32x32
                (tH, tW) = thresh.shape
                dX = int(max(0, 32 - tW) / 2.0)
                dY = int(max(0, 32 - tH) / 2.0)

                # pad the image and force 32x32 dimensions
                padded = cv2.copyMakeBorder(thresh, top=dY, bottom=dY, left=dX, right=dX,
                                            borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0))
                padded = cv2.resize(padded, (32, 32))

                # prepare the padded image for classification via our
                # handwriting OCR model
                padded = padded.astype("float32") / 255.0
                padded = np.expand_dims(padded, axis=-1)

                # update our list of characters that will be OCR'd
                chars.append((padded, (x, y, w, h)))
                index += 1
                (px, py, pw, ph) = (x, y, w, h)


    # extract the bounding box locations and padded characters
    boxes = [b[1] for b in chars]
    chars = np.array([c[0] for c in chars], dtype="float32")
    np.ndarray.view(chars)

    # OCR the characters using our handwriting recognition model
    preds = model.predict(chars)

    # define the list of label names
    labelNames = "0123456789"
    labelNames += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    labelNames = [l for l in labelNames]
    output_labels = []

    # loop over the predictions and bounding box locations together
    for (pred, (x, y, w, h)) in zip(preds, boxes):
        # find the index of the label with the largest corresponding
        # probability, then extract the probability and label
        i = np.argmax(pred)
        prob = pred[i]
        label = labelNames[i]
        output_labels.append(label)

        # draw the prediction on the image
        print("[INFO] {} - {:.2f}%".format(label, prob * 100))
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(image, label, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)

        output_images.append(image.copy())
        output_image_labels.append("Character: " + label)
        
    added = 0
    for space in spaces:
        output_labels.insert(space + added, ' ')
        added += 1

    return (output_labels, output_images, output_image_labels)

# USAGE
# python ocr_handwriting.py --model handwriting.model --image images/umbc_address.png
if __name__ == "__main__":
    import sys
    import argparse
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True, help="path to input image")
    ap.add_argument("-m", "--model", type=str, required=True, help="path to trained handwriting recognition model")
    ap.add_argument("-s", "--show", type=bool, required=False, help="path to trained handwriting recognition model")
    args = vars(ap.parse_args())
    
    show = False
    if args["show"] is not None:
        show = args["show"]

    analyzeImage(args["image"], args["model"], show)
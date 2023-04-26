import cv2
from matplotlib import pyplot as plt
import numpy as np
import imutils
import easyocr

import streamlit as st
from  PIL import Image

# uploaded_file = st.file_uploader("", type=['jpg','png','jpeg'])
def calulate_number_plate(uploaded_file):
    try: 
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            

            st.markdown('<p style="text-align: left;">Car Photo</p>',unsafe_allow_html=True)
            st.image(image,width=300)  

            #Image read
            # img = cv2.imread('data/image1.jpg')
            img = np.array(image.convert('RGB'))
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # plt.imshow(cv2.cvtColor(gray, cv2.COLOR_BGR2RGB))

            ##Apply filter and find edges for localization
            bfilter = cv2.bilateralFilter(gray, 11, 17, 17) #Noise reduction
            edged = cv2.Canny(bfilter, 30, 200) #Edge detection
            # plt.imshow(cv2.cvtColor(edged, cv2.COLOR_BGR2RGB))

            ##Find Contours and Apply Mask
            keypoints = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            contours = imutils.grab_contours(keypoints)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

            location = None
            for contour in contours:
                approx = cv2.approxPolyDP(contour, 10, True)
                if len(approx) == 4:
                    location = approx
                    break
            print(location)

            mask = np.zeros(gray.shape, np.uint8)
            new_image = cv2.drawContours(mask, [location], 0,255, -1)
            new_image = cv2.bitwise_and(img, img, mask=mask)

            (x,y) = np.where(mask==255)
            (x1, y1) = (np.min(x), np.min(y))
            (x2, y2) = (np.max(x), np.max(y))
            cropped_image = gray[x1:x2+1, y1:y2+1]

            ##Use Easy OCR To Read Text
            reader = easyocr.Reader(['en'])
            result = reader.readtext(cropped_image)
            print(result)

            ##final result
            text = result[0][-2]
            accuracy = result[0][-1]
            accuracy = round(accuracy,2)*100
            font = cv2.FONT_HERSHEY_SIMPLEX
            res = cv2.putText(img, text=text, org=(approx[0][0][0], approx[1][0][1]+60), fontFace=font, fontScale=1, color=(0,255,0), thickness=2, lineType=cv2.LINE_AA)
            res = cv2.rectangle(img, tuple(approx[0][0]), tuple(approx[2][0]), (0,255,0),3)
            plt.imshow(cv2.cvtColor(res, cv2.COLOR_BGR2RGB))
            print(text)
        else:
            print("something wrong")
            text = ""
            accuracy= ""

    except Exception as e:
        print("Algo might not have found number plate")
        text = ""
        accuracy= ""
    return text,accuracy

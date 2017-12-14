
from xml.dom import minidom
from PIL import Image
from pylab import array, imshow, show, ginput, close
from scipy.ndimage import measurements
import os
import xlwt
import Tkinter, tkFileDialog
import subprocess as sp
from tkinter import messagebox
from tkMessageBox import showinfo

filepath = tkFileDialog.askopenfilename(title="Ouvrir une image ou un pdf a convertir",filetypes=[("all files",".*")])
file_name, file_extension = os.path.splitext(os.path.basename(filepath))


img = Image.open(filepath)

# /!\ ADAPTER selon le tableau il faudra changer la valeur "(i-127)*2.3)"
img_tableau_noir = img.point(lambda i: (i-127)*2.3).point(lambda i: 0 if i < 250 else 255)
img_table = img_tableau_noir.point(lambda i: 0 if i == 255 else 255)


# ceate array
img_block_array = array(img.point(lambda i: 0 if i < 250 else 255))

# Get connected componens and their bounding boxes...
labels, num_obects = measurements.label(img_block_array)
boxes = measurements.find_objects(labels)

# /!\ ADAPTER selon le tableau
min_height, max_height, min_width, max_width = 30, 300, 100, 800

# trier les boite avec bonne taille
panel_boxes = list()
for boxe in boxes:
    if min_height < boxe[0].stop - boxe[0].start or min_height == None: # hauteur min
        if max_height > boxe[0].stop - boxe[0].start or max_height == None: # hauteur max
            if min_width < boxe[1].stop - boxe[1].start or min_width == None: # largeur min
                if max_width > boxe[1].stop - boxe[1].start or max_width == None: # largeur max
                    panel_boxes.append([int(boxe[1].start), int(boxe[0].start), int(boxe[1].stop), int(boxe[0].stop)]) 
                    
print panel_boxes

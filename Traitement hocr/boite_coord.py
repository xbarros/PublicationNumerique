from PIL import Image
from pylab import array, imshow, show
from scipy.ndimage import measurements
import os



def main():

    img_table, img = choose_img()
    
    
    # ceate array
    img_block_array = array(img_table)
    img_array = array(img)
    
    imshow(img_block_array)
    show()
    imshow(img_array)
    show()

    # ici choisir ce qu"on veut annalyser comme tableau (min et max pour les boite)... 
    panel_boxes = find_objects_with_size(
        img_block_array,
        min_height=40,
        min_width=10,
        )
 
    write_text_from_panels(img_array, panel_boxes)
 
def write_text_from_panels(image_array, panels):
    

    for i in range(len(panels)):
        # panels[i] --> coordonnee de chaque boite
        panel_array = image_array[panels[i]]
        
        # transforme array en image et la sauve...
        im = Image.fromarray(panel_array)
        
        imshow(array(im))
        show()

def find_objects_with_size(img_array, min_height=None, max_height=None, min_width=None, max_width=None):
    
    # Get connected componens and their bounding boxes...
    labels, num_obects = measurements.label(img_array)
    boxes = measurements.find_objects(labels)
    
    # trier les boite avec bonne taille
    panel_boxes = list()
    for boxe in boxes:
        
        if min_height < boxe[0].stop - boxe[0].start or min_height == None: # hauteur min
            if max_height > boxe[0].stop - boxe[0].start or max_height == None: # hauteur max
                if min_width < boxe[1].stop - boxe[1].start or min_width == None: # largeur min
                    if max_width > boxe[1].stop - boxe[1].start or max_width == None: # largeur max
                        panel_boxes.append([boxe[0].start, boxe[1].start, boxe[0].stop, boxe[1].stop]) 
                        
            # ajouter coordonnee boite ici !!!!!!!!!!!-------------------
    print panel_boxes
    return panel_boxes
    
def choose_img():
    
    img = Image.open("petit2.tif")
    
    img_tableau_noir = img.point(lambda i: (i-127)*2.3).point(lambda i: 0 if i < 250 else 255)
    img_tableau_blanc = img_tableau_noir.point(lambda i: 0 if i == 255 else 255)
    #purifier image de base
    img = img.point(lambda i: (i-127)*2.3).point(lambda i: 0 if i < 50 else 255)
    
    return img_tableau_blanc, img
    
if __name__ == "__main__":
    main()
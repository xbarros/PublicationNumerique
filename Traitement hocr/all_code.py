from xml.dom import minidom
from PIL import Image
from pylab import array, imshow, show
from scipy.ndimage import measurements
import os


def main():

    #print boite_coord()
    #print word_coord()
    
    word_table = word_in_box(word_coord(),boite_coord())
    print word_table
    
# utiliser image tif
def boite_coord():
    
    img = Image.open("petit2.tif")
    
    # ADAPTER selon le tableau il faudra changer la valeur "(i-127)*2.3)"
    img_tableau_noir = img.point(lambda i: (i-127)*2.3).point(lambda i: 0 if i < 250 else 255)
    
    img_table = img_tableau_noir.point(lambda i: 0 if i == 255 else 255)
    
    # ceate array
    img_block_array = array(img_table)
    
    # Get connected componens and their bounding boxes...
    labels, num_obects = measurements.label(img_block_array)
    boxes = measurements.find_objects(labels)
    
    # ADAPTER selon le tableau
    min_height, max_height, min_width, max_width = 30, 300, 10, 700
    
    # trier les boite avec bonne taille
    panel_boxes = list()
    for boxe in boxes:
        if min_height < boxe[0].stop - boxe[0].start or min_height == None: # hauteur min
            if max_height > boxe[0].stop - boxe[0].start or max_height == None: # hauteur max
                if min_width < boxe[1].stop - boxe[1].start or min_width == None: # largeur min
                    if max_width > boxe[1].stop - boxe[1].start or max_width == None: # largeur max
                        panel_boxes.append([int(boxe[1].start), int(boxe[0].start), int(boxe[1].stop), int(boxe[0].stop)]) 
                        
    """
    imshow(img_tableau_noir)
    show()
    """
    
    return panel_boxes

    
# utiliser document xml
# REMARQUE /!\ NE MARCHE PAS AVEC CHARACTERE SPECIEUX /!\
def word_coord():

    all_word = list()

    # Import xml doc
    xmldoc = minidom.parse('petit2.xml')
    # garde que span
    reflist = xmldoc.getElementsByTagName('span')
    #print(len(reflist))
    #print (reflist[0].toxml()) # afficher contenu xml 

    for i in range(len(reflist)):
        refword = reflist[i]
        if refword.attributes["class"].value == "ocrx_word":
            # trouver ccord de chaque mot 
            bbox_all = refword.attributes["title"].value.split(";")
            bbox_coord = bbox_all[0].split()
            bbox_coord.remove("bbox")
            bbox_coord = map(int, bbox_coord) # in python3 --> bbox_coord = list(map(int, bbox_coord))
            # trouver le contenu du mot
            span = minidom.parseString(refword.toxml())
            span_content = [p.firstChild.wholeText for p in span.getElementsByTagName("span") if p.firstChild.nodeType == p.TEXT_NODE]
            # si vide --> ADAPTER trouver qqch de tout le temps ok
            if len(span_content) == 0:
                span_content = [p.firstChild.wholeText for p in span.getElementsByTagName("strong") if p.firstChild.nodeType == p.TEXT_NODE]
            # ajouter valeur dans la liste des coordonnee
            bbox_coord.append(span_content[0])
            
            all_word.append(bbox_coord)
            
    return all_word
        
def word_in_box(list_word, list_box):
    
    for i in list_box:
        box_content = str()
        #si le mot dans la boite (comparer les coordonnee)
        for j in list_word:            
            if i[0] < j[0] < i[2] and\
            i[0] < j[2] < i[2] and\
            i[1] < j[1] < i[3] and\
            i[1] < j[3] < i[3] :
                box_content = box_content + str(j[4]) + " "
        # ajoute a la coordonnee de la boite son contenue
        i.append(box_content) 
    
    return list_box

if __name__ == "__main__":
    main()
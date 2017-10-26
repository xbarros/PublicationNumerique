from xml.dom import minidom
from PIL import Image
from pylab import array, imshow, show
from scipy.ndimage import measurements
import os
import xlwt
import Tkinter
import tkFileDialog

def main():

    word_table = word_in_box(word_coord(),boite_coord())
    creer_xls(coord_excel(word_table))
        

        
# utiliser image tif
def boite_coord():
    
    img = Image.open("petit2.tif")
    
    # /!\ ADAPTER selon le tableau il faudra changer la valeur "(i-127)*2.3)"
    img_tableau_noir = img.point(lambda i: (i-127)*2.3).point(lambda i: 0 if i < 250 else 255)
    
    img_table = img_tableau_noir.point(lambda i: 0 if i == 255 else 255)
    
    # ceate array
    img_block_array = array(img_table)
    
    # Get connected componens and their bounding boxes...
    labels, num_obects = measurements.label(img_block_array)
    boxes = measurements.find_objects(labels)
    
    # /!\ ADAPTER selon le tableau
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
            # si vide --> /!\ ADAPTER trouver qqch de tout le temps ok
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
                if box_content == "":
                    box_content = box_content + str(j[4])
                else: 
                    box_content = box_content + " " + str(j[4]) 
        # ajoute a la coordonnee de la boite son contenue
        del i[2]
        del i[2]
        i.append(box_content)
        
    return list_box
    
    
def coord_excel(word_table):
    
    x_coord = list()
    y_coord = list()

    # obtenir les coordonnee x et y 
    for i in word_table:
        if i[0] not in x_coord:
            x_coord.append(i[0])
        if i[1] not in y_coord:
            y_coord.append(i[1])
        
    # ordonner par ordre croissant
    x_coord = sorted(x_coord)
    y_coord = sorted(y_coord)

    # valeur de coordonnee sur image corespond a 
    # valeur de coordonnee de tableau excel
    x_coord = {k: v for v, k in enumerate(x_coord)}
    y_coord = {k: v for v, k in enumerate(y_coord)}
        
    # transformee coordonnee sur image en coordonnee de tableau excel
    for i in x_coord.keys():
        for j in word_table:
            if i == j[0]:
                j[0] = x_coord[i]
    for i in y_coord.keys():
        for j in word_table:
            if i == j[1]:
                j[1] = y_coord[i]
    
    return word_table
    
def creer_xls(contenu):

    # creer feuille excel
    wb = xlwt.Workbook(encoding="utf-8")
    ws = wb.add_sheet("XXX")
    # creer fenetre de dialogue
    root = Tkinter.Tk()
    root.withdraw() #use to hide tkinter window
    
    # remplire la  feuille excel
    for i in range(len(contenu)):
        ws.write(contenu[i][1], contenu[i][0], contenu[i][2])

    # choisir le dossier de sauvegarde
    currdir = os.getcwd()
    path_to_save = tkFileDialog.askdirectory(parent=root, initialdir=currdir, title="Please select a directory to save your excel file")
    
    # sauver le dossier excel 
    if len(path_to_save) > 0:
        print "You chose %s" % path_to_save
        wb.save(os.path.normpath(path_to_save)+"\image_to_excel.xls") 
    # si pas de lien rentre, ne rien faire
    else:
        print "Le fichier n'a pas ete sauvegarde" 
  

if __name__ == "__main__":
    main()
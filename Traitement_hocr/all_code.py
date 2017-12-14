#/usr/bin/env python
# coding: utf-8

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


def main():

    root = Tkinter.Tk()
    root.withdraw()
    
    reponse = messagebox.askyesno("Title","Do you want to analyse a text ?")
    if reponse:
        # choisir son fichier
        path, file_name, file_extension = choose_file()

        if path != "":
            
            if file_extension in [".pdf", ".PDF"]:
            
                # convertir le pdf en fichier image grace a imagemagic
                path = pdf_to_tiff(path)
                file_extension = ".tiff"
                
            reponse = messagebox.askyesno("Title","Do you want to analyse a all the picture ?")
            if not reponse:
                path, file_name, file_extension = select_img(path, file_name, file_extension)
    
            text_img(path, file_extension)
                
    else:
        reponse = messagebox.askyesno("Title","Do you want to analyse a table ?")
        if reponse:
            # choisir son fichier
            path, file_name, file_extension = choose_file()

            if path != "":
                
                if file_extension in [".pdf", ".PDF"]:
                
                    # convertir le pdf en fichier image grace a imagemagic
                    path = pdf_to_tiff(path)
                    file_extension = ".tiff"

                reponse = messagebox.askyesno("Title","Do you want to analyse a all the picture ?")
                if not reponse:
                    path, file_name, file_extension = select_img(path, file_name, file_extension)
       
                # analyser l'image avec tesseract    
                xml_path = table_img(path, file_extension)
                os.chdir(os.path.normpath(path[:-len(file_name+file_extension)])) # revenir la ou on traite le fichier (optionel)
                
                #xml_path = "C:\Users\Xavier\Desktop\Projet\\PublicationNumerique\Traitement_hocr\petit2(1).xml" # pour des test.. a supprimer !

                # utiliser document xml et l'image pour trouver les coordonnees
                word = word_coord(xml_path)
                boite = boite_coord(path)
                #print (word)

                # mettre les mots dans les boites
                word_table = word_in_box( word, boite )

                # transformer coordonnee de l'image en coordonnee excel
                contenu_excel = coord_excel(word_table)

                # creer tableau excel
                root.destroy()
                creer_xls(contenu_excel)

    
# choisir son fichier
def choose_file():

    root = Tkinter.Tk()
    root.withdraw()

    # demander a l'utilisateur un fichier a traiter
    filepath = tkFileDialog.askopenfilename(title="Ouvrir une image ou un pdf a convertir",filetypes=[("all files",".*")])
    file_name, file_extension = os.path.splitext(os.path.basename(filepath))

    # verifier que c'est un fichier image
    file_allowed = ["jpg", "png", "PNG", "JPG", "tif", "tiff", "TIF" "TIFF", "PDF", "pdf"]
    
    # si l'utilisateur ne rentre pas qqch de correcte, redemmander 
    while file_extension[1:] not in file_allowed:
        
        if filepath == "":
            messagebox.showwarning("Warning","Warning, You don't choose anything")
            answer = messagebox.askretrycancel("Question", "Do you want to try it again?")
            if answer == False:
                break

        else:
            messagebox.showerror("Error", "Error, You must choose an image file or pdf file !")
            answer = messagebox.askretrycancel("Question", "Do you want to try it again?")
            if answer == False:
                break
        
        filepath = tkFileDialog.askopenfilename(title="Ouvrir une image ou un pdf a convertir",filetypes=[("all files",".*")])
        file_name, file_extension = os.path.splitext(os.path.basename(filepath))
    
    root.destroy()

    return filepath, file_name, file_extension
 
# convertir le pdf en fichier image grace a imagemagic
def pdf_to_tiff(path_pdf):

    pdf = os.path.basename(path_pdf)
    path = path_pdf[:-len(pdf)]

    commande = "convert -density 400 "+path_pdf+" -depth 8 -strip -alpha off "+path+pdf[:-4]+".tiff"

    output = sp.Popen(commande, stdout=sp.PIPE, shell=True)
    outtext = output.communicate()[0].decode(encoding="utf-8", errors="ignore")
    
    return path+pdf[:-4]+".tiff"
        
                  
def select_img(img_path, file_name, file_extension):
    
    root = Tkinter.Tk()
    root.withdraw() 
    
    im = array(Image.open(img_path))
    imshow(im)
   
    showinfo("Title", 'Please click 2 points')

    coord = ginput(2)
       
    
    print [(coord[0][0],coord[0][1],coord[1][0],coord[1][0])]
    
    img = Image.open(img_path)
    img_crop = img.crop((min(coord[0][0],coord[1][0]),min(coord[0][1],coord[1][1]),max(coord[0][0],coord[1][0]),max(coord[0][1],coord[1][1])))
    """
    print img.getpixel((coord[0][0],coord[0][1])),"1" 
    """
    path = img_path[:-len(file_name + file_extension)]
    
    img_crop.save(path+"img_crop.tif")
    img_path =  path + "img_crop.tif"
    
    close()
    root.destroy()
    return img_path, "img_crop", ".tif"
  
# analyser l'image avec tesseract
def table_img(path_to_img, path_end):
        
        # pour travailler ou se trouve tesseract
        os.chdir(os.path.normpath(r"C:\Program Files\Tesseract-OCR\\")) # /!\ MODIFIER selon son chemin vers Tesseract-OCR
        
        path_basename = path_to_img[:-len(path_end)]

        # donner un ordre a la ligne de commande
        commande = "tesseract " + path_to_img +" "+ path_basename + " -l fra hocr"

        output = sp.Popen(commande, stdout=sp.PIPE, shell=True)
        outtext = output.communicate()[0].decode(encoding="utf-8", errors="ignore")
        

        if not os.path.isfile(path_basename + ".xml"): 
            os.rename( path_basename + ".hocr", path_basename + ".xml" )
        else:
            i=1
            while True:
                if not os.path.isfile(path_basename + "("+str(i)+").xml"):
                    os.rename( path_basename + ".hocr", path_basename + "("+str(i)+").xml" )
                    break
                i+=1
        
        return os.path.normpath(path_basename + ".xml")
        
        
# trouver les coordonnee des cases
def boite_coord(path_to_img):
    
    img = Image.open(path_to_img)
    
    # /!\ ADAPTER selon le tableau il faudra changer la valeur "(i-127)*2.3)"
    img_tableau_noir = img.point(lambda i: (i-127)*2.3).point(lambda i: 0 if i < 250 else 255)
    
    img_table = img_tableau_noir.point(lambda i: 0 if i == 255 else 255)
    
    # ceate array
    img_block_array = array(img_table)
    
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
                           
    return panel_boxes

    
# utiliser document xml
def word_coord(xml_path):

    all_word = list()

    # Import xml doc
    xmldoc = minidom.parse(xml_path)
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
            
            
            span = minidom.parseString(refword.toxml().encode("utf-8"))
            # trouver le contenu du mot
            span_content = [p.nodeName for p in span.getElementsByTagName("span") if p.firstChild.nodeType == p.TEXT_NODE]
            
            # si vide alors autre chose qui fonctionne
            if len(span_content) == 0:
                root = span.documentElement
                for node in root.childNodes:
                    if node.nodeType != node.TEXT_NODE:
                        span_content = node.firstChild.nodeValue
                        
            # ajouter valeur dans la liste des coordonnee
            bbox_coord.append(span_content[0])
            #print span_content, "2"
            
            all_word.append(bbox_coord)
            
            
    return all_word
  
# mettre chaque contenu de texte dans la boite dans lequel il se trouve  
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
                    box_content = box_content + str(j[4].encode("utf-8"))
                else: 
                    box_content = box_content + " " + str(j[4].encode("utf-8")) 
        # ajoute a la coordonnee de la boite son contenue
        del i[2]
        del i[2]
        i.append(box_content)

    return list_box
    
# donner les coordonnee utilisable pour creer un doc excel   
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
  
# analyser l'image avec tesseract
def text_img(path_to_img, path_end):
        
        # pour travailler ou se trouve tesseract
        os.chdir(os.path.normpath(r"C:\Program Files\Tesseract-OCR\\")) # /!\ MODIFIER selon son chemin vers Tesseract-OCR
        
        path_basename = path_to_img[:-len(path_end)]

        # donner un ordre a la ligne de commande
        commande = "tesseract " + path_to_img +" "+ path_basename + " -l fra"

        output = sp.Popen(commande, stdout=sp.PIPE, shell=True)
        outtext = output.communicate()[0].decode(encoding="utf-8", errors="ignore")
        

        # sauvegarder le text de l'image
        text_file = open(path_basename+".txt", "r")
        text_image = text_file.readlines()
        for i in range(len(text_image)):

            if text_image[i] != "\n":
                if text_image[i][-1:] == "\n":
                    if text_image[i][-2:] == "-\n":
                        text_image[i] = text_image[i][:-2]
                    else:
                        text_image[i] = text_image[i][:-1]

        text_file = open(path_basename+".txt", "w")
        
        for i in range(len(text_image)):
            if i == 0:
                text_file.write("<html>\n\t<head>\n\t\t<title>\n\t\t\tImage Content\n\t\t</title>\n\t</head>\n\t<body>\n\t\t<h1>\n")
                text_file.write("\t\t\t"+text_image[i])
                text_file.write("\n\t\t</h1>")
            
            elif text_image[i] == "\n" and i != 1 and i+1 != len(text_image):
                text_file.write("\n\t\t</p>"+text_image[i]+"\t\t<p>\n")
            
            elif text_image[i] == "\n" and i == 1:
                text_file.write(text_image[i]+"\t\t<p>\n")
            
            elif text_image[i-1] == "\n":
                text_file.write("\t\t\t"+text_image[i])
            
            else:
                text_file.write(text_image[i])
            
            if i+1 == len(text_image):
                text_file.write("\n\t\t</p>"+text_image[i]+"\t</body>\n</html>")
                            

if __name__ == "__main__":
    main()
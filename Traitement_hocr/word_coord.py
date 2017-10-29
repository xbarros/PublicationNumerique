from xml.dom import minidom

all_word = dict()
print(all_word)

# Import xml doc
xmldoc = minidom.parse('petit2.xml')
# garde que span
reflist = xmldoc.getElementsByTagName('span')
print(len(reflist))
#print (reflist[0].toxml()) # afficher contenu xml 

for i in range(len(reflist)):
    refword = reflist[i]
    if refword.attributes["class"].value == "ocrx_word":
        # trouver ccord de chaque mot 
        bbox_all = refword.attributes["title"].value.split(";")
        bbox_coord = bbox_all[0].split()
        bbox_coord.remove("bbox")
        # trouver le contenu du mot
        span = minidom.parseString(refword.toxml())
        span_content = [p.firstChild.wholeText for p in span.getElementsByTagName("span") if p.firstChild.nodeType == p.TEXT_NODE]
        
        bbox_coord.append(span_content[0])
        print(bbox_coord)

from utils import get_info, get_starts_volume
from page import PAGE
import sys, math

act_order = "/data/chancery2/acts-avec-correction.csv"
acts_page = "/data/chancery2/JJ35-95_ActSegmentation20180615/"
file_order = "/data/chancery2/page2.csv"

all_volumes, all_act_per_legajo, img_order_legajo, vol_first_image = get_info(act_order, file_order, acts_page)

volume_name = sys.argv[1]

Volume = all_act_per_legajo[volume_name]
Volume_order_img = img_order_legajo[volume_name]

first_img_with_act = vol_first_image[volume_name]
while True:
    if Volume_order_img[0][2] != first_img_with_act:
        Volume_order_img.pop(0)
    else:
        break

# for id, id_vol, volume, fol_start, fol_end, start_img in Volume:
#     print(id, id_vol, volume, fol_start, fol_end, start_img)

img_starts = get_starts_volume(Volume)

print("Image \t NumberOfstarts \t NumberOfTextRegions \t labels")

for folio, folio_legajo, img_name in Volume_order_img:
    if not img_name:
        print("////////////// Folio {} is a blank page //////////////".format(folio))
        continue
    # þ = "pepe"
    xml_page = "{}/{}.xml".format(acts_page, img_name)
    page = PAGE(xml_page)
    textRegions = page.get_textRegions()
    n_textRegions = len(textRegions)

    n_starts = img_starts.get(img_name, 0)

    labels = []

    if n_starts == n_textRegions:
        labels = ["AC" for _ in range(0,n_starts-1)]
        labels.append(("AC","AI"))
    if n_starts+1 == n_textRegions:
        if n_starts == 0:
            labels = [("AF","AM")]
        else:
            labels = ["AF"]
            labels.extend(["AC" for _ in range(0,n_starts-2)])
            labels.append(("AC","AI"))

    labels_s = ""
    for x in labels:
        if type(x) == tuple:
            x = "({}/{})".format(x[0],x[1])
        labels_s += x + "-"

    print("{} \t {} \t {} \t {}".format(img_name, n_starts, n_textRegions, labels_s))
    dif = n_textRegions - n_starts
    if dif != 0 and dif != 1:
        print("problem!")
from utils import get_info, get_starts_volume
from page import PAGE
import sys, math

act_order = "/data/chancery2/acts_corrected_march.csv"
acts_page = "/data/chancery2/JJ35-95_ActSegmentation20180615/"
file_order = "/data/chancery2/Act-to-Image20200327_order.csv"

def flatten(acts):
    res = []
    for i, acts_page in enumerate(acts):
        for j, act in enumerate(acts_page):
            res.append(act)
    return res

def act_has_tuple(acts):
    act_flatten = flatten(acts)
    for act in act_flatten:
        if type(act) == tuple:
            return True
    return False

def fit_acts(acts):
    res = []
    res_flatten = flatten(acts)
    res_flatten.append("LAST")
    count = 0
    for i, acts_page in enumerate(acts):
        res_page = []
        for j, act in enumerate(acts_page):
            if type(act) != tuple:
                res_page.append(act)
            else: # looking at LM
                next = res_flatten[count+1] #last?
                if "AC" in act and "AI" in act:
                    if next == "AF" or next == "AM":
                        res_page.append("AI")
                    elif next == "AC" or next == "LAST" or next == "AI":
                        res_page.append("AC")
                    elif type(next) == tuple:
                        res_page.append(act)
                    else:
                        print("Problem. ACT {} NEXT {}".format(act, next))
                        exit()
                if "AF" in act and "AM" in act:
                    if next == "AF" or next == "AM":
                        res_page.append("AM")
                    elif next == "AC" or next == "AI" or next == "LAST":
                        res_page.append("AF")
                    elif type(next) == tuple:
                        res_page.append(act)
                    else:
                        print("Problem. ACT {} NEXT {}".format(act, next))
                        exit()
            count += 1
        res.append(res_page)
    #for i in res:
    #    print(i)
    return res

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
res = []
res_labels = []
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

    if n_starts == 0 and n_textRegions == 0:
        print("////////////// Folio {} is a blank page becasuse n_starts and n_textRegions == 0 //////////////".format(folio))
        continue
    assert n_starts <= n_textRegions
    labels = []

    if n_starts == n_textRegions:
        labels = ["AC" for _ in range(0,n_starts-1)]
        labels.append(("AC","AI"))
    if n_starts+1 == n_textRegions:
        if n_starts == 0:
            labels = [("AF","AM")]
        else:
            labels = ["AF"]
            labels.extend(["AC" for _ in range(0,n_textRegions-2)])
            labels.append(("AC","AI"))

    labels_s = ""
    for x in labels:
        if type(x) == tuple:
            x = "({}/{})".format(x[0],x[1])
        labels_s += x + "-"
    #print("{} \t {} \t {} \t {}".format(img_name, n_starts, n_textRegions, labels_s))
    dif = n_textRegions - n_starts
    if dif != 0 and dif != 1:
        print("problem!")
        exit()
    res.append((img_name, n_starts, n_textRegions, labels_s))
    res_labels.append(labels)


print("A total of {} images".format(len(res)))
res_labels_updated = fit_acts(res_labels)
while act_has_tuple(res_labels_updated):
    res_labels_updated = fit_acts(res_labels_updated)
for i in range(len(res)):
    img_name, n_starts, n_textRegions, labels_s = res[i]
    labels_s = res_labels[i]
    new_label = res_labels_updated[i]

    labels_new = ""
    for x in new_label:
        if type(x) == tuple:
            x = "({}/{})".format(x[0], x[1])
        labels_new += x + "-"

    labels = ""
    for x in labels_s:
        if type(x) == tuple:
            x = "({}/{})".format(x[0], x[1])
        labels += x + "-"

    assert len(labels_s) == len(new_label)

    print("{} \t {} \t {} \t {} {:>40s}".format(img_name, n_starts, n_textRegions, labels, labels_new))
    assert len(labels_s) == n_textRegions

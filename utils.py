import glob
from page import PAGE

def get_all(path, ext="xml"):
    if path[-1] != "/":
        path = path+"/"
    file_names = glob.glob("{}*.{}".format(path,ext))
    return file_names

def get_all_acts(file):
    """
    Himanis_provisory_act-ID, 0
    Volume, 1
    Act_Nr,
    Folio_start,
    VOL_FOL_START,
    Folio_end,
    Language,
    Inventory_Name,
    Inventory_Nr,
    ImageStart_UPVLC_BVMM, 9
    ImageStart_READ
    :param file:
    :return:
    """
    f = open(file, "r")
    lines = f.readlines()[1:]
    f.close()
    res = []
    res_by_legajo = {}
    for line in lines:
        line = line.rstrip()
        s = line.split(",")
        id, volume, start_img = s[0], s[1], s[9]
        id_vol = s[2]
        fol_start, fol_end = s[3], s[5]
        start_img = start_img.split(".")[0]
        res.append((id, id_vol, volume, start_img))
        aux = res_by_legajo.get(volume, [])
        aux.append((id, id_vol, volume, fol_start, fol_end, start_img))
        res_by_legajo[volume] = aux
    return res, res_by_legajo

def search_next_img(l, name_img):
    if name_img == "END":
        return "ENDED"
    for i, img in enumerate(l):
        if img == name_img:
            try:
                return l[i+1]
            except:
                return "END"
    return "ERROR"

def get_file_order(file_order):
    f = open(file_order, "r")
    lines = f.readlines()
    f.close()
    res = []
    res_by_legajo = {}
    for line in lines:
        line = line.split(",")
        legajo_name = line[0]
        img_name = line[3].split(".")[0]
        s = img_name.split("_")
        if len(s) <= 2:
            img_name = False
        folio = line[1]
        folio_legajo = line[2]
        res.append((folio, folio_legajo, img_name))
        # if len(s) <= 2:
        #     pass
        #     # print(line)
        # else:
        aux = res_by_legajo.get(legajo_name, [])
        aux.append((folio, folio_legajo, img_name))
        res_by_legajo[legajo_name] = aux

    return res, res_by_legajo

def pags_between(a, b, order):
    count = 0
    start_count = False
    a = a.lstrip("0")
    b = b.lstrip("0")
    for folio, folio_legajo, img_name in order:
        if start_count:
            if folio == b:
                if not img_name:
                    return 0
                return count
            else:
                count += 1
        if folio == a:
            start_count = True
    # raise Exception("Error on pags between with {} and {}".format(a, b))
    return "ERROR"


def get_info(act_order, file_order, acts_page):
    imgs_order, img_order_legajo = get_file_order(file_order)
    all_acts, all_act_per_legajo = get_all_acts(act_order)

    all_volumes = list(all_act_per_legajo.keys())

    # Delete some volumes
    all_volumes = [x for x in all_volumes if len(x) == 5]

    """
    ALL first images of all volumes
    """
    vol_first_image = {}
    for volume_name in all_volumes:

        Volume = all_act_per_legajo[volume_name]
        Volume_order_img = img_order_legajo[volume_name]

        for i, _ in enumerate(Volume):
            _, _, _, _, _, first_img_with_act = Volume[i]
            if first_img_with_act != "#N/A" and len(first_img_with_act) > 10:
                break

        # print("Volume {} first_img_with_act {}".format(volume_name, first_img_with_act))
        vol_first_image[volume_name] = first_img_with_act

    return all_volumes, all_act_per_legajo, img_order_legajo, vol_first_image

def process(volume_name, act_order, file_order, acts_page):
    all_volumes, all_act_per_legajo, img_order_legajo, vol_first_image = get_info(act_order, file_order, acts_page)
    volumes_result = []
    corrects = 0
    ERROR = False

    Volume = all_act_per_legajo[volume_name]
    Volume_order_img = img_order_legajo[volume_name]

    first_img_with_act = vol_first_image[volume_name]
    while True:
        if Volume_order_img[0][2] != first_img_with_act:
            Volume_order_img.pop(0)
        else:
            break

    idx_counts = 0
    res = []

    AM_counts = 0
    id = -1
    volume = -1
    fol_start = -1
    fol_end = -1
    start_img = -1
    coords = -1
    set_AF = False
    etiq = -1
    blank = False
    n_blank_continued = 0
    MAX_n_blank_continued = 5

    for folio, folio_legajo, img_name in Volume_order_img:
        if not img_name:
            print("////////////// Folio {} is a blank page //////////////".format(folio))
            continue
        xml_page = "{}/{}.xml".format(acts_page, img_name)
        page = PAGE(xml_page)
        textRegions = page.get_textRegions()
        n_textRegions = len(textRegions)
        # if not n_textRegions:
        #     continue
        print("{} -> {}".format(xml_page, n_textRegions))
        if AM_counts > 0:
            coords = "ALL"
            etiq = "AM"
            print("{1} ----------------------------> {0}".format(etiq, img_name))
            print(id, volume, fol_start, fol_end, img_name)
            res.append((id, volume, fol_start, fol_end, img_name, coords, etiq))
            AM_counts -= 1
            # set_AF = AM_counts == 0 # not necessary
            print("*" * 20)
            n_blank_continued = 0
            continue
        if set_AF:
            set_AF = False
            etiq = "AF"
            coords, id_tr = textRegions[0]
            print("{1} ----------------------------> {0}".format(etiq, img_name))
            print(id, volume, fol_start, fol_end, img_name)
            res.append((id, volume, fol_start, fol_end, img_name, coords, etiq))
            n_textRegions -= 1
            n_blank_continued = 0
        for idx in range(idx_counts, idx_counts + n_textRegions):
            id, id_vol, volume, fol_start, fol_end, start_img = Volume[idx]
            fol_start = fol_start.lstrip("0")
            fol_end = fol_end.lstrip("0")
            print(id, volume, id_vol, fol_start, fol_end, start_img)

            if img_name != start_img:
                if etiq != "AM" and etiq != "AI":
                    blank = True
                    break
                else:
                    print("Problem near to act {}".format(id))
                    ERROR = True
                    break
                    # exit()
            if etiq == "AM" or etiq == "AI":
                print("Problem with order. etiq: {}".format(etiq))
                print("Problem near to act {}".format(id))
                ERROR = True
                break
                # exit()
            etiq = "AC"
            coords, id_tr = textRegions[idx - idx_counts]
            if fol_end and fol_end != fol_start:
                etiq = "AI"
                set_AF = True
                AM_counts = pags_between(fol_start, fol_end, Volume_order_img)
                if AM_counts == "ERROR":
                    ERROR = True
                    print("Error on pags between with {} and {}".format(fol_start, fol_end))
                    break

                print(fol_start, fol_end, AM_counts)
            start_img_name = start_img.split(".")[0]
            print("{1} ----------------------------> {0}".format(etiq, img_name))
            res.append((id, volume, fol_start, fol_end, start_img, coords, etiq))
        if ERROR:
            break
        if blank:  # blank page, jump!
            print("<<<<< {} blank page".format(img_name))
            n_blank_continued += 1
            if MAX_n_blank_continued == n_blank_continued:
                print("To many continuous blank pages ")
                ERROR = True
                break
                # exit()
            blank = False
            continue

        idx_counts += n_textRegions
        print("*" * 20)
    if ERROR:
        n_correct = max(0, len(res) - n_blank_continued)
        if n_correct < 2:
            n_correct = "0 acts -> Something happened at the beginning"
        else:
            n_correct = "near to {} valid acts".format(n_correct)
        volumes_result.append((volume_name, "ERROR", "{}".format(n_correct)))
    else:
        volumes_result.append((volume_name, "---------- ALL CORRECT -------------- Have a beer to celebrate it!"))
        corrects += 1

    return volumes_result

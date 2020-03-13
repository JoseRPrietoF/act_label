from utils import  get_info, process
import re

def print_aux(a, *args):
    print(end="")

act_order = "/data/chancery2/acts-avec-correction.csv"
acts_page = "/data/chancery2/JJ35-95_ActSegmentation20180615/"
file_order = "/data/chancery2/page2.csv"
all_volumes, all_act_per_legajo, img_order_legajo, vol_first_image = get_info(act_order, file_order, acts_page)

volumes_result = []
for volume_name in all_volumes:
    number = int(re.findall(r'\d+', volume_name)[0])
    if number >= 85:
        print("Skipping {}".format(volume_name))
        continue
    try:
        print("/////////// START WITH {} //////////".format(volume_name))
        volumes_result.extend(process(volume_name,act_order, file_order, acts_page, print=print_aux))
    except:
        print("Problem with volume {}".format(volume_name))

for v in volumes_result:
    print(v)

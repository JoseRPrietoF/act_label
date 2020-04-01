from utils import process, create_IMF_file
import sys

def print_aux(a, *args):
    print(end="")

#act_order = "/data/chancery2/Act-to-Image20200327.csv"
act_order = "/data/chancery2/acts-avec-correction_20200327.csv"
acts_page = "/data/chancery2/JJ35-95_ActSegmentation20180615/"
file_order = "/data/chancery2/Act-to-Image20200327_order.csv"


# all_volumes = ["JJ035", "JJ036", "JJ037", "JJ038", "JJ040", "JJ041", "JJ042A" JJ042B JJ044 JJ045 JJ046 JJ047 JJ048 JJ049 JJ050 JJ052 JJ053 JJ054A JJ054B JJ055 JJ056 JJ058 JJ059 JJ060 JJ061 JJ062 JJ064 JJ065A JJ065B JJ066 JJ067 JJ068 JJ069 JJ070 JJ071 JJ072 JJ073 JJ074 JJ075 JJ076 JJ077 JJ078 JJ079A JJ079B JJ080 JJ081 JJ082 JJ083 JJ084 JJ085 JJ086 JJ087 JJ088 JJ089 JJ090 JJ091 JJ092 JJ093 JJ094 JJ095 K37 K38 "Registre de Léningrad" Volume]
# all_pages = get_all(acts_page)
# print(all_pages)

# volume_name = "JJ035"
volume_name = sys.argv[1]

path_output = "/data/chancery2/labelled_volumes2/{}.mlf".format(volume_name)

try:
    volumes_result, res = process(volume_name,act_order, file_order, acts_page, print=print_aux)
    #for v in volumes_result:
    #    print(v)
except Exception as e:
    print(e)
    print("Problem with volume {}".format(volume_name))

#for i in res:
#    print(i)

create_IMF_file(res, path_output, path_xmls=acts_page)
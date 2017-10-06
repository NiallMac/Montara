import galsim
import yaml
import sys
import glob
import logging

logger=logging.Logger('galsim')

#read in config file and list of tile exposures
config_file="focal_allfiles_objcat.yaml"
source_path_file="/global/cscratch1/sd/maccrann/DES/meds/y3v02/DES0544-2249/lists/DES0544-2249_r_exp-flist-y3v02.dat"

config = galsim.config.ReadConfig(config_file, "yaml", logger)[0]

#with open(config_file, 'rb') as f:
#    config=yaml.load(f)
with open(source_path_file,'r') as f:
    lines=f.readlines()
    input_exps=[]
    for l in lines:
        input_exps.append((l.strip()).split())



#call galsim for each exposure, updating the input exposure as we go
for e in input_exps:
    print e
    print config
    config['input']['all_files']['dir']=e[0]
    config['input']['all_files']['files']=e[1]
    galsim.config.Process(config)





#------------------------------------------------------------------------------
# Function: clear item without any object
# Author: yanggang
#------------------------------------------------------------------------------
import dota_utils as util
import os

def clear(txtpath):
    filelist = util.GetFileFromThisRootDir(txtpath)
    for file in filelist:
        objs = util.parse_dota_poly(file)
        if len(objs) == 0:
            image = file.replace('labelTxt-v1.0', 'images').replace('.txt','.png')
            print(image + ',' + file)
            os.remove(image)
            os.remove(file)
    print("complete!")


if __name__ == '__main__':
    clear('E:/data/DOTA_SPLIT_1024_SingleScale/val/labelTxt-v1.0')
import dota_utils as util
import os
import cv2
import xml
from xml.dom.minidom import parse

def readset(img_set):
    train_set = os.path.join(img_set, 'train.txt')
    val_set = os.path.join(img_set, 'val.txt')
    train_files, val_files = [],[]
    with open(train_set, 'r') as f:
        lines = f.read().split('\n')
        for line in lines:
            train_files.append(line)
    with open(val_set, 'r') as f:
        lines = f.read().split('\n')
        for line in lines:
            val_files.append(line)

    return train_files, val_files

def getItemname(file):
    return file.split(os.sep)[-1].split('.')[0]

def parse_dior(img_path, label_path):
    image = cv2.imread(img_path)
    label= parse(label_path)
    name = getItemname(label_path)
    objects = label.getElementsByTagName('object')
    results = []
    for object in objects:
        boundingbox = object.getElementsByTagName('robndbox')[0]
        x_left_top = boundingbox.getElementsByTagName('x_left_top')[0].childNodes[0].data
        y_left_top = boundingbox.getElementsByTagName('y_left_top')[0].childNodes[0].data
        x_right_top = boundingbox.getElementsByTagName('x_right_top')[0].childNodes[0].data
        y_right_top = boundingbox.getElementsByTagName('y_right_top')[0].childNodes[0].data
        x_right_bottom = boundingbox.getElementsByTagName('x_right_bottom')[0].childNodes[0].data
        y_right_bottom = boundingbox.getElementsByTagName('y_right_bottom')[0].childNodes[0].data
        x_left_bottom = boundingbox.getElementsByTagName('x_left_bottom')[0].childNodes[0].data
        y_left_bottom = boundingbox.getElementsByTagName('y_left_bottom')[0].childNodes[0].data
        difficult = object.getElementsByTagName('difficult')[0].childNodes[0].data
        category = object.getElementsByTagName('name')[0].childNodes[0].data
        pt1, pt2, pt3, pt4 = (int(x_left_top), int(y_left_top)), \
                             (int(x_right_top), int(y_right_top)),\
                             (int(x_right_bottom),int(y_right_bottom)),\
                             (int(x_left_bottom), int(y_left_bottom))
        pts = [pt1, pt2, pt3, pt4]
        result = {
            'category' : category,
            'boundingbox':pts,
            'difficult': difficult
        }
        results.append(result)
    return image, results, name

def writeAsDOTA(img, labels, save_path, name):
    img_save_dir = os.path.join(save_path, 'images')
    label_save_dir = os.path.join(save_path, 'labelTxt')
    if not os.path.exists(img_save_dir):
        os.mkdir(img_save_dir)
    if not os.path.exists(label_save_dir):
        os.mkdir(label_save_dir)
    cv2.imwrite(os.path.join(img_save_dir , name+'.jpg'),img)
    with open(os.path.join(label_save_dir, name+'.txt'), "w") as f:
        f.write("imagesource:DIOR-R\n")
        f.write("gsd:Unknown\n")
        for object in labels:
            pt1, pt2,pt3, pt4 = object['boundingbox'][0],object['boundingbox'][1],object['boundingbox'][2],object['boundingbox'][3]
            category = object['category']
            difficult = object['difficult']
            line = f'{str(pt1[0])} {str(pt1[1])} {str(pt2[0])} {str(pt2[1])} {str(pt3[0])} {str(pt3[1])} {str(pt4[0])} {str(pt4[1])} {category} {difficult}'
            f.write(line+'\n')

def main(root, save_dir):
    trainval_imgs_dir = root + "/JPEGImages-trainval"
    test_imgs_dir = root + "/JPEGImages-test"
    imgset_dir = root + "/Main"

    trainval_imgs = util.GetFileFromThisRootDir(trainval_imgs_dir)
    trainval_labels = [x.replace('JPEGImages-trainval', 'Annotations/Oriented Bounding Boxes').replace('.jpg', '.xml')
                       for x in trainval_imgs]
    train_files, val_files = readset(imgset_dir)
    for (img_file, label_file) in zip(trainval_imgs, trainval_labels):
        image, label, name = parse_dior(img_file, label_file)
        assert image is not None
        if name in train_files:
            setmode = 'train'
        elif name in val_files:
            setmode = 'val'
        else:
            setmode = 'test'
        writeAsDOTA(image, label, save_path=os.path.join(save_dir, setmode), name=name)
    test_imgs = util.GetFileFromThisRootDir(test_imgs_dir)
    test_labels = [x.replace('JPEGImages-test', '/Annotations/Oriented Bounding Boxes').replace('.jpg', '.xml') for x in
                   test_imgs]
    for (img_file, label_file) in zip(test_imgs, test_labels):
        image, label, name = parse_dior(img_file, label_file)
        writeAsDOTA(image, label, save_path=os.path.join(save_dir,"test"), name=name)

if __name__ == '__main__':
    root = "D:/data/DIOR"
    save_dir = "D:/data/DIOR_DOTA"
    main(root, save_dir)

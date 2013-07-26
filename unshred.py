#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image
from math import sqrt, pow

NUM = 20

image = Image.open("1.png")

unshredded = Image.new("RGBA", image.size)

width, height = image.size

shred_width = width / NUM

SPLIT_NUM = 359

edge_width = 2

def count_euclidean_distance(src_vec, target_vec):
    """
    multiple vector euclidean distance
    """
    dis = 0.0

    assert len(src_vec) == len(target_vec)
    
    dis_sum = sum([pow(item[0] - item[1], 2) for item in zip(src_vec, target_vec)])
    dis = sqrt(dis_sum)

    return dis

def count_similar_degree(dis):
    """
    count similar degree from euclidean distance
    the bigger, the more similar
    """
    sim_degree = 1 / (dis + 1)
    return sim_degree

#####################
def split_image(img, part_size=(edge_width, height / SPLIT_NUM)):
    """
    return img obj list, split image to pieces
    """
    w, h = img.size
    pw, ph = part_size

    return [img.crop((i, j, i + pw, j + ph)).copy() for i in xrange(0, w, pw) for j in xrange(0, h, ph)]

def create_shred_arr(num, origin_img):
    """
    init shred piece image to array 
    """
    shred_arr = []
    
    for i in range(num):
        x1, y1 = shred_width * i, 0
        x2, y2 = x1 + shred_width, height
        box = (x1, y1, x2, y2)
        region = origin_img.crop(box)
        #region.show()
        shred_arr.append(region)

    return shred_arr

def get_both_side_edge(img):
    """
    return both edge side of a img
    """
    box_edge_left = (0, 0, edge_width, height)
    box_edge_right = (shred_width - edge_width, 0, shred_width, height)
    left_edge = img.crop(box_edge_left)
    right_edge = img.crop(box_edge_right)
    return left_edge, right_edge

def get_pixel_vector(img):
    """
    return a vector of all pixel RGBA info of an image
    """
    data = img.getdata()
    # just fetch RGB value, and not need alpha value
    return [item for RGBA in data for item in RGBA[:3]]

def cacl_similar(src_img, target_img):
    """
    count similar degree with euclidean distance
    """
    src_vec = [get_pixel_vector(piece) for piece in split_image(src_img)]
    target_vec = [get_pixel_vector(piece) for piece in split_image(target_img)]

    eu_dic = sum([count_euclidean_distance(item[0], item[1]) for item in zip(src_vec, target_vec)]) / SPLIT_NUM
    return count_similar_degree(eu_dic)
    
def unshred(shred_arr):
    """
    do core recovery algorithm
    """

    unshred_arr = []
    num = len(shred_arr)
    
    for i in range(num):
        temp_dict = {}
        temp_dict['img'] = shred_arr[i]
        temp_dict['root'] = i
        temp_dict['left'] = -1
        temp_dict['right'] = -1
        temp_dict['max_left_sim_degree'] = -1
        temp_dict['max_right_sim_degree'] = -1

        src_left_edge, src_right_edge = get_both_side_edge(temp_dict['img'])
        
        for j in range(num):
            if i != j:
                target_left_edge, target_right_edge = get_both_side_edge(shred_arr[j])

                left_sim_degree = cacl_similar(src_left_edge, target_right_edge)
                right_sim_degree = cacl_similar(src_right_edge, target_left_edge)
                
                if left_sim_degree > temp_dict['max_left_sim_degree'] and j != temp_dict['right']:
                    temp_dict['max_left_sim_degree'] = left_sim_degree
                    temp_dict['left'] = j

                if right_sim_degree > temp_dict['max_right_sim_degree'] and j != temp_dict['left']:
                    temp_dict['max_right_sim_degree'] = right_sim_degree
                    temp_dict['right'] = j

        unshred_arr.append(temp_dict)

    # find the smallest one, and set to it to edge piece
    unshred_arr = sorted(unshred_arr, key=lambda x:x['max_left_sim_degree'])
    unshred_arr[0]['left'] = -1
    unshred_arr = sorted(unshred_arr, key=lambda x:x['max_right_sim_degree'])
    unshred_arr[0]['right'] = -1

    # sort unsort dict array
    # find the left most -1, and start it to finish the chain
    sorted_arr = []    
    for item in unshred_arr:
        if item['left'] == -1:
            sorted_arr.append(item['img'])
            
    return unshred_arr

def create_new_image(raw_pieces, target, file_name):
    for i, item in enumerate(raw_pieces):
        target.paste(item, (shredded_width * i, 0))
    target.save(file_name)

if __name__ == '__main__':
    shred_arr = create_shred_arr(NUM, image)
    unshred_arr = unshred(shred_arr)
    print min([item['max_left_sim_degree'] for item in unshred_arr])
    print min([item['max_right_sim_degree'] for item in unshred_arr])
    print [(item['left'], item['root'], item['right']) for item in unshred_arr]
    #print [((item['left'], item['max_left_sim_degree']), item['root'], (item['right'], item['max_right_sim_degree'])) for item in unshred_arr]

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image
from math import sqrt, pow

# number of shredded pieces in the original image 
NUM = 20

image = Image.open("1.png")

# image object of final unshredded image 
unshredded = Image.new("RGBA", image.size)

# width and height of origin image 
width, height = image.size

# the whole width of regular 
shred_width = width / NUM

# width of edge piece use to compare
edge_width = 1

#############################
## Euclidean Distance Detect
############################

def count_euclidean_distance(src_vec, target_vec):
    """
    count multiple vector euclidean distance and get the average value of them
    to make the result more reliable(maybe)
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

def cacl_similar(src_img, target_img):
    """
    count similar degree with euclidean distance
    """
    src_pixels = src_img.getdata()
    target_pixels = target_img.getdata()

    eu_dic = 0
    for i in range(height):
        eu_dic += count_euclidean_distance(src_pixels[i], target_pixels[i])
    eu_dic = eu_dic / height
    
    return count_similar_degree(eu_dic)

def cacl_similar_1(src_img, target_img):
    """
    count similar degree with euclidean distance
    """
    src_vec = [item for pixel in src_img.getdata() for item in pixel]
    target_vec = [item for pixel in target_img.getdata() for item in pixel]

    eu_dic = count_euclidean_distance(src_vec, target_vec)
    
    return count_similar_degree(eu_dic)

def unshred(shred_arr, cacl_similar_func):
    """
    do core recovery algorithm
    """

    unshred_arr = []
    num = len(shred_arr)
    
    for i in range(num):
        temp_dict = {}
        temp_dict['img'] = shred_arr[i]
        temp_dict['root'] = i
        temp_dict['right'] = -1
        temp_dict['left'] = -1
        temp_dict['max_right_sim_degree'] = -1
        temp_dict['max_left_sim_degree'] = -1

        src_left_edeg, src_right_edge = get_both_side_edge(temp_dict['img'])
        
        for j in range(num):
            target_left_edge, target_right_edge = get_both_side_edge(shred_arr[j])
            right_sim_degree = cacl_similar_func(src_right_edge, target_left_edge)
            left_sim_degree = cacl_similar_func(src_left_edeg, target_right_edge)
            if right_sim_degree > temp_dict['max_right_sim_degree']:
                temp_dict['max_right_sim_degree'] = right_sim_degree
                temp_dict['right'] = j
            if left_sim_degree > temp_dict['max_left_sim_degree']:
                temp_dict['max_left_sim_degree'] = left_sim_degree
                temp_dict['left'] = j                

        unshred_arr.append(temp_dict)

    # find the first pic from left side
    nexts = [item['right'] for item in  unshred_arr]

    first_left = -1
    for i in range(num):
        if i not in nexts:
            first_left = i

    # build ordered unshred_arr from left side
    ordered_arr = [unshred_arr[first_left]]

    for _ in range(num - 1):
       ordered_arr.append(unshred_arr[ordered_arr[-1]['right']]) 

    return [item['img'] for item in ordered_arr]

######################
##
## common util method
######################
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

def create_unshred_img(unshred_img, unshred_arr, file_name):
    """
    create unshred image from unshred_arr
    """
    for i, img in enumerate(unshred_arr):
        paste_position = (i * shred_width, 0)
        unshred_img.paste(img, paste_position)
        
    unshred_img.save(file_name)
    
if __name__ == '__main__':
    image.show()
    shred_arr = create_shred_arr(NUM, image)
    unshred_arr = unshred(shred_arr, cacl_similar)
    file_name = "unshredded_img.png"
    create_unshred_img(unshredded, unshred_arr, file_name)
    unshredded.show()
    print "create %s successfully!!" % file_name

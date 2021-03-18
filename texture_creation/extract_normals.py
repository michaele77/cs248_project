# -----------------------------------------------------------------------------#
#                                IMPORTS                                       #
# -----------------------------------------------------------------------------#
import numpy as np
from colorutils import Color
import math
from PIL import Image
from PIL import ImageFilter


# -----------------------------------------------------------------------------#
#                                 DEFINES                                      #
# -----------------------------------------------------------------------------#


# -----------------------------------------------------------------------------#
#                                 CLASSES                                      #
# -----------------------------------------------------------------------------#



# -----------------------------------------------------------------------------#
#                                FUNCTIONS                                     #
# -----------------------------------------------------------------------------#




# -----------------------------------------------------------------------------#
#                                   MAIN                                       #
# -----------------------------------------------------------------------------#
if __name__ == "__main__":

    normal_img = Image.open("Quartz_001_NORM.png")
    normal_arr = np.array(normal_img, dtype=np.float)
    normal_arr = normal_arr[:, :, 0:3]  # cut out alpha channel
    px,py,dd = normal_arr.shape
    avg_val = normal_arr.sum(axis=0)/px
    avg_val = avg_val.sum(axis=0)/py
    print("Quartz normal average:")
    print(avg_val)

    normal_img = Image.open("Red_Marble_001_NRM.png")
    normal_arr = np.array(normal_img, dtype=np.float)
    normal_arr = normal_arr[:, :, 0:3]  # cut out alpha channel
    px, py, dd = normal_arr.shape
    avg_val = normal_arr.sum(axis=0) / px
    avg_val = avg_val.sum(axis=0) / py
    print("Red Marble normal average:")
    print(avg_val)

    normal_img = Image.open("Stone_Tiles_003_NORM.png")
    normal_arr = np.array(normal_img, dtype=np.float)
    normal_arr = normal_arr[:, :, 0:3]  # cut out alpha channel
    px, py, dd = normal_arr.shape
    avg_val = normal_arr.sum(axis=0) / px
    avg_val = avg_val.sum(axis=0) / py
    print("Stone Tile normal average:")
    print(avg_val)





    ## Based on a normal image, we will create a texture map off of it
    normal_img = Image.open("human_skin_1.png")


    normal_arr = np.array(normal_img, dtype=np.float)
    normal_arr = normal_arr[:,:,0:3] # cut out alpha channel

    px,py,dd = normal_arr.shape
    avg_val = normal_arr.sum(axis=0)/px
    avg_val = avg_val.sum(axis=0)/py

    print(avg_val)

    subract_arr = np.array([127,127,253])
    out_normal_arr = 128*np.ones((px,py,dd), dtype=np.uint8)

    for i in range(px):
        for j in range(py):
            out_normal_arr[i,j,:] = subract_arr + (normal_arr[i,j,:] - avg_val)



    px, py, dd = out_normal_arr.shape
    avg_val = out_normal_arr.sum(axis=0) / px
    avg_val = avg_val.sum(axis=0) / py
    print("final output avg:")
    print(avg_val)
    out_normal = Image.fromarray(out_normal_arr)
    out_normal.save("new_normal.png")




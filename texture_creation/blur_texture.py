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
    ## Upsampling this will inadvertantly blur the output image, so avoid doing that
    ## Gaussian blur seems a bit extreme
    ## Custom window slider is...


    im = Image.open("machined_0.png")
    test_im = Image.open("Blue_Marble_002_NORM.png")

    test_im = Image.fromarray(np.array(test_im)- 50)
    # im_arr = np.array(im, dtype = np.float)
    #
    # window_avg = 2 ## MAKE SURE THIS IS EVEN
    # e_sd = round(window_avg/2)
    # input_shape_tuple = im_arr.shape
    # input_shape = np.array([0,0,3])
    # input_shape[0] = input_shape_tuple[0] - window_avg + 1
    # input_shape[1] = input_shape_tuple[1] - window_avg + 1
    # out_img = np.zeros(input_shape, dtype = np.uint8)
    #
    # for i in range(input_shape[0]):
    #     for j in range(input_shape[1]):
    #         out_img[i,j,0] = sum(sum(im_arr[i:i+window_avg, j:j+window_avg, 0])) / (window_avg**2)
    #         out_img[i,j,1] = sum(sum(im_arr[i:i + window_avg, j:j + window_avg, 1])) / (window_avg ** 2)
    #         out_img[i,j,2] = sum(sum(im_arr[i:i + window_avg, j:j + window_avg, 2])) / (window_avg ** 2)

    out_im = im.filter(ImageFilter.GaussianBlur(radius=1))


    # new_size = (1000,1000)
    # out_im = im.resize(new_size)
    # out_im = Image.fromarray(out_img)
    out_im.save("blurred_texture.png")

    test_im.save("new_text.png")



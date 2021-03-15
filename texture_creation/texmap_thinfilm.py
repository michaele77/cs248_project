# -----------------------------------------------------------------------------#
#                                IMPORTS                                       #
# -----------------------------------------------------------------------------#
import numpy as np
from colorutils import Color
import math
from PIL import Image
import matplotlib.pyplot as plt
import colour

# -----------------------------------------------------------------------------#
#                                 DEFINES                                      #
# -----------------------------------------------------------------------------#
## 380nm to 780nm every 5nm
CIE_wavlen = np.linspace(380e-9, 780e-9, 81)
CIE_color_match = np.array([ [0.0014,0.0000,0.0065], [0.0022,0.0001,0.0105], [0.0042,0.0001,0.0201], \
                             [0.0076,0.0002,0.0362], [0.0143,0.0004,0.0679], [0.0232,0.0006,0.1102], \
                             [0.0435,0.0012,0.2074], [0.0776,0.0022,0.3713], [0.1344,0.0040,0.6456], \
                             [0.2148,0.0073,1.0391], [0.2839,0.0116,1.3856], [0.3285,0.0168,1.6230], \
                             [0.3483,0.0230,1.7471], [0.3481,0.0298,1.7826], [0.3362,0.0380,1.7721], \
                             [0.3187,0.0480,1.7441], [0.2908,0.0600,1.6692], [0.2511,0.0739,1.5281], \
                             [0.1954,0.0910,1.2876], [0.1421,0.1126,1.0419], [0.0956,0.1390,0.8130], \
                             [0.0580,0.1693,0.6162], [0.0320,0.2080,0.4652], [0.0147,0.2586,0.3533], \
                             [0.0049,0.3230,0.2720], [0.0024,0.4073,0.2123], [0.0093,0.5030,0.1582], \
                             [0.0291,0.6082,0.1117], [0.0633,0.7100,0.0782], [0.1096,0.7932,0.0573], \
                             [0.1655,0.8620,0.0422], [0.2257,0.9149,0.0298], [0.2904,0.9540,0.0203], \
                             [0.3597,0.9803,0.0134], [0.4334,0.9950,0.0087], [0.5121,1.0000,0.0057], \
                             [0.5945,0.9950,0.0039], [0.6784,0.9786,0.0027], [0.7621,0.9520,0.0021], \
                             [0.8425,0.9154,0.0018], [0.9163,0.8700,0.0017], [0.9786,0.8163,0.0014], \
                             [1.0263,0.7570,0.0011], [1.0567,0.6949,0.0010], [1.0622,0.6310,0.0008], \
                             [1.0456,0.5668,0.0006], [1.0026,0.5030,0.0003], [0.9384,0.4412,0.0002], \
                             [0.8544,0.3810,0.0002], [0.7514,0.3210,0.0001], [0.6424,0.2650,0.0000], \
                             [0.5419,0.2170,0.0000], [0.4479,0.1750,0.0000], [0.3608,0.1382,0.0000], \
                             [0.2835,0.1070,0.0000], [0.2187,0.0816,0.0000], [0.1649,0.0610,0.0000], \
                             [0.1212,0.0446,0.0000], [0.0874,0.0320,0.0000], [0.0636,0.0232,0.0000], \
                             [0.0468,0.0170,0.0000], [0.0329,0.0119,0.0000], [0.0227,0.0082,0.0000], \
                             [0.0158,0.0057,0.0000], [0.0114,0.0041,0.0000], [0.0081,0.0029,0.0000], \
                             [0.0058,0.0021,0.0000], [0.0041,0.0015,0.0000], [0.0029,0.0010,0.0000], \
                             [0.0020,0.0007,0.0000], [0.0014,0.0005,0.0000], [0.0010,0.0004,0.0000], \
                             [0.0007,0.0002,0.0000], [0.0005,0.0002,0.0000], [0.0003,0.0001,0.0000], \
                             [0.0002,0.0001,0.0000], [0.0002,0.0001,0.0000], [0.0001,0.0000,0.0000], \
                             [0.0001,0.0000,0.0000], [0.0001,0.0000,0.0000], [0.0000,0.0000,0.0000], \
])


# -----------------------------------------------------------------------------#
#                                 CLASSES                                      #
# -----------------------------------------------------------------------------#

class Ray:
    def __init__(self, vec_origin, vec_dir, light_color):
        self.d = vec_dir # This should be a tuple
        self.o = vec_origin
        self.color = light_color



# -----------------------------------------------------------------------------#
#                                FUNCTIONS                                     #
# -----------------------------------------------------------------------------#
def sample_CIE_color(spectrum_idx, input_spectrum):
    t_x = []
    t_y = []
    t_z = []

    CIE_x = [i[0] for i in CIE_color_match]
    CIE_y = [i[1] for i in CIE_color_match]
    CIE_z = [i[2] for i in CIE_color_match]
    cut_input_spectrum = []
    for i, cur_wavlen in enumerate(spectrum_idx):
        if cur_wavlen < 380e-9 or cur_wavlen > 780e-9:
            continue

        cut_input_spectrum.append(input_spectrum[i])
        bot_i = math.floor( (cur_wavlen - (380e-9)) / (5e-9) )
        del_x = cur_wavlen - spectrum_idx[bot_i]

        t_x.append( CIE_x[bot_i] +  (CIE_x[bot_i+1]-CIE_x[bot_i])*del_x )
        t_y.append( CIE_y[bot_i] +  (CIE_y[bot_i+1]-CIE_y[bot_i])*del_x )
        t_z.append( CIE_z[bot_i] +  (CIE_z[bot_i+1]-CIE_z[bot_i])*del_x )

    mean_x = sum( [t_x[jj]*cut_input_spectrum[jj] for jj in range(len(t_x))] ) / len(t_x)
    mean_y = sum( [t_y[jj]*cut_input_spectrum[jj] for jj in range(len(t_y))] ) / len(t_y)
    mean_z = sum( [t_z[jj]*cut_input_spectrum[jj] for jj in range(len(t_z))] ) / len(t_z)

    ## X,Y,Z follow property that X + Y + Z = 1
    XYZ = mean_x + mean_y + mean_z
    X = mean_x/XYZ
    Y = mean_y/XYZ
    Z = mean_z/XYZ


    return X,Y,Z


def convert_to_rgb(fx,fy,fz):
    ## Using Apple RGB standard from here: http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    M_inv = np.array([ [2.0413690, -0.5649464, -0.3446944], \
                       [-0.9692660, 1.8760108, 0.0415560],
                       [0.0134474, -0.1183897, 1.0154096] ])
    xyz_vec = np.array([fx, fy, fz])

    rgb_vec = np.matmul(M_inv, xyz_vec)
    return rgb_vec



# -----------------------------------------------------------------------------#
#                                   MAIN                                       #
# -----------------------------------------------------------------------------#
if __name__ == "__main__":
    R_list = []
    T_list = []
    for i in range(90):

        ## SIMULATION PARAMETERS ##
        n_1 = 1 # Assume to be air
        n_2 = 1.3 # Assume to be an oil of some sort
        d = 500e-9 # in meters
        th_i = math.radians(i)
        th_r = th_i
        th_t = math.asin( n_1*math.sin(th_i)/n_2 )
        Z0 = 376.7303 # constant
        z_1 = Z0 / n_1
        z_2 = Z0 / n_2
        R_s = ( ((z_2 * math.cos(th_i) - z_1 * math.cos(th_t)) / (z_2 * math.cos(th_i) + z_1 * math.cos(th_t))) ) ** 2
        R_p = ( ((z_2 * math.cos(th_t) - z_1 * math.cos(th_i)) / (z_2 * math.cos(th_t) + z_1 * math.cos(th_i))) ) ** 2
        R = 0.5 * (R_s + R_p)
        T = 1 - R
        R_list.append(R)
        T_list.append(T)

    print(R)
    print(T)


    ## PHYSICAL PARAMETERS ##
    n_1 = 1  # Assume to be air
    n_2 = 1.3  # Assume to be an oil of some sort
    reflected_1_2 = n_2 > n_1 # IF n_2 > n_1, directly reflected power has a 180 degree phase shift
    n_3 = 1.5 # Used ony as base condition, enforces pi shift off base
    reflected_2_3 = n_3 > n_2
    d = 200e-9  # in meters
    th_i = math.radians(30)
    th_r = th_i
    th_t = math.asin(n_1 * math.sin(th_i) / n_2)
    OPD = 2 * n_2 * d * math.cos(th_t) # Optical path difference, phase shift due to longer transmitted path
    Z0 = 376.7303  # constant
    ## Calculate reflectance/transmission going 1 --> 2
    z_1 = Z0 / n_1
    z_2 = Z0 / n_2
    R_s = ((z_2 * math.cos(th_i) - z_1 * math.cos(th_t)) / (z_2 * math.cos(th_i) + z_1 * math.cos(th_t))) ** 2
    R_p = ((z_2 * math.cos(th_t) - z_1 * math.cos(th_i)) / (z_2 * math.cos(th_t) + z_1 * math.cos(th_i))) ** 2
    R = 0.5 * (R_s + R_p)
    T = 1 - R
    ## Calculate reflectance/transmission going 2 --> 1
    z_1 = Z0 / n_2
    z_2 = Z0 / n_1
    Ru_s = ((z_2 * math.cos(th_t) - z_1 * math.cos(th_i)) / (z_2 * math.cos(th_t) + z_1 * math.cos(th_i))) ** 2
    Ru_p = ((z_2 * math.cos(th_i) - z_1 * math.cos(th_t)) / (z_2 * math.cos(th_i) + z_1 * math.cos(th_t))) ** 2
    Ru = 0.5 * (Ru_s + Ru_p)
    Tu = 1 - Ru
    ## Quick and dirty perfect base reflector assumption
    R_base = 1
    T_base = 0

    ## SIMULATION PARAMETERS ##
    num_inter_refl = 3








    spectrum_num = 1000
    wavlen_min = 300e-9 # in meters
    wavlen_max = 800e-9 # in meters

    specturm_wavlen = np.linspace(wavlen_min, wavlen_max, spectrum_num)
    master_spectrum = np.ones(spectrum_num) # This is the incident spectrum can define to something else later!


    ## Plot some stuff first
    plt.figure()
    plt.plot([i for i in range(90)], R_list)
    plt.plot([i for i in range(90)], T_list)
    plt.legend(['reflectance', 'transmission'])
    plt.show()

    plt.figure()
    plt.plot(specturm_wavlen, master_spectrum)
    plt.show()




    ## We compute inter_refl number of reflections
    ## We define 1 inter_refl as a transmission at the surface, reflection at the base, and
    ## ESSSENTIALLY, num_inter_refl is how many additional outgoing reflections we want AFTER the first!
    ##      So num_inter_refl = 2 will result in 3 total reflections to be summed
    output_spectrum = np.zeros(spectrum_num, dtype=np.complex128) # Allocate our output spectrum
    for indx,i in enumerate(master_spectrum):
        output_spectrum[indx] = i

    for i, cur_wavlen in enumerate(specturm_wavlen):
        OPD_phase = 2*math.pi*(OPD / cur_wavlen)
        in_pow = master_spectrum[i]
        outgoing_refl = []
        outgoing_shift = []
        outgoing_complex = []

        reflected = R * in_pow
        refl_phase = math.pi if reflected_1_2 else 0


        outgoing_refl.append(reflected)
        outgoing_shift.append(refl_phase)
        outgoing_complex.append(reflected * np.exp(refl_phase*1j))

        transmitted = T * in_pow
        trans_phase = 0

        next_pow = transmitted
        next_phase = trans_phase
        for k in range(num_inter_refl):
            ## TODO: Verify this:
            ## We assume that all light is reflected off of base material
            ## If this is no longer a valid assumption, modify 2 lines below
            cur_pow = R_base * next_pow
            cur_phase = next_phase + OPD_phase
            cur_phase = cur_phase + math.pi if reflected_2_3 else cur_phase

            reflected = Ru * cur_pow
            refl_phase = cur_phase + math.pi if not reflected_1_2 else cur_phase
            transmitted = Tu * cur_pow
            trans_phase = cur_phase

            outgoing_refl.append(transmitted)
            outgoing_shift.append(trans_phase)
            outgoing_complex.append(transmitted * np.exp(trans_phase * 1j))

            next_pow = reflected
            next_phase = refl_phase

        for iter_outgoing in outgoing_complex:
            output_spectrum[i] += iter_outgoing

    ## take magnitude and normalize output spectrum
    spectrum_norm_mag = abs(output_spectrum) / 2 # Divide by 2 to take into account potential full reflection

    plt.figure()
    plt.plot(specturm_wavlen, spectrum_norm_mag)
    plt.show()

    x,y,z = sample_CIE_color(specturm_wavlen, spectrum_norm_mag)
    r,g,b = convert_to_rgb(x,y,z)

    print(x)
    print(y)
    print(z)

    print(r)
    print(g)
    print(b)


    pass









# -----------------------------------------------------------------------------#
#                                IMPORTS                                       #
# -----------------------------------------------------------------------------#
import numpy as np
from colorutils import Color
import math
from PIL import Image


# -----------------------------------------------------------------------------#
#                                 DEFINES                                      #
# -----------------------------------------------------------------------------#
global accum
accum = 0

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

## Helper for intersection function
## Returns true if inside our box
def bounding_check(val):
    return val[0] >= -W/2 and val[0] <= W/2 and val[1] <= H and val[1] >= 0

def compute_box_intersection(r):
    t = 0
    pos = r.o
    while bounding_check(pos):
        t += t_iter
        pos = r.o + t*r.d

    ## Check if we got "outside" ie intersect with top lid
    if pos[1] <= 0:
        return 0, np.array([0,0])
    elif pos[0] <= -W/2:
        return 1, np.array([-W/2, pos[1]])
    elif pos[1] >= H:
        return 2, np.array([pos[0], H])
    elif pos[0] >= W/2:
        return 3, np.array([W/2, pos[1]])

## This computes the diffuse BRDF on the inside of the box
## For debugging, can at first set to a perfect reflection
## TODO: make this an actually diffuse BRDF reflection
def pure_reflection(side_hit, og_pt, input_ray):
    input_dir = input_ray.d
    ## Don't need fancy bisecting angles here, just reverse whatever axis is orthogonal to the wall
    if side_hit == 1:
        reflec_dir = np.array( [-input_dir[0],input_dir[1]] )
    elif side_hit == 2:
        reflec_dir = np.array( [input_dir[0],-input_dir[1]] )
    elif side_hit == 3:
        reflec_dir = np.array( [-input_dir[0],input_dir[1]] )

    reflec_ray = Ray(og_pt, reflec_dir, input_ray.color)

    ## We actually "hit" the wall here, so pass on an updated color here
    reflec_ray.color = input_ray.color + polluting_color

    return [reflec_ray]

## Here we create N = branching_rays of splits based on diffusion equation
## Diffusion equation we use will be (1-cos(x+offset))/2, where offset is 0 to pi based on where we want diffusion pointed tp
## If incident angle is theta, reflected angle = beta = 180 - theta, and offset = 180 - beta = theta
## Based on the output of diffusion eqaution (already normalized to 1), add that fraction of polluting color
def diffuse_reflection_original(side_hit, og_pt, input_ray):
    input_dir = input_ray.d
    temp_bisect = math.degrees(math.atan(abs(input_dir[1]) / abs(input_dir[0])))

    ## Need to compute ideal reflection for offset and incident angle based on wall
    if side_hit == 1:
        reflec_dir = np.array( [-input_dir[0],input_dir[1]] )
        incid_ang = 90-temp_bisect
    elif side_hit == 2:
        reflec_dir = np.array( [input_dir[0],-input_dir[1]] )
        incid_ang = temp_bisect
    elif side_hit == 3:
        reflec_dir = np.array( [-input_dir[0],input_dir[1]] )
        incid_ang = 90 - temp_bisect

    # func_samp = np.linspace(0,math.radians(180),1000)
    rad_incid_ang = math.radians(incid_ang)
    # R_samp = (1 - np.cos(func_samp + rad_incid_ang)) / 2

    reflected_rays = []
    max_mag = (1 - np.cos(rad_incid_ang + rad_incid_ang))
    min_mag = min((1 - np.cos(0 + rad_incid_ang)), (1 - np.cos(math.radians(180) + rad_incid_ang)))
    for i, cur_branch_ang in enumerate(branch_dir_arr):
        ## Have already pre-computed branching angle samples
        ## Determine which sample corresponds to our angle
        # idx = (np.abs(func_samp - math.radians(cur_branch_ang))).argmin()
        # polar_mag = R_samp[idx]

        polar_mag = (1 - np.cos(math.radians(cur_branch_ang) + rad_incid_ang))
        polar_mag = (polar_mag - min_mag) / (max_mag - min_mag) # Normalize magnitude to be 0 to 1

        ## Now compute reflected direction
        tru_x = math.cos(math.radians(cur_branch_ang))
        tru_y = math.sin(math.radians(cur_branch_ang))
        if side_hit == 1:
            cur_refl_dir = np.array([tru_y,tru_x])
        elif side_hit == 2:
            cur_refl_dir = np.array([tru_x,tru_y])
        elif side_hit == 3:
            cur_refl_dir = np.array([-tru_y,-tru_x])


        cur_refl_ray = Ray(og_pt, cur_refl_dir, input_ray.color)
        cur_refl_ray.color = input_ray.color + polluting_color * polar_mag
        reflected_rays.append(cur_refl_ray)


    return reflected_rays

## Helper function that helps to construct a denser sampling rate around the focal angle of interest
def construct_branches(focal_ang):
    ## We will march away from the angle at increasing interval until we run out of branches
    sampled_angles = [focal_ang]
    step_track = 1
    incr_deg = 1
    while step_track < branching_rays:
        prefix_ang = sampled_angles[0] - incr_deg
        suffix_ang = sampled_angles[-1] + incr_deg
        incr_deg = math.ceil(incr_deg * 1.1) ## 1.6 and above lead to some weirdness...



        if prefix_ang >= 0 and suffix_ang <= 180:
            sampled_angles.insert(0,prefix_ang)
            sampled_angles.append(suffix_ang)
            step_track += 2
        elif prefix_ang >= 0:
            sampled_angles.insert(0, prefix_ang)
            step_track += 1
        elif suffix_ang <= 180:
            sampled_angles.append(suffix_ang)
            step_track += 1

        if prefix_ang < 0 and suffix_ang > 180:
            print("Focal spread too large, revisit construct_branches function!")
            return sampled_angles
    return sampled_angles






def diffuse_reflection(side_hit, og_pt, input_ray):
    input_dir = input_ray.d
    # temp_bisect = math.degrees(math.atan(abs(input_dir[1]) / abs(input_dir[0])))

    ## Need to compute ideal reflection for offset and incident angle based on wall
    if side_hit == 1:
        wall_vector = np.array([0,-1]) ## REMEMBER: REVERSE ANGLE
    elif side_hit == 2:
        wall_vector = np.array([-1, 0])
    elif side_hit == 3:
        wall_vector = np.array([0, 1])

    rev_wall_vec = -wall_vector
    incid_ang = math.degrees(np.arccos(np.dot(wall_vector, input_dir)))

    # func_samp = np.linspace(0,math.radians(180),1000)
    rad_incid_ang = math.radians(incid_ang)
    # R_samp = (1 - np.cos(func_samp + rad_incid_ang)) / 2

    reflected_rays = []
    max_mag = (1 - np.cos(rad_incid_ang + rad_incid_ang))
    min_mag = min((1 - np.cos(0 + rad_incid_ang)), (1 - np.cos(math.radians(180) + rad_incid_ang)))
    branch_tracker_arr = branch_dir_arr
    branch_tracker_arr = construct_branches(incid_ang)
    for i, cur_branch_ang in enumerate(branch_tracker_arr):
        ## Have already pre-computed branching angle samples
        ## Determine which sample corresponds to our angle
        # idx = (np.abs(func_samp - math.radians(cur_branch_ang))).argmin()
        # polar_mag = R_samp[idx]

        polar_mag = (1 - np.cos(math.radians(cur_branch_ang) + rad_incid_ang))
        polar_mag = (polar_mag - min_mag) / (max_mag - min_mag) # Normalize magnitude to be 0 to 1

        ## Now compute reflected direction
        cur_cos = math.cos(math.radians(cur_branch_ang))
        cur_sin = math.sin(math.radians(cur_branch_ang))

        rot_mat = np.zeros((2,2))

        rot_mat[0][0] = cur_cos
        rot_mat[0][1] = cur_sin
        rot_mat[1][0] = -cur_sin
        rot_mat[1][1] = cur_cos
        cur_refl_dir = np.matmul(rot_mat, rev_wall_vec)


        cur_refl_ray = Ray(og_pt, cur_refl_dir, input_ray.color)
        cur_refl_ray.color = input_ray.color + polluting_color * polar_mag
        reflected_rays.append(cur_refl_ray)


    return reflected_rays



## Recursive function
## Uses helper intersection function to see where the ray hits the bounding box
## Explodes into some amount of branching_rays recursively
## IF a ray intersects with upper bound, it has exited the box
##      In that case, store the value of that ray into the angle that corresponds to correct v_pixel
def trace_ray(ray_to_trace, tracker):
    if tracker > bounce_limit:
        return

    global accum
    accum += 1
    if accum % 100000 == 0:
        print(accum)
    side_flag, origin_point = compute_box_intersection(ray_to_trace)
    # print(side_flag)
    # print(origin_point)
    # print(tracker)

    ## Check if we have exited the box
    if side_flag == 0:
        exit_dir = ray_to_trace.d.copy()
        # exit_dir[1] *= -1
        # temp_angle = math.degrees(math.atan(-exit_dir[1] / exit_dir[0]))
        # if temp_angle < 0:
        #     temp_angle = 180 - abs(temp_angle)
        ref_dir = np.array([1,0])
        temp_angle = math.degrees(np.arccos(np.dot(ref_dir, exit_dir)))

        u = theta_indx
        v = math.floor(temp_angle / iter_phi) # Just use nearest neigbor

        try:
            color_diff = np.array([255,255,255]) - ray_to_trace.color
            color_diff = np.uint8(color_diff)
            texture[u][v][:] -= color_diff # TODO: Implement an averaging in case we get repeat angles...
        except:
            print("here")
        return


    ## We have intersection point, now let's compute the diffuse BRDF and sample it with N = branching_rays
    rays_spun = diffuse_reflection(side_flag, origin_point, ray_to_trace)
    tracker += 1
    for this_ray in rays_spun:
        # print("spinning off these ray, at tracker {0}:".format(tracker))
        # print(len(rays_spun))
        trace_ray(this_ray, tracker)






# -----------------------------------------------------------------------------#
#                                   MAIN                                       #
# -----------------------------------------------------------------------------#
if __name__ == "__main__":
    print("hello!")
    ## Defining simulation-critical parameters
    branching_rays = 17 # How many rays spin off each reflection
    original_color =  np.array([0,0,0]) #Color((0,0,0)) # This is black
    polluting_color = np.array([20,0,20]) #Color((20,0,0)) # This is a hint of red
    t_iter = 0.05 # parameterization variable step size

    branching_iter = 180 / branching_rays
    branch_dir_arr = np.linspace(branching_iter / 2, 180 - branching_iter / 2, branching_rays)

    bounce_limit = 6 # Limit on ray_trace recursion, point at which ray will "dissapear"

    ## First, let's set up the dimensions of our laser hole!
    ## Make it a square for now
    ## These are unitless! Only have meaning relative to light angles
    W = 1
    H = 1
    box_bounds = [np.array([-W/2,0]), np.array([W/2,0]), np.array([W/2,H]), np.array([-W/2,H])] # List of tuples

    iter_theta = 1    # incident angle of light...THESE ARE IN DEGREES!
    iter_phi   = 1    # reflected angle of light...THESE ARE IN DEGREES!

    u_pixels = round(180/iter_theta)
    v_pixels = round(180/iter_phi)
    # texture = 255*np.ones((u_pixels, v_pixels, 3), dtype=np.uint8)
    texture = 0 * np.ones((u_pixels, v_pixels, 3), dtype=np.uint8)

    # texture = [[0]*v_pixels for ttt in range(u_pixels)]

    ## Start the iteration over thera!
    ## Theta makes up the U coordinate axis of our texture map
    ##      therefore, we iterate 180/iter_theta times to create that many columns of data

    ## Every ray spins off a recursive function that computes some amount of rays
    theta_dir_arr = np.linspace(iter_theta/2, 180-iter_theta/2, u_pixels)
    accum = 0

    for theta_indx, cur_theta in enumerate(theta_dir_arr):
        print("------{0}-------".format(theta_indx))
        rad_ang = math.radians(cur_theta)
        vec = np.array([ -math.cos(rad_ang), math.sin(rad_ang) ]) # cosine is negtive because light is reflected across x axis
        cur_ray = Ray( np.array([0,0]), vec, original_color )


        ## Now run the recursive ray tracer
        trace_ray(cur_ray, 0)
        print("total accumulation = {0}".format(accum))
        accum = 0

    pass

    ## Save the image we've produced!
    im = Image.fromarray(texture)
    im.save("diffuse_reflection_text.png")



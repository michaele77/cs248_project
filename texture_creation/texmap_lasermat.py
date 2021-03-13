# -----------------------------------------------------------------------------#
#                                IMPORTS                                       #
# -----------------------------------------------------------------------------#
import numpy as np
from colorutils import Color
import math
from PIL import Image

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

def diffuse_reflection(side_hit, og_pt, input_ray):
    input_dir = input_ray.d
    ## Don't need fancy bisecting angles here, just reverse whatever axis is orthogonal to the wall
    if side_hit == 1:
        wall_normal = np.array([1,0])
        reflec_dir = np.array( [-input_dir[0],input_dir[1]] )
    elif side_hit == 2:
        wall_normal = np.array([0, -1])
        reflec_dir = np.array( [input_dir[0],-input_dir[1]] )
    elif side_hit == 3:
        wall_normal = np.array([-1, 0])
        reflec_dir = np.array( [-input_dir[0],input_dir[1]] )

    # input_dir = input_ray.d
    # bisecting_alpha = math.acos(np.dot(wall_normal, input_dir)
    # reflec_dir = input_dir

    reflec_ray = Ray(og_pt, reflec_dir, input_ray.color)

    ## We actually "hit" the wall here, so pass on an updated color here
    reflec_ray.color = input_ray.color + polluting_color

    return [reflec_ray]



## Recursive function
## Uses helper intersection function to see where the ray hits the bounding box
## Explodes into some amount of branching_rays recursively
## IF a ray intersects with upper bound, it has exited the box
##      In that case, store the value of that ray into the angle that corresponds to correct v_pixel
def trace_ray(ray_to_trace, tracker):
    side_flag, origin_point = compute_box_intersection(ray_to_trace)
    print(side_flag)
    print(origin_point)
    print(tracker)

    ## Check if we have exited the box
    if side_flag == 0:
        exit_dir = ray_to_trace.d.copy()
        exit_dir[1] *= -1
        temp_angle = math.degrees(math.atan(-exit_dir[1] / exit_dir[0]))
        if temp_angle < 0:
            temp_angle = 180 - abs(temp_angle)

        u = theta_indx
        v = round(temp_angle / iter_phi) # Just use nearest neigbor

        texture[u][v][:] = ray_to_trace.color # TODO: Implement an averaging in case we get repeat angles...
        return

    if tracker > bounce_limit:
        return

    ## We have intersection point, now let's compute the diffuse BRDF and sample it with N = branching_rays
    rays_spun = diffuse_reflection(side_flag, origin_point, ray_to_trace)
    tracker += 1
    for this_ray in rays_spun:
        trace_ray(this_ray, tracker)






# -----------------------------------------------------------------------------#
#                                   MAIN                                       #
# -----------------------------------------------------------------------------#
if __name__ == "__main__":
    print("hello!")
    ## Defining simulation-critical parameters
    branching_rays = 3 # How many rays spin off each reflection
    original_color =  np.array([0,0,0]) #Color((0,0,0)) # This is black
    polluting_color = np.array([50,0,0]) #Color((20,0,0)) # This is a hint of red
    t_iter = 0.01 # parameterization variable step size

    branching_iter = 180 / branching_rays

    bounce_limit = 50 # Limit on ray_trace recursion, point at which ray will "dissapear"

    ## First, let's set up the dimensions of our laser hole!
    ## Make it a square for now
    ## These are unitless! Only have meaning relative to light angles
    W = 1
    H = 1
    box_bounds = [np.array([-W/2,0]), np.array([W/2,0]), np.array([W/2,H]), np.array([-W/2,H])] # List of tuples

    iter_theta = 0.5    # incident angle of light...THESE ARE IN DEGREES!
    iter_phi   = 0.5    # reflected angle of light...THESE ARE IN DEGREES!

    u_pixels = round(180/iter_theta)
    v_pixels = round(180/iter_phi)
    texture = np.zeros((u_pixels, v_pixels, 3), dtype=np.uint8)
    # texture = [[0]*v_pixels for ttt in range(u_pixels)]

    ## Start the iteration over thera!
    ## Theta makes up the U coordinate axis of our texture map
    ##      therefore, we iterate 180/iter_theta times to create that many columns of data

    ## Every ray spins off a recursive function that computes some amount of rays
    theta_dir_arr = np.linspace(iter_theta/2, 180-iter_theta/2, u_pixels)

    for theta_indx, cur_theta in enumerate(theta_dir_arr):
        print("------{0}-------".format(theta_indx))
        rad_ang = math.radians(cur_theta)
        vec = np.array([ -math.cos(rad_ang), math.sin(rad_ang) ]) # cosine is negtive because light is reflected across x axis
        cur_ray = Ray( np.array([0,0]), vec, original_color )


        ## Now run the recursive ray tracer
        trace_ray(cur_ray, 0)

    pass

    ## Save the image we've produced!
    im = Image.fromarray(texture)
    im.save("diffuse_reflection_text.jpg")



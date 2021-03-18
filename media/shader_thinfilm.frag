//
// Parameters that control fragment shader behavior. Different materials
// will set these flags to true/false for different looks
//

uniform bool useTextureMapping;     // true if basic texture mapping (diffuse) should be used
uniform bool useNormalMapping;      // true if normal mapping should be used
uniform bool useEnvironmentMapping; // true if environment mapping should be used
uniform bool useMirrorBRDF;         // true if mirror brdf should be used (default: phong)

//
// texture maps
//

uniform sampler2D diffuseTextureSampler;
uniform sampler2D normalTextureSampler;
uniform sampler2D environmentTextureSampler;
uniform sampler2DArray shadowTextureSampler;


//
// lighting environment definition. Scenes may contain directional
// and point light sources, as well as an environment map
//

#define BRDF_NUM 4
#define MAX_NUM_LIGHTS 5
uniform int  num_directional_lights;
uniform vec3 directional_light_vectors[MAX_NUM_LIGHTS];

uniform int  num_point_lights;
uniform vec3 point_light_positions[MAX_NUM_LIGHTS];

uniform int   num_spot_lights;
uniform vec3  spot_light_positions[MAX_NUM_LIGHTS];
uniform vec3  spot_light_directions[MAX_NUM_LIGHTS];
uniform vec3  spot_light_intensities[MAX_NUM_LIGHTS];
uniform float spot_light_angles[MAX_NUM_LIGHTS];



//
// material-specific uniforms
//

// parameters to Phong BRDF
uniform float spec_exp;

// values that are varying per fragment (computed by the vertex shader)

in vec3 position;     // surface position
in vec3 normal;
in vec2 texcoord;     // surface texcoord (uv)
in vec3 dir2camera;   // vector from surface point to camera
in mat3 tan2world;    // tangent space to world space transform
in vec3 vertex_diffuse_color; // surface color
in vec4 lightspace_pos[MAX_NUM_LIGHTS];
out vec4 fragColor;

#define PI 3.14159265358979323846


//
// Simple diffuse brdf
//
// L -- direction to light
// N -- surface normal at point being shaded
//
vec3 Diffuse_BRDF(vec3 L, vec3 N, vec3 diffuseColor) {
    return diffuseColor * max(dot(N, L), 0.);
}

//
// Phong_BRDF --
//
// Evaluate phong reflectance model according to the given parameters
// L -- direction to light
// V -- direction to camera (view direction)
// N -- surface normal at point being shaded
//
vec3 Phong_BRDF(vec3 L, vec3 V, vec3 N, vec3 diffuse_color, vec3 specular_color, float specular_exponent)
{
    // TODO CS248: Phong Reflectance
    // Implement diffuse and specular terms of the Phong
    // reflectance model here.
    float diffuse = max(dot(normalize(L), normalize(N)), 0.); // make sure it is positive
    vec3 R = 2*dot(normalize(L), normalize(N))*N - normalize(L);
    float spec = pow(max(dot(normalize(R),normalize(V)),0.0),specular_exponent);

    return diffuse*diffuse_color + spec*specular_color;
}

//
// SampleEnvironmentMap -- returns incoming radiance from specified direction
//
// D -- world space direction (outward from scene) from which to sample radiance
// 
vec3 SampleEnvironmentMap(vec3 D)
{    
    // TODO CS248 Environment Mapping
    // sample environment map in direction D.  This requires
    // converting D into spherical coordinates where Y is the polar direction
    // (warning: in our scene, theta is angle with Y axis, which differs from
    // typical convention in physics)
    //
    // Tips:
    //
    // (1) See GLSL documentation of acos(x) and atan(x, y)
    //
    // (2) atan() returns an angle in the range -PI to PI, so you'll have to
    //     convert negative values to the range 0 - 2PI
    //
    // (3) How do you convert theta and phi to normalized texture
    //     coordinates in the domain [0,1]^2?
    vec3 normalized = normalize(D);
    float theta =  acos(normalized.y/(length(normalized)));
    float phi = atan(normalized.x, normalized.z);
    // convert negative values to the range 0 - 2PI
    if (phi<0){
        phi = phi+ 2*PI;
    }
    
    // convert to texture coordinates
    vec2 envCoord = vec2(phi/(2*PI), theta/PI);
    vec3 environmentColor = texture(environmentTextureSampler, envCoord).rgb;

    return environmentColor; 
}

//
// Debug BRDF --
//
// Just return a simple diffuse 
//
vec3 debug_BRDF(vec3 L, vec3 V, vec3 N, vec3 diffuse_color, vec3 specular_color, float specular_exponent)
{
    float diffuse = max(dot(normalize(L), normalize(N)), 0.); // make sure it is positive

    return diffuse*diffuse_color;
}

//
// strange normal BRDF --
//
// Just return a simple diffuse 
//
vec3 strange_normal_BRDF(vec3 L, vec3 V, vec3 N, vec3 diffuse_color, vec3 specular_color, float specular_exponent)
{
    float diffuse = dot(normalize(L), normalize(N)); // make sure it is positive
    if (diffuse < 0.) {
        diffuse *= -1;
    }

    return diffuse*diffuse_color;
}

vec3 texture_map(vec3 L, vec3 V, vec3 N, vec3 diffuse_color, vec3 specular_color, float specular_exponent)
{
    // We will use the specular_exponent to transfer information from JSON file to the fragment shader without totally ripping up the application
    vec3 L_norm = normalize(L);
    vec3 V_norm = normalize(V);
    vec3 N_norm = normalize(N);

    // When sampling texture coordinate, we use the following nomeclature:
    // u --> incident angle of incoming light relative to +x axis
    // v --> angle required to reflect light to eye, or "reflected" angle, relative to +x axis

    // Here we calculate if the viewer's vector is on the "opposide side" of the plane formed by incident vector and normal vector
    // if is_opposite == true, then the surface can be seen if the surface was a strongly reflective/diffuse surface 
    // if is_opposite == false, then the viewer can only see the surface is some of the light "bounces back" towards the light
    // vec3 temp_inc = cross(L_norm, N_norm);
    // vec3 temp_refl = cross(N_norm, V_norm);
    // float opp_side = dot(temp_inc, temp_refl);
    // bool is_opposite = opp_side >= 0;
    

    // Now we define a basis coordinate system from which we can calculate our radial coordinates
    // Define X axis as the axis "underneath" the incoming light
    vec3 naxis_Y = cross(vec3(1,0,0), N_norm);
    naxis_Y = normalize(naxis_Y);
    vec3 naxis_X = cross(naxis_Y, N_norm);
    naxis_X = normalize(naxis_X);

    float theta = 0.5*(1 - dot(naxis_X, L_norm));
    float phi = 0.5*(1 - dot(naxis_X, V_norm));
    vec2 new_text_coords = vec2(theta, phi);

    vec2 film_coords = new_text_coords;

    vec3 film_color = texture(environmentTextureSampler, film_coords).rgb;
    vec3 direct_sample_color = texture(diffuseTextureSampler, texcoord).rgb;
    vec3 color_to_see = texture(diffuseTextureSampler, new_text_coords).rgb; 
    

    float specular_exponent_true = 20.0;
    vec3 spec_ext = vec3(0.3,0.3,0.3);
    float diffuse = max(dot(normalize(L), normalize(N)), 0.); // make sure it is positive
    vec3 R = 2*dot(normalize(L), normalize(N))*N - normalize(L);
    float spec = pow(max(dot(normalize(R),normalize(V)),0.0), specular_exponent_true);

    

    
    if (specular_exponent == 1.0) {
        // lambertian shading: I = dot(L,N)*mapped_tex*intensity  <--  no intensity, multiplied later 
        color_to_see = dot(L_norm, N_norm) * color_to_see; 

        // Add faked specular "glare"
        color_to_see =  color_to_see + spec_ext*spec;

        return color_to_see;

    } else if (specular_exponent == 7.0) {
        // If we are here, then we will directly sample a texture map from diffuse texture map for the "real" color
        // We will apply the film color on top with some coefficient
        float application_coef = 0.5;

        // lambertian shading: I = dot(L,N)*mapped_tex*intensity  <--  no intensity, multiplied later 
        color_to_see = dot(L_norm, N_norm) * color_to_see; 

        // apply thin film with attenuation by application coefficient
        color_to_see = (1-application_coef)*direct_sample_color + application_coef*film_color;

        // Add faked specular "glare"
        color_to_see =  diffuse*color_to_see + spec_ext*spec;
        
        return color_to_see;
        
    } else if (specular_exponent == 10.0) {
        // Produce pure texture map, no lambertian shading

        // Add faked specular "glare"
        color_to_see =  diffuse*color_to_see + spec_ext*spec;
        
        return color_to_see;
        
    } else if (specular_exponent == 20.0) {
        // Use this if we want direct texture sampling, no angle based stuff

        // lambertian shading: I = dot(L,N)*mapped_tex*intensity  <--  no intensity, multiplied later 
        direct_sample_color = dot(L_norm, N_norm) * direct_sample_color; 

        // Add faked specular "glare"
        direct_sample_color =  direct_sample_color + spec_ext*spec;

        return direct_sample_color;
    }

}


// Function to choose BRDF
vec3 choose_BRDF(vec3 L, vec3 V, vec3 N, vec3 diffuse_color, vec3 specular_color, float specular_exponent) {
    switch(BRDF_NUM) {
        case 0:
            return vec3(0.5,0.5,0.5);
        case 1:
            return Phong_BRDF(L, V, N, diffuse_color, specular_color, specular_exponent);
        case 2: 
            return debug_BRDF(L, V, N, diffuse_color, specular_color, specular_exponent);
        case 3:
            return strange_normal_BRDF(L, V, N, diffuse_color, specular_color, specular_exponent);
        case 4:
            // This case is used for purely precomputer BRDFs
            // In this case, our "diffuse" texture is actually whatever texture we are trying to sample
            return texture_map(L, V, N, diffuse_color, specular_color, specular_exponent);
    }

    // if (BRDF_NUM == 0) {
    //     return vec3(0.5,0.5,0.5);
    // } else if (BRDF_NUM == 1) {
    //     return Phong_BRDF(L, V, N, diffuse_color, specular_color, specular_exponent);
    // } else if (BRDF_NUM == 2) {
    //     return debug_BRDF(L, V, N, diffuse_color, specular_color, specular_exponent);
    // }

}


//
// Fragment shader main entry point
//
void main(void)
{

    //////////////////////////////////////////////////////////////////////////
	// Pattern generation. Compute parameters to BRDF 
    //////////////////////////////////////////////////////////////////////////
    
    // BY CONVENTION, we will store the "default color" texture in the diffuse color which is in the diffuseTextureSampler
    // We will store film color to superimpose onto the diffuse color in environmentTextureSampler
    // NOTE: If we want to for example show a mirror texture, now we must use diffuseTextureSampler...upon which we can use a thin film
	vec3 diffuseColor = vec3(1.0, 1.0, 1.0);
    vec3 specularColor = vec3(1.0, 1.0, 1.0);
    vec3 filmColor = vec3(0, 0, 0);
    float specularExponent = spec_exp;

    diffuseColor = texture(diffuseTextureSampler, texcoord).rgb;

    // if (useTextureMapping) {
    //     diffuseColor = texture(diffuseTextureSampler, texcoord).rgb;
    // } else {
    //     diffuseColor = vertex_diffuse_color;
    // }

    // perform normal map lookup if required
    vec3 N = vec3(0);
    if (useNormalMapping) {
        N = texture(normalTextureSampler, texcoord).rgb;     
        // N = normal;
        N = N * 2.0 - 1.0;

        N = tan2world*N;
    //    N = normalize(normal);

    } else {
       N = normalize(normal);
    }

    vec3 V = normalize(dir2camera);

    // Define ambient light; if we are sampling angle-based texture, don't want ambient coming through
    // Only want ambient during thin film application, which is code 7
    vec3 Lo = vec3(0,0,0);
    if (specularExponent == 7.0 || specularExponent == 20.0){
        Lo = vec3(0.1 * diffuseColor);   // this is ambient
    }
    

    /////////////////////////////////////////////////////////////////////////
    // Phase 2: Evaluate lighting and surface BRDF 
    /////////////////////////////////////////////////////////////////////////

    if (useMirrorBRDF) {
        vec3 R = normalize(vec3(1.0));
        R = reflect(normalize(-dir2camera), normalize(normal));

        // sample environment map
        vec3 envColor = SampleEnvironmentMap(R);
        
        // this is a perfect mirror material, so we'll just return the light incident
        // from the reflection direction
        fragColor = vec4(envColor, 1);
        return;
    }

	// for simplicity, assume all lights (other than spot lights) have unit magnitude
	float light_magnitude = 1.0;

	// for all directional lights
	for (int i = 0; i < num_directional_lights; ++i) {
	    vec3 L = normalize(-directional_light_vectors[i]);
		// vec3 brdf_color = Phong_BRDF(L, V, N, diffuseColor, specularColor, specularExponent);
        vec3 brdf_color = choose_BRDF(L, V, N, diffuseColor, specularColor, specularExponent);
	    Lo += light_magnitude * brdf_color;
    }

    // for all point lights
    for (int i = 0; i < num_point_lights; ++i) {
		vec3 light_vector = point_light_positions[i] - position;
        vec3 L = normalize(light_vector);
        float distance = length(light_vector);
        // vec3 brdf_color = Phong_BRDF(L, V, N, diffuseColor, specularColor, specularExponent);
        vec3 brdf_color = choose_BRDF(L, V, N, diffuseColor, specularColor, specularExponent);
        float falloff = 1.0 / (0.01 + distance * distance);
        Lo += light_magnitude * falloff * brdf_color;
    }

    // for all spot lights
	for (int i = 0; i < num_spot_lights; ++i) {
    
        vec3 intensity = spot_light_intensities[i];   // intensity of light: this is intensity in RGB
        vec3 light_pos = spot_light_positions[i];     // location of spotlight
        float cone_angle = spot_light_angles[i];      // spotlight falls off to zero in directions whose
                                                      // angle from the light direction is grester than
                                                      // cone angle. Caution: this value is in units of degrees!

        vec3 dir_to_surface = position - light_pos;
        float angle = acos(dot(normalize(dir_to_surface), spot_light_directions[i])) * 180.0 / PI;

      
        
        // Step 1.
        float D = length(dir_to_surface);
        // printf("here is distance %f\n", D);
        float dist_mod = pow(D, 2.0);
        intensity = (1.0/(1.0+dist_mod)) * intensity;

        // Step 2.
        float smoothing_var = 0.25;

        // float angle_spotlightDir_lightsurfacePos;
        if (angle > (1.0 + smoothing_var) * cone_angle) {
            intensity = vec3(0);
        } else if (angle > (1.0 - smoothing_var) * cone_angle) {
            // If here, we're inteprolating between current intensity and 0
            // delta_x = 2*smoothing_var*cone_angle
            float bound_angle = (1.0 + smoothing_var)*cone_angle;
            intensity = ((bound_angle - angle) / (2*smoothing_var*cone_angle)) * intensity;
        }



        // Render Shadows for all spot lights
        // CS248 TODO: Shadow Mapping: compute shadowing for spotlight i here 
        // compute texture coordinate for the position.
        // homogenous divide for texture coordinates and use that to sample shadow map and then compare that value with the z value of the object
        float pcf_step_size = 256;
        float count=0.0;
        for (int j=-2; j<=2; j++) {
            for (int k=-2; k<=2; k++) {
                vec2 offset = vec2(j,k) / pcf_step_size;
             // sample shadow map at shadow_uv + offset
                vec3 projCoords = lightspace_pos[i].xyz / lightspace_pos[i].w; 
                vec3 look = vec3(projCoords.xy + offset, i);

                float closestDepth = texture(shadowTextureSampler, look).x; 
                float currentDepth = projCoords.z;
                if(currentDepth > closestDepth +.005){
                    count = count + 1.0;
                }
             // and test if the surface is in shadow according to this sample
          }
        }
        intensity=intensity*(1-count/25.0); 
        // record the fraction (out of 25) of shadow tests that are in shadow
        // and attenuate illumination accordingly


    
	    vec3 L = normalize(-spot_light_directions[i]);
		// vec3 brdf_color = Phong_BRDF(L, V, N, diffuseColor, specularColor, specularExponent);
        vec3 brdf_color = choose_BRDF(L, V, N, diffuseColor, specularColor, specularExponent);

	    Lo += intensity * brdf_color;
    }

    fragColor = vec4(Lo, 1);
}




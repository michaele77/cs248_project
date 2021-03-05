uniform mat4 obj2world;                 // object to world transform
uniform mat3 obj2worldNorm;             // object to world transform for normals
uniform vec3 camera_position;           // world space camera position           

uniform mat4 mvp;                       // model-view-projection matrix

uniform bool useNormalMapping;         // true if normal mapping should be used

// per vertex input attributes 
in vec3 vtx_position;            // object space position
in vec3 vtx_tangent;
in vec3 vtx_normal;              // object space normal
in vec2 vtx_texcoord;
in vec3 vtx_diffuse_color; 

// per vertex outputs 
out vec3 position;                  // world space position
out vec3 vertex_diffuse_color;
out vec2 texcoord;
out vec3 dir2camera;                // world space vector from surface point to camera
out vec3 normal;
out mat3 tan2world;                 // tangent space rotation matrix multiplied by obj2WorldNorm

void main(void)
{
    position = vec3(obj2world * vec4(vtx_position, 1));

    // TODO CS248 Normal Mapping: compute 3x3 tangent space to world space matrix here: tan2world
    //
       
    // Tips:
    //
    // (1) Make sure you normalize all columns of the matrix so that it is a rotation matrix.
    //
    // (2) You can initialize a 3x3 matrix using 3 vectors as shown below:
    // vec3 a, b, c;
    // mat3 mymatrix = mat3(a, b, c)
    // (3) obj2worldNorm is a 3x3 matrix transforming object space normals to world space normals
    // compute tangent space to world space matrix

    // As per github instructions:
    // We want to create a rotation matrix that takes tangent space vectors and converts them to world space
    // Per lecture slide, this would look like:
    // | u_x  v_x  w_x |    where u, v, w is the tangent space normal, tangent, and binormal vector respectively
    // | u_y  v_y  w_y |    (NOTE: w column might need to be negative...)
    // | u_z  v_z  w_z |

    vec3 vtx_binomial, norm_norm, norm_tang, norm_binom;
    vtx_binomial = cross(vtx_normal, vtx_tangent);
    
    norm_norm = normalize(vtx_normal);
    norm_tang = normalize(vtx_tangent);
    norm_binom = normalize(vtx_binomial);

    // mat3 rot_mat = mat3(norm_norm, norm_tang, norm_binom);
    // tan2world = rot_mat;
    mat3 tan2objNorm =  mat3(norm_tang,norm_binom, norm_norm);
    tan2world = obj2worldNorm * tan2objNorm;

    
    normal = obj2worldNorm * vtx_normal;

    vertex_diffuse_color = vtx_diffuse_color;
    texcoord = vtx_texcoord;
    dir2camera = camera_position - position;
    gl_Position = mvp * vec4(vtx_position, 1);
}

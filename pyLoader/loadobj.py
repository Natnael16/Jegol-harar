import os
import numpy as np
import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import pyrr
from TextureLoader import load_texture
from ObjLoader import ObjLoader

def rotationMatrix(degree):
    radian = degree * np.pi / 180.0
    mat = np.array([
        [np.cos(radian), 0.0, np.sin(radian), 0.0],
        [0.0,1.0, 0.0,0.0,],
        [-np.sin(radian), 0.0, np.cos(radian) ,0.0],
        [0.0,0.0,0.0,1.0]
    ])

    return mat

vertex_shader = os.path.join(os.getcwd() , "shader" ,"vertex.shader")
vertex_src = open(vertex_shader , 'r').read()

fragment_shader = os.path.join(os.getcwd() , "shader" ,"fragment.shader")
fragment_src = open(fragment_shader , 'r').read()
# vertex_src = """
# # version 330
# layout(location = 0) in vec3 a_position;
# layout(location = 1) in vec2 a_texture;
# layout(location = 2) in vec3 a_normal;
# uniform mat4 model;
# uniform mat4 projection;
# uniform mat4 view;
# out vec2 v_texture;
# void main()
# {
#     gl_Position = projection * view * model * vec4(a_position, 1.0);
#     v_texture = a_texture;
# }
# """

# fragment_src = """
# # version 330
# in vec2 v_texture;
# out vec4 out_color;
# uniform sampler2D s_texture;
# void main()
# {
#     out_color = texture(s_texture, v_texture);
# }
# """


# glfw callback functions
def window_resize(window, width, height):
    glViewport(0, 0, width, height)
    projection = rotationMatrix(30)
    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)


# initializing glfw library
if not glfw.init():
    raise Exception("glfw can not be initialized!")

# creating the window
window = glfw.create_window(1280, 720, "My OpenGL window", None, None)

# check if window was created
if not window:
    glfw.terminate()
    raise Exception("glfw window can not be created!")

# set window's position
glfw.set_window_pos(window, 400, 200)

# set the callback function for window resize
glfw.set_window_size_callback(window, window_resize)

# make the context current
glfw.make_context_current(window)

# load here the 3d meshes
chibi_indices, chibi_buffer = ObjLoader.load_model("D:\\Rsa\\Jegol-harar\\Blender Files\\jegol_combined_backup_final.obj")
# monkey_indices, monkey_buffer = ObjLoader.load_model("C:\\Users\\Lenovo\\Desktop\\Jegol-harar\\Blender Files\\jegol_combined_3.obj")

shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))

# VAO and VBO
VAO = glGenVertexArrays(2)
VBO = glGenBuffers(2)
EBO = glGenBuffers(1)

# Chibi VAO
glBindVertexArray(VAO[0])
# Chibi Vertex Buffer Object
glBindBuffer(GL_ARRAY_BUFFER, VBO[0])
glBufferData(GL_ARRAY_BUFFER, chibi_buffer.nbytes, chibi_buffer, GL_STATIC_DRAW)

glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, chibi_indices.nbytes, chibi_indices, GL_STATIC_DRAW)

# chibi vertices
glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, chibi_buffer.itemsize * 8, ctypes.c_void_p(0))
# chibi textures
glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, chibi_buffer.itemsize * 8, ctypes.c_void_p(12))
# chibi normals
glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, chibi_buffer.itemsize * 8, ctypes.c_void_p(20))
glEnableVertexAttribArray(2)

# # Monkey VAO
# glBindVertexArray(VAO[1])
# # Monkey Vertex Buffer Object
# glBindBuffer(GL_ARRAY_BUFFER, VBO[1])
# glBufferData(GL_ARRAY_BUFFER, monkey_buffer.nbytes, monkey_buffer, GL_STATIC_DRAW)

# # monkey vertices
# glEnableVertexAttribArray(0)
# glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, monkey_buffer.itemsize * 8, ctypes.c_void_p(0))
# # monkey textures
# glEnableVertexAttribArray(1)
# glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, monkey_buffer.itemsize * 8, ctypes.c_void_p(12))
# # monkey normals
# glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, monkey_buffer.itemsize * 8, ctypes.c_void_p(20))
# glEnableVertexAttribArray(2)


textures = glGenTextures(2)
# load_texture("C:\\Users\\Lenovo\\Desktop\\Jegol-harar\\Bricks069_1K_Color.jpg", textures[0])
texture_image = os.path.join(os.getcwd() , "Image Models" ,"Merged_document.png")
load_texture(texture_image, textures[0])

glUseProgram(shader)
glClearColor(0.234375, 0.3576, 0.408, 1)
glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

projection = pyrr.matrix44.create_perspective_projection_matrix(80, 1280 / 720, 0.1, 1000)
chibi_pos = pyrr.matrix44.create_from_translation(pyrr.Vector3([0, -5, -10]))
# monkey_pos = pyrr.matrix44.create_from_translation(pyrr.Vector3([-4, 0, 0]))

# eye, target, up
view = pyrr.matrix44.create_look_at(pyrr.Vector3([80, 50,80]), pyrr.Vector3([0, 0, 0]), pyrr.Vector3([0, 4, 0]))

model_loc = glGetUniformLocation(shader, "model")
proj_loc = glGetUniformLocation(shader, "projection")
view_loc = glGetUniformLocation(shader, "view")

glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)
glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

# the main application loop
degree=0
while not glfw.window_should_close(window):
    glfw.poll_events()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    rot_y = rotationMatrix(degree)
    model = pyrr.matrix44.multiply(rot_y, chibi_pos)

    # draw the chibi character
    glBindVertexArray(VAO[0])
    glBindTexture(GL_TEXTURE_2D, textures[0])
    glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
    glDrawArrays(GL_TRIANGLES, 0, len(chibi_indices))
    glDrawElements(GL_TRIANGLES, len(chibi_indices), GL_UNSIGNED_INT, None)

    # rot_y = pyrr.Matrix44.from_y_rotation(-0.8 * glfw.get_time())
    # model = pyrr.matrix44.multiply(rot_y, monkey_pos)

    # # draw the monkey head
    # glBindVertexArray(VAO[1])
    # glBindTexture(GL_TEXTURE_2D, textures[1])
    # glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
    # glDrawArrays(GL_TRIANGLES, 0, len(monkey_indices))

    glfw.swap_buffers(window)
    degree+=0.125
# terminate glfw, free up allocated resources
glfw.terminate()



# import os
# from OpenGL.GL.shaders import *
# from OpenGL.GLU import *
# from OpenGL.GL import *
# import numpy as np
# from pygame import *
# import pygame

# triangleVAO , program = None , None
# def file_getter(filename):
#     file = os.path.join(os.getcwd() , "shaders" , filename)

#     return open(file , 'r').read()




# def init():

#     global program
    

#     # vertices = np.array([
#     #     [-0.5, -0.5 , 0 , 0 , 1 , 0],
#     #     [.5 , -0.5 , 0, 0 , 0 , 1],
#     #     [-.5 , 0.5 , 0, 0 , 0 , 1],
#     #     [0.5, 0.5 , 0, 1.0 , 0, 0],

#     # ] , dtype = np.float32)
#     vertices = np.array([
#         (-1, -1, -1),
#         (-1, 1, -1),
#         (1, -1, -1),
#         (1, 1, -1),

#         (-1, -1, 1),
#         (-1, 1, 1),
#         (1, -1, 1),
#         (1, 1, 1)
#     ], dtype=np.float32)

#     rec_points = np.array([
#         3, 2, 1,
#         0, 1, 2,

#         7, 6, 5,
#         4, 5, 6,

#         5, 4, 1,
#         0, 1, 4,

#         7, 6, 3,
#         2, 3, 6,

#         7, 3, 5,
#         1, 5, 3,

#         2, 6, 0,
#         4, 0, 6
#     ], dtype=np.uint32)


#     vertex_shader = file_getter("triangle.vertex.shader")
#     fragment_shader = file_getter("triangle.fragment.shader")

#     vertex_shader = compileShader(vertex_shader , GL_VERTEX_SHADER)
#     fragment_shader = compileShader(fragment_shader, GL_FRAGMENT_SHADER)

#     program = compileProgram(vertex_shader, fragment_shader)


#     # VBO
#     rect_VBO = glGenBuffers(1)
#     glBindBuffer(GL_ARRAY_BUFFER , rect_VBO)

#     glBufferData(GL_ARRAY_BUFFER , vertices.nbytes ,vertices , GL_STATIC_DRAW)
 
    
#     #EBO
#     rectangleEBO = glGenBuffers(1)
    
#     glBindBuffer(GL_ELEMENT_ARRAY_BUFFER , rectangleEBO)
#     glBufferData(GL_ELEMENT_ARRAY_BUFFER, rec_points.nbytes ,rec_points , GL_STATIC_DRAW)
     

#     glEnableVertexAttribArray(0)
#     glVertexAttribPointer(0 ,3 , GL_FLOAT , GL_FALSE , 3 * vertices.itemsize ,ctypes.c_void_p(0))

#     glEnableVertexAttribArray(1)
#     glVertexAttribPointer(1 , 3 , GL_FLOAT , GL_FALSE , 3 * vertices.itemsize , ctypes.c_void_p(12))
   
    
#     # glUseProgram(program)
#     glClearColor(0.4 , 0.4 , 0.4 , 1)
    

# def draw():
    
#     init()
#     # radian = 30 * np.pi / 180.0
#     # rotation_mat = np.array([
#     #     [np.cos(radian), -np.sin(radian), 0.0, 0.0],
#     #     [np.sin(radian), np.cos(radian), 0.0, 0.0],
#     #     [0.0, 0.0, 1.0, 0.0],
#     #     [0.0, 0.0, 0.0, 1.0]
#     # ], dtype=np.float32)
#     glRotatef(1, 0.6, 0.4, 0)
#     glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
#     glEnable(GL_DEPTH_TEST)
#     glDepthFunc(GL_LESS)
    
#     glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);

#     glDrawElements(GL_TRIANGLES , 36 ,GL_UNSIGNED_INT, None )
   


# def main():

#     pygame.init()
#     pygame.display.set_mode((800, 600), DOUBLEBUF|OPENGL)
#     glClearColor(0.3 , 0.4 , 0.2 , .7)
#     # glViewport(0, 0 , 500 , 500)
#     gluPerspective(45, (800/600), 0.1, 100.0)
#     glTranslatef(0.0, 0.0, -5)
#     while True:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#         draw()
#         pygame.display.flip()
#         pygame.time.wait(7)

# main()

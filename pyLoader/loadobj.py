
import os
from OpenGL.GL.shaders import *
from OpenGL.GLU import *
from OpenGL.GL import *
import numpy as np
from OpenGL.GL.shaders import compileProgram, compileShader
import pyrr

from pygame import *
import pygame


buffer = []

def differentiate(data_values, coordinates, skip, data_type):
    for d in data_values:
        if d == skip:
            continue
        if data_type == 'float':
            coordinates.append(float(d))
        elif data_type == 'int':
            coordinates.append(int(d)-1)



def fill_buffer(indices_data, vertices, textures, normals):
    for i in range(len(indices_data)):
        if i % 3 == 1: # sort the texture coordinates
            start = indices_data[i] * 2
            end = start + 2
            buffer.extend(textures[start:end])
        elif i % 3 == 0: # sort the vertex coordinates
            start = indices_data[i] * 3
            end = start + 3
            buffer.extend(vertices[start:end])
        elif i % 3 == 1: # sort the texture coordinates
            start = indices_data[i] * 2
            end = start + 2
            buffer.extend(textures[start:end])
        elif i % 3 == 2: # sort the normal vectors
            start = indices_data[i] * 3
            end = start + 3
            buffer.extend(normals[start:end])

def load_model(file, buffer):
    vert_coords = [] # will contain all the vertex coordinates
    tex_coords = [] # will contain all the texture coordinates
    norm_coords = [] # will contain all the vertex normals
    all_indices = [] # will contain all the vertex, texture and normal indices
    indices = [] # will contain the indices for indexed drawing
    with open(file, 'r' , encoding="utf8") as f:
        line = f.readline()
        while line:
            values = line.split()
            if values[0] == 'vt':
                differentiate(values, tex_coords, 'vt', 'float')
            elif values[0] == 'v':
                differentiate(values, vert_coords, 'v', 'float')
            elif values[0] == 'vn':
                differentiate(values, norm_coords, 'vn', 'float')
            elif values[0] == 'f':
                for value in values[1:]:
                    val = value.split('/')
                    for char in val:
                        if char != 'f':
                            all_indices.append(int(char)-1)
                    indices.append(int(val[0])-1)
            line = f.readline()
    
    fill_buffer(all_indices, vert_coords, tex_coords, norm_coords)
    backup = buffer.copy() 
    buffer = [] 
    return np.array(indices, dtype='uint32'), np.array(backup, dtype='float32')


obj_model = vertex_shader = os.path.join(os.getcwd(), "Blender Files", "jegol_combined_backup_f.obj")
verticies = load_model(obj_model , buffer=buffer)[0]
indicies = load_model(obj_model , buffer = buffer)[1]


def init(angle):
    vertex_shader = os.path.join(os.getcwd(), "shader", "vertex.shader")
    vertex_program = compileShader(open(vertex_shader, 'r').read(), GL_VERTEX_SHADER)
    fragment_shader = os.path.join(os.getcwd(), "shader", "fragment.shader")
    fragment_program = compileShader(open(fragment_shader, 'r').read(), GL_FRAGMENT_SHADER)

    shader = compileProgram(vertex_program, fragment_program)

    # VAO and VBO
    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)
    EBO = glGenBuffers(1)

    glBindVertexArray(VAO)  # VAO
    glBindBuffer(GL_ARRAY_BUFFER, VBO)  # VBO
    glBufferData(GL_ARRAY_BUFFER, indicies.nbytes, indicies, GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)  # element buffer object
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, verticies.nbytes, verticies, GL_STATIC_DRAW)

    glEnableVertexAttribArray(0)  # vertices
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, indicies.itemsize * 8, ctypes.c_void_p(0))

    glEnableVertexAttribArray(1)  # for textures
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, indicies.itemsize * 8, ctypes.c_void_p(12))

    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, indicies.itemsize * 8, ctypes.c_void_p(20))
    glEnableVertexAttribArray(2)

    textures_buffer = glGenTextures(1)

    texture_image = os.path.join(os.getcwd(), "Image Models", "Merged_document.png")

    glBindTexture(GL_TEXTURE_2D, textures_buffer)
  
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    loaded = pygame.image.load(texture_image)
    image = pygame.transform.flip(loaded, False, True)
    width = image.get_rect().size[0]
    height = image.get_rect().size[1]

    img_data = pygame.image.tostring(image, "RGBA")
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

    glUseProgram(shader)
    glClearColor(0.5,0.8,1,0.2)  # sky


    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    projection = perspective(80 , 0.1 , 1000,1480/ 900)
    obj = pyrr.matrix44.create_from_translation(pyrr.Vector3([0, -5, -10]))

    # eye, target, up
    view = pyrr.matrix44.create_look_at(pyrr.Vector3([100, 50, 100]), pyrr.Vector3([0, 0, 0]), pyrr.Vector3([0, 4, 0]))

    model_loc = glGetUniformLocation(shader, "model")
    proj_loc = glGetUniformLocation(shader, "projection")
    view_loc = glGetUniformLocation(shader, "view")

    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)
    glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

    rot_y = rotationMatrix(angle)
    model = pyrr.matrix44.multiply(rot_y, obj)

    glBindVertexArray(VAO)
    glBindTexture(GL_TEXTURE_2D, textures_buffer)
    glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)

def perspective(angleofview,near, far,aspectratio ):
    scale = np.tan(angleofview * 0.5 * np.pi / 180)*near
    r=aspectratio*scale
    l=-r
    b=-scale

    mat = np.array([
        [ 2 * near / (r - l), 0.0, 0.0, 0.0],
        [0.0,2 * near / (scale - b), 0.0, 0.0, ],
        [(r + l) / (r - l), (scale + b) / (scale - b), -(far + near) / (far - near), -1.0],
        [0.0, 0.0,  -2 * far * near / (far - near), 0.0]
    ])
    return mat

def rotationMatrix(degree):
    radian = degree * np.pi / 180.0
    mat = np.array([
        [np.cos(radian), 0.0, np.sin(radian), 0.0],
        [0.0, 1.0, 0.0, 0.0, ],
        [-np.sin(radian), 0.0, np.cos(radian), 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])
    return mat

def draw(degree):
    init(degree)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glDrawArrays(GL_TRIANGLES, 0, len(verticies))
    glDrawElements(GL_TRIANGLES, len(verticies), GL_UNSIGNED_INT, None)


def main():
    pygame.init()
    pygame.display.set_mode((1480, 900), DOUBLEBUF | OPENGL)
    degree=0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        draw(degree)
        degree+=20
        pygame.display.flip()
        pygame.time.wait(1)

main()
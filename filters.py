import numpy as np
import tkinter as tk
from tkinter import filedialog
import PIL as pil
from PIL import Image, ImageTk 
import math
from scipy.signal import convolve2d

photo = None
img = None
canvas = None
matrice_pixel = None
matrice_affichee = None
root = None


def rafraichir():
    global img
    global photo

    img =  Image.fromarray(matrice_affichee)
    photo = ImageTk.PhotoImage(img)
    # On vide le canvas
    canvas.delete("all")
    canvas.create_image(0, 0, anchor=tk.NW, image=photo)
    # On redimensionne le canvas à la taille de l'image
    canvas.config(width=img.size[0], height=img.size[1])
    # On force le recalcul des dimensions
    root.update_idletasks()


def filtre_vert():
    global matrice_pixel

    matrice_pixel[:, :, [0,2]] = 0 #SOLUTION Slicing
    rafraichir()


def filtre_sepia():
    global matrice_pixel
    sep = np.array([[0.4,0.3,0.4],
                    [0.3,0.3,0.2],
                    [0.4,0.5,0.1]])
    matrice_pixel = matrice_pixel.dot(sep)
    matrice_pixel = np.clip(matrice_pixel, 0, 225)
    matrice_pixel = matrice_pixel.astype(np.uint8)
    rafraichir()


def correction_gamma(m): #lumo
    global matrice_affichee

    gamma = math.log(float(m)) / math.log(0.5)
    max_value = float(np.iinfo(matrice_affichee.dtype).max)

    matrice_gamma = matrice_affichee.astype(np.float64)
    matrice_gamma = max_value * (matrice_gamma / max_value) ** gamma
    matrice_gamma = np.clip(matrice_gamma, 0, max_value)

    matrice_affichee = matrice_gamma.astype(matrice_affichee.dtype)
    rafraichir()


def correction_gamma_pivotee(p, c): #contrast
    global matrice_affichee

    gammap = 0
    if c >= 0:
        gammap = 1+c
    else:
        gammap = 1/(1-c)
    max_value = float(np.iinfo(matrice_affichee.dtype).max)

    matrice_gammap = matrice_affichee.astype(np.float64) / max_value

    temp = matrice_gammap # pour pas fausser les verif
    matrice_gammap = np.where(temp <= p, p*(temp/p)**gammap, 1 -(1-p)*((1-temp)/(1-p))**gammap) #if else qui marche parce que ambiguous

    matrice_gammap *= max_value
    matrice_gammap = np.clip(matrice_gammap, 0, max_value)

    matrice_affichee = matrice_gammap.astype(matrice_affichee.dtype)
    rafraichir()


def flou():
    global matrice_affichee
    mat_convl = np.ones((3,3)) / 9
    temp_flou = np.zeros_like(matrice_affichee)
    temp_c = 0

    for i in range(3):
        temp_c = convolve2d(matrice_affichee[:,:,i], mat_convl, mode='same', boundary='symm')
        temp_flou[:,:,i] = temp_c
    
    matrice_affichee = temp_flou
    rafraichir()

def flou_gaussien():
    global matrice_affichee
    mat_convl = np.array([[1,2,1],
                         [2,4,2],
                         [1,2,1]])/16
    temp_flou = np.zeros_like(matrice_affichee)
    temp_c = 0

    for i in range(3):
        temp_c = convolve2d(matrice_affichee[:,:,i], mat_convl, mode='same', boundary='symm')
        temp_flou[:,:,i] = temp_c
    
    matrice_affichee = temp_flou
    rafraichir()

def nette(n):
    global matrice_pixel
    global matrice_affichee

    mat_convl = np.ones((3,3)) / 9
    temp_flou = np.zeros_like(matrice_affichee)
    temp_c = 0

    for i in range(3):
        temp_c = convolve2d(matrice_affichee[:,:,i], mat_convl, mode='same', boundary='symm')
        temp_flou[:,:,i] = temp_c

    matrice_details = (matrice_affichee.astype(float) - temp_flou)
    temp = matrice_affichee.astype(float) + matrice_details*float(n)
    matrice_affichee = np.clip(temp, 0, 255)
    matrice_affichee = matrice_affichee.astype(np.uint8)
    rafraichir()

def nette_gaussien():
    global matrice_affichee
    mat_convl = np.array([[1,2,1],
                         [2,4,2],
                         [1,2,1]])/16
    temp_flou = np.zeros_like(matrice_affichee)
    temp_c = 0

    for i in range(3):
        temp_c = convolve2d(matrice_affichee[:,:,i], mat_convl, mode='same', boundary='symm')
        temp_flou[:,:,i] = temp_c
    
    matrice_details = (matrice_affichee.astype(float) - temp_flou)
    temp = matrice_affichee.astype(float) + matrice_details
    matrice_affichee = np.clip(temp, 0, 255)
    matrice_affichee = matrice_affichee.astype(np.uint8)
    rafraichir()
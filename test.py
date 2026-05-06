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
dialogue_effet = None

root = tk.Tk()
root.title("Menubar in Tk")
root.geometry("400x300")

def charger(container):
    """
    Cette fonction :
    * demande à l'utilisateur de choisir une image
    * crée un canevas affichant cette image et le place 
      dans le conteneur passé en paramètre 
        ou
      met à jour le canvas déjà créé lors d'un appel précédent
    """
    # Les variables globales pour l'affichage
    global photo
    global img
    global canvas
    global matrice_pixel
    global matrice_affichee

    # On demande à sélectionner un fichier. Le nom du fichier
    # est renvoyé par la fonction, et stocké dans une variable
    nom_fichier = filedialog.askopenfilename(title="Ouvrir une image")

    # On vérifie si l'utilisateur n'a pas annulé l'ouverture
    if nom_fichier != "":
        # On crée une image Pillow puis on la convertit au format TkInter 
        img = pil.Image.open(nom_fichier)
        matrice_pixel = np.array(img)
        matrice_affichee = matrice_pixel.copy()
        photo = ImageTk.PhotoImage(img)
    
        # Si c'est la première fois qu'on affiche l'image, on crée le canvas
        if canvas is None:
            canvas = tk.Canvas(container, width=img.size[0], height=img.size[1])
            canvas.pack()
        # Si le canvas a déjà été créé, on le met à jour
        else:
            # On vide le canvas
            canvas.delete("all")

            # On redimensionne le canvas à la taille de l'image
            canvas.config(width=img.size[0], height=img.size[1])
            
            # On force le recalcul des dimensions
            container.update_idletasks()

        # On insère la nouvelle image dan le canvas
        canvas.create_image(0, 0, anchor=tk.NW, image=photo)

def fusion():
    global matrice_affichee
    global canvas
    global matrice_pixel
    img2 = None
    matrice_pixel2 = None

    # On demande à sélectionner un fichier. Le nom du fichier
    # est renvoyé par la fonction, et stocké dans une variable
    nom_fichier = filedialog.askopenfilename(title="Ouvrir une image")

    # On vérifie si l'utilisateur n'a pas annulé l'ouverture
    if nom_fichier != "":
        # On crée une image Pillow puis on la convertit au format TkInter 
        img2 = pil.Image.open(nom_fichier)
        matrice_pixel2 = np.array(img2)

        matrice_affichee = (0.5*matrice_pixel2 + 0.5*matrice_pixel)
        matrice_affichee = np.clip(matrice_affichee, 0, 225)
        matrice_affichee = matrice_affichee.astype(np.uint8)
    rafraichir()


def demande():
    charger(root)

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

def applique_effet():
    global matrice_pixel
    global matrice_affichee
    matrice_pixel = matrice_affichee.copy()
    rafraichir()
    dialogue_effet.destroy()

def annule_effet():
    global matrice_pixel
    global dialogue_effet
    global matrice_affichee
    matrice_affichee = matrice_pixel.copy()
    rafraichir()
    dialogue_effet.destroy()

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

def nette_slider():
    global dialogue_effet
    dialogue_effet = tk.Toplevel(root)
    dialogue_effet.title("nette")
    dialogue_effet.geometry("300x150")
    dialogue_effet.grab_set()
    slider = tk.Scale(dialogue_effet, from_=0.05, to=0.95,
                      orient=tk.HORIZONTAL, length=200,
                      resolution=0.01, digits=2,
                      command=nette)
    slider.set(0.50)
    slider.pack(pady=20)

    frame_boutons = tk.Frame(dialogue_effet)
    frame_boutons.pack(side=tk.BOTTOM, pady=10)

    bouton_appliquer = tk.Button(frame_boutons, text="Appliquer",
                                 command=applique_effet)
    bouton_appliquer.pack(side=tk.LEFT, padx=10)

    bouton_annuler = tk.Button(frame_boutons, text="Annuler",
                               command=annule_effet)
    bouton_annuler.pack(side=tk.LEFT, padx=10)

def luminosite_slider():
    global dialogue_effet
    dialogue_effet = tk.Toplevel(root)
    dialogue_effet.title("Luminosité")
    dialogue_effet.geometry("300x150")
    dialogue_effet.grab_set()
    slider = tk.Scale(dialogue_effet, from_=0.05, to=0.95,
                      orient=tk.HORIZONTAL, length=200,
                      resolution=0.01, digits=2,
                      command=correction_gamma)
    slider.set(0.50)
    slider.pack(pady=20)

    frame_boutons = tk.Frame(dialogue_effet)
    frame_boutons.pack(side=tk.BOTTOM, pady=10)

    bouton_appliquer = tk.Button(frame_boutons, text="Appliquer",
                                 command=applique_effet)
    bouton_appliquer.pack(side=tk.LEFT, padx=10)

    bouton_annuler = tk.Button(frame_boutons, text="Annuler",
                               command=annule_effet)
    bouton_annuler.pack(side=tk.LEFT, padx=10)

def contraste_slider():
    global dialogue_effet
    dialogue_effet = tk.Toplevel(root)
    dialogue_effet.title("contraste")
    dialogue_effet.geometry("300x150")
    dialogue_effet.grab_set()
    slider_p = tk.Scale(dialogue_effet, from_=0.001, to=0.999,
                      orient=tk.HORIZONTAL, length=200,
                      resolution=0.01, digits=2,
                      command=lambda x: correction_gamma_pivotee(slider_p.get(), slider_c.get()))
    slider_c = tk.Scale(dialogue_effet, from_=-1, to=1,
                      orient=tk.HORIZONTAL, length=200,
                      resolution=0.01, digits=2,
                      command=lambda x: correction_gamma_pivotee(slider_p.get(), slider_c.get()))
    slider_p.set(0.50)
    slider_p.pack(pady=5)
    slider_c.set(0)
    slider_c.pack(pady=5)

    frame_boutons = tk.Frame(dialogue_effet)
    frame_boutons.pack(side=tk.BOTTOM, pady=10)

    bouton_appliquer = tk.Button(frame_boutons, text="Appliquer",
                                 command=applique_effet)
    bouton_appliquer.pack(side=tk.LEFT, padx=10)

    bouton_annuler = tk.Button(frame_boutons, text="Annuler",
                               command=annule_effet)
    bouton_annuler.pack(side=tk.LEFT, padx=10)



menubar = tk.Menu()

file_menu = tk.Menu(menubar, tearoff=False)
file_menu.add_command(
    label="ouvrir",
    command=demande
)
file_menu.add_command(
    label="fusion",
    command=fusion
)

filtre_menu = tk.Menu(menubar, tearoff=False)
filtre_menu.add_command(
    label='filtre vert',
    command=filtre_vert
)
filtre_menu.add_command(
    label='filtre sépia',
    command=filtre_sepia
)
filtre_menu.add_command(
    label='lumo',
    command=luminosite_slider
)
filtre_menu.add_command(
    label='contraste',
    command=contraste_slider
)
filtre_menu.add_command(
    label='flou',
    command=flou
)
filtre_menu.add_command(
    label='nette',
    command=nette_slider
)

menubar.add_cascade(menu=file_menu, label='file')
menubar.add_cascade(menu=filtre_menu, label='filtre')

root.config(menu = menubar)
root.mainloop()
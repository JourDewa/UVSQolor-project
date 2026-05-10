import numpy as np
import tkinter as tk
from tkinter import filedialog
import PIL as pil
from PIL import Image, ImageTk 
import filters

photo = None
img = None
canvas = None
matrice_pixel = None
matrice_affichee = None
dialogue_effet = None

root = tk.Tk()
root.title("Menubar in Tk")
root.geometry("400x300")
filters.root = root


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
    
        filters.photo = photo
        filters.img = img
        filters.matrice_pixel = matrice_pixel
        filters.matrice_affichee = matrice_affichee
        filters.canvas = canvas
    
        # Si c'est la première fois qu'on affiche l'image, on crée le canvas
        if canvas is None:
            canvas = tk.Canvas(container, width=img.size[0], height=img.size[1])
            canvas.pack()
            filters.canvas = canvas
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
        
        # Update filters module globals
        filters.matrice_affichee = matrice_affichee
    
    filters.rafraichir()


def demande():
    charger(root)


def applique_effet():
    global matrice_pixel
    global matrice_affichee
    global dialogue_effet
    matrice_pixel = matrice_affichee.copy()
    filters.matrice_pixel = matrice_pixel
    filters.rafraichir()
    dialogue_effet.destroy()


def annule_effet():
    global matrice_pixel
    global dialogue_effet
    global matrice_affichee
    matrice_affichee = matrice_pixel.copy()
    filters.matrice_affichee = matrice_affichee
    filters.rafraichir()
    dialogue_effet.destroy()


def nette_slider():
    global dialogue_effet
    dialogue_effet = tk.Toplevel(root)
    dialogue_effet.title("nette")
    dialogue_effet.geometry("300x150")
    dialogue_effet.grab_set()
    slider = tk.Scale(dialogue_effet, from_=0.05, to=0.95,
                      orient=tk.HORIZONTAL, length=200,
                      resolution=0.01, digits=2,
                      command=filters.nette)
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
                      command=filters.correction_gamma)
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
                      command=lambda x: filters.correction_gamma_pivotee(slider_p.get(), slider_c.get()))
    slider_c = tk.Scale(dialogue_effet, from_=-1, to=1,
                      orient=tk.HORIZONTAL, length=200,
                      resolution=0.01, digits=2,
                      command=lambda x: filters.correction_gamma_pivotee(slider_p.get(), slider_c.get()))
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
    command=filters.filtre_vert
)
filtre_menu.add_command(
    label='filtre sépia',
    command=filters.filtre_sepia
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
    command=filters.flou
)
filtre_menu.add_command(
    label='nette',
    command=nette_slider
)

filtre_gaussien = tk.Menu(menubar, tearoff=False)
filtre_gaussien.add_command(
    label='flou gaussien',
    command=filters.flou_gaussien
)
filtre_gaussien.add_command(
    label='nette gaussien',
    command=filters.nette_gaussien
)

menubar.add_cascade(menu=file_menu, label='file')
menubar.add_cascade(menu=filtre_menu, label='filtre')
menubar.add_cascade(menu=filtre_gaussien, label='gaussien')

root.config(menu = menubar)
root.mainloop()

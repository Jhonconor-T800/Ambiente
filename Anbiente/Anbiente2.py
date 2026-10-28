import random
import subprocess
import tkinter as tk

NARANJA = "#ff8700"
VERDE = "#00cc44"
FONDO = "black"
ALFA = 0.7           # transparencia de la ventana: 1.0 = opaca, 0.3 = muy transparente (nunca 0.0)
FUENTE = ("Segoe UI Emoji", 18)

# Para añadir una época nueva, copia una entrada y cambia sus datos
EPOCAS = {
    "Halloween": {
        "titulo": "🎃 HALLOWEEN 🎃",
        "color": NARANJA,
        "lista": ["👻", "💀", "🎃",  "🦇",  "🍁 🍂"],
    },
    "Navidad": {
        "titulo": "🎄 NAVIDAD 🎄",
        "color": VERDE,
        "lista": ["🎄", "🎅", "🤶", "🦌", "❄️", "⛄", "🎁", "🕯️"],
    },
}

CANTIDAD = 9        # cuántas decoraciones se mueven
VELOCIDAD_MS = 30   # menos = más fluido y rápido

ventana = tk.Tk()
ventana.title("Anbiente")
ventana.geometry("420x640")
ventana.configure(bg=FONDO)


def hay_compositor():
    """En Linux/X11, -alpha solo funciona si hay un compositor activo."""
    if ventana.tk.call("tk", "windowingsystem") != "x11":
        return True
    try:
        salida = subprocess.run(["xprop", "-root", "_NET_WM_CM_S0"],
                                capture_output=True, text=True).stdout
        return "not found" not in salida
    except FileNotFoundError:
        return True  # sin xprop no podemos comprobarlo


def aplicar_transparencia():
    ventana.attributes("-alpha", ALFA)
    if not hay_compositor():
        print("Aviso: no hay compositor activo, la transparencia no se verá. "
              "Actívalo en Ajustes > Ajustador de ventanas > Compositor.")


# Se aplica una vez la ventana ya es visible (en X11 si no, a veces se ignora)
ventana.after(200, aplicar_transparencia)

marco = tk.Frame(ventana, bg=FONDO)
marco.pack(fill="both", expand=True, padx=20, pady=20)

animacion = None  # guarda la animación en marcha para poder pararla
#crear funcioncion para detener la animacion
def detener_animacion():
    global animacion
    boton_detener.config(state="disabled")  # deshabilitar el botón
    if animacion is not None:
        ventana.after_cancel(animacion)
        animacion = None
#reanudar animacion
def reanudar_animacion():
    global animacion
    boton_detener.config(state="normal")  # habilitar el botón
    if animacion is None:
        # Llamar a la función mover() para reanudar la animación
        decoracion = EPOCAS["Halloween"]["lista"][0]  # ejemplo de decoración
        menu_epoca("Halloween")  # volver al menú de época para reiniciar la animación

boton_reanudar = tk.Button(ventana, text="Reanudar animación", command=reanudar_animacion, font=("Segoe UI", 12),
                          bg="#555555", fg="white", relief="flat")
boton_reanudar.pack(side="bottom", pady=10)        



boton_detener = tk.Button(ventana, text="Detener animación", command=detener_animacion, font=("Segoe UI", 12),
                          bg="#555555", fg="white", relief="flat")
boton_detener.pack(side="bottom", pady=10)



def limpiar():
    global animacion
    if animacion is not None:
        ventana.after_cancel(animacion)
        animacion = None
    for widget in marco.winfo_children():
        widget.destroy()


def etiqueta(texto, color="white", fuente=FUENTE, **opciones):
    return tk.Label(marco, text=texto, fg=color, bg=FONDO, font=fuente, **opciones)


def boton(texto, comando, color=NARANJA, **opciones):
    return tk.Button(marco, text=texto, command=comando, font=("Segoe UI", 12),
                     bg=color, fg="black", relief="flat", **opciones)


def menu_principal():
    limpiar()
    etiqueta("Elige una época", "white", ("Segoe UI", 20, "bold")).pack(pady=20)

    for nombre, datos in EPOCAS.items():
        # nombre=nombre fija el valor de cada botón (si no, todos abrirían la última época)
        boton(datos["titulo"], lambda nombre=nombre: menu_epoca(nombre),
              datos["color"], width=20).pack(pady=10)


def menu_epoca(nombre):
    limpiar()
    datos = EPOCAS[nombre]
    lista = datos["lista"]
    color = datos["color"]

    etiqueta(datos["titulo"], color, ("Segoe UI Emoji", 22, "bold")).pack(pady=10)
    etiqueta("Elige una decoración:").pack(pady=5)

    for numero, emoji in enumerate(lista, 1):
        etiqueta(f"{numero}.  {emoji}").pack(anchor="w", padx=100)

    entrada = tk.Entry(marco, font=FUENTE, width=5, justify="center",
                       bg="#000000", fg="white", insertbackground="white")
    entrada.pack(pady=15)
    entrada.focus()

    mensaje = etiqueta("", "red", ("Segoe UI", 12))
    mensaje.pack()

    def elegir(evento=None):
        opcion = entrada.get().strip()
        if opcion.isdigit() and 1 <= int(opcion) <= len(lista):
            decorar(lista[int(opcion) - 1], nombre)
        else:
            mensaje.config(text="No lo tenemos, prueba otra vez")
            entrada.delete(0, "end")

    entrada.bind("<Return>", elegir)
    boton("Elegir", elegir, color).pack(pady=5)
    boton("Cambiar de época", menu_principal, "#555555").pack(pady=5)


def decorar(decoracion, nombre):
    global animacion
    limpiar()
    color = EPOCAS[nombre]["color"]

    etiqueta("¡Decorando tu espacio!", color,
             ("Segoe UI", 12), wraplength=360).pack(pady=10)

    # El botón se coloca antes que el canvas para que quede abajo
    boton("Volver", lambda: menu_epoca(nombre), color).pack(side="bottom", pady=10)

    canvas = tk.Canvas(marco, bg=FONDO, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    ventana.update_idletasks()  # para conocer el tamaño real del canvas
    ancho = max(canvas.winfo_width(), 100)
    alto = max(canvas.winfo_height(), 100)

    # Cada decoración: [id, velocidad en x, velocidad en y]
    items = []
    for _ in range(CANTIDAD):
        x = random.randint(30, ancho - 30)
        y = random.randint(30, alto - 30)
        dx = random.choice([-1, 1]) * random.randint(2, 5)
        dy = random.choice([-1, 1]) * random.randint(2, 5)
        id_texto = canvas.create_text(x, y, text=decoracion, font=FUENTE, fill="white")
        items.append([id_texto, dx, dy])

    def mover():
        global animacion
        ancho = canvas.winfo_width()
        alto = canvas.winfo_height()
        for item in items:
            id_texto, dx, dy = item
            canvas.move(id_texto, dx, dy)
            x, y = canvas.coords(id_texto)
            # Rebote: se invierte la dirección al tocar un borde
            if x <= 20:
                item[1] = abs(dx)
            elif x >= ancho - 20:
                item[1] = -abs(dx)
            if y <= 20:
                item[2] = abs(dy)
            elif y >= alto - 20:
                item[2] = -abs(dy)
        animacion = ventana.after(VELOCIDAD_MS, mover)

    mover()

print(ventana.tk.call("tk", "windowingsystem"))
menu_principal()
ventana.mainloop()
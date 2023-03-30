import cv2
import pyautogui
import time
import os
import numpy as np
import tkinter as tk
import threading
import tkinter.filedialog as filedialog
from tkinter import ttk
from tkinter import messagebox
from pynput import mouse
import keyboard

root = tk.Tk()

IMAGES_PATH = 'C:\\Users\\iansi\\imagens'
running = True

def stop_process():
    global root
    print("Processo cancelado")
    root.destroy()

def update_images_path():
    global IMAGES_PATH
    IMAGES_PATH = images_path_entry.get()
    print(f"IMAGES_PATH atualizado para: {IMAGES_PATH}")

def update_positions():
    global aumentar_valor_position, colocar_venda_position, item_region
    
    valor_position_str = valor_position_entry.get().strip()
    venda_position_str = venda_position_entry.get().strip()
    region_str = region_entry.get().strip()
    
    if not valor_position_str or not venda_position_str or not region_str:
        print("Certifique-se de que todos os campos estejam preenchidos.")
        return
    
    x_val, y_val = [int(x.strip()) for x in valor_position_str.split(',')]
    aumentar_valor_position = (x_val, y_val)
    
    x_ven, y_ven = [int(x.strip()) for x in venda_position_str.split(',')]
    colocar_venda_position = (x_ven, y_ven)
    
    x1, y1, x2, y2 = [int(x.strip()) for x in region_str.split(',')]
    item_region = (x1, y1, x2 - x1, y2 - y1)
    
    print(f"aumentar_valor_position atualizado para: {aumentar_valor_position}")
    print(f"colocar_venda_position atualizado para: {colocar_venda_position}")
    print(f"item_region atualizado para: {item_region}")
    
def export_config():
    config_data = {
        "Caminho Imagens": images_path_entry.get(),
        "Valor Position": valor_position_entry.get(),
        "Venda Position": venda_position_entry.get(),
        "Região": region_entry.get()
    }

    with open("config.txt", "w") as config_file:
        for key, value in config_data.items():
            config_file.write(f"{key}: {value}\n")
    
    print("Configuração exportada para 'config.txt'")

import tkinter.filedialog as filedialog

def import_config():
    config_file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")])

    if not config_file_path:
        print("Nenhum arquivo selecionado.")
        return

    with open(config_file_path, "r") as config_file:
        for line in config_file:
            key, value = line.strip().split(": ")
            if key == "Caminho Imagens":
                images_path_entry.delete(0, tk.END)
                images_path_entry.insert(0, value)
            elif key == "Valor Position":
                valor_position_entry.delete(0, tk.END)
                valor_position_entry.insert(0, value)
            elif key == "Venda Position":
                venda_position_entry.delete(0, tk.END)
                venda_position_entry.insert(0, value)
            elif key == "Região":
                region_entry.delete(0, tk.END)
                region_entry.insert(0, value)

    update_positions()  # Adicione esta linha para atualizar as posições
    print(f"Configuração importada de '{config_file_path}'")
    
def get_click_coordinates():
    print("Mova o mouse para o canto superior esquerdo da região e pressione Enter.")
    keyboard.wait('enter')  # Usar a biblioteca keyboard em vez de input()
    x1, y1 = pyautogui.position()
    print(f"Canto superior esquerdo: ({x1}, {y1})")

    print("Mova o mouse para o canto inferior direito da região e pressione Enter.")
    keyboard.wait('enter')  # Usar a biblioteca keyboard em vez de input()
    x2, y2 = pyautogui.position()
    print(f"Canto inferior direito: ({x2}, {y2})")

    return x1, y1, x2, y2

def update_region_entry():
    x1, y1, x2, y2 = get_click_coordinates()
    region_entry.delete(0, tk.END)
    region_entry.insert(0, f"{x1}, {y1}, {x2 - x1}, {y2 - y1}")

get_region_coordinates_button = tk.Button(root, text="Obter Coordenadas da Região", command=update_region_entry, bg="#4CAF50", fg="white", relief="raised")
get_region_coordinates_button.grid(column=2, row=9, padx=5, pady=10)

def update_region():
    global item_region
    item_region = tuple(map(int, region_entry.get().split(',')))
    print(f"Região atualizada para: {item_region}")
    
def open_parameter_discovery_window():
    parameter_window = tk.Toplevel(root)
    parameter_window.title("Descobrir Parâmetros")
    parameter_window.configure(bg="#F0F0F0")

def capture_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot_np = np.array(screenshot)
    return cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

def find_and_click(image, confidence=0.9, region=None):
    image_path = os.path.join(IMAGES_PATH, image)
    template = cv2.imread(image_path)

    if region:
        screenshot = capture_screenshot()[region[1]:region[1]+region[3], region[0]:region[0]+region[2]]
    else:
        screenshot = capture_screenshot()

    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= confidence:
        if region:
            center = (region[0] + max_loc[0] + template.shape[1] // 2, region[1] + max_loc[1] + template.shape[0] // 2)
        else:
            center = (max_loc[0] + template.shape[1] // 2, max_loc[1] + template.shape[0] // 2)
        pyautogui.click(center)
        return True
    return False

def click_fixed_position(x, y):
    pyautogui.click(x, y)
    
aumentar_valor_position = (1250, 554)  # Substitua pelas coordenadas corretas
colocar_venda_position = (1194, 861)   # Substitua pelas coordenadas corretas

def open_parameter_discovery_window():
    discovery_window = tk.Toplevel(root)
    discovery_window.title("Descobrir Parâmetros")

    coords_label = tk.Label(discovery_window, text="Coordenadas VALOR:")
    coords_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)

    coords_var = tk.StringVar()
    coords_entry = tk.Entry(discovery_window, textvariable=coords_var, width=30)
    coords_entry.grid(row=0, column=1, padx=10, pady=10)

    current_param = "VALOR"
    valor_position = None
    venda_position = None

    def display_mouse_position():
        nonlocal current_param, valor_position, venda_position
        x, y = pyautogui.position()
        position_str = f"{x}, {y}"
        coords_var.set(position_str)

        if current_param == "VALOR":
            valor_position = position_str
            discovery_window.after(100, ask_continue_or_restart)
        else:
            venda_position = position_str
            valor_pos, venda_pos = save_positions_to_config_file()
            valor_position_entry.delete(0, tk.END)
            valor_position_entry.insert(0, valor_pos)
            venda_position_entry.delete(0, tk.END)
            venda_position_entry.insert(0, venda_pos)
            discovery_window.destroy()

    def ask_continue_or_restart():
        nonlocal current_param
        user_response = messagebox.askyesno("Continuar ou recomeçar", "Deseja continuar para o próximo passo?")
        if user_response:
            current_param = "VENDA"
            coords_label.config(text="Coordenadas VENDA:")
        else:
            coords_var.set("")


    def save_positions_to_config_file():
        nonlocal valor_position, venda_position
        return valor_position, venda_position

        valor_position_line = f"Valor Position: {valor_position}\n"
        venda_position_line = f"Venda Position: {venda_position}\n"

        lines[1] = valor_position_line
        lines[2] = venda_position_line

        with open("config.txt", "w") as file:
            file.writelines(lines)

    def get_position():
        keyboard.wait('space')
        display_mouse_position()

    get_position_button = tk.Button(discovery_window, text="Obter Posição", command=get_position)
    get_position_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    discovery_window.mainloop()
    
def browse_directory():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        images_path_entry.delete(0, tk.END)
        images_path_entry.insert(0, folder_selected)
        update_images_path()

browse_button = tk.Button(root, text="Procurar", command=browse_directory, bg="#4CAF50", fg="white", relief="raised")
browse_button.grid(column=3, row=0, padx=5, pady=5)
    
def get_repetitions():
    try:
        repetitions = int(repetitions_entry.get())
        if repetitions < 1:
            raise ValueError
        return repetitions
    except ValueError:
        messagebox.showerror("Erro", "Insira um número inteiro válido maior que 0 para as repetições.")
        return None

def main(item, repetitions):
    global aumentar_valor_position, colocar_venda_position, running

    running = True
    for i in range(repetitions):
        if not running:
            break
        print(f"Executando o processo {i + 1} de {repetitions}")
        while not find_and_click('caixa.png', region=(417, 188, 1040, 722)):
            pass
        while not find_and_click(f'{item}.png', region=(417, 188, 1040, 722)):
            pass
        time.sleep(0.020)  # Adiciona um intervalo de 2 milissegundos
        click_fixed_position(*aumentar_valor_position)
        click_fixed_position(*colocar_venda_position)

def select_item():
    item = item_var.get()
    if item:
        repetitions = get_repetitions()
        if repetitions is not None:
            root.destroy()
            main(item, repetitions)

def on_item_select():
    item = item_var.get()
    for rbutton, value in radio_buttons.items():
        if item == value:
            rbutton.config(bg='#90EE90')
        else:
            rbutton.config(bg='#ADD8E6')

root.title("@MagoDoHayDay")
root.configure(bg="#ffde59")

repetitions_label = tk.Label(root, text="Repetições:", bg="#F0F0F0")
repetitions_label.grid(column=0, row=8, padx=5, pady=5, sticky='W')

repetitions_entry = tk.Entry(root)
repetitions_entry.grid(column=1, row=8, padx=5, pady=5, columnspan=2)

images_path_label = tk.Label(root, text="Caminho Imagens:", bg="#F0F0F0")
images_path_label.grid(column=0, row=0, padx=5, pady=5, sticky='W')

images_path_entry = tk.Entry(root)
images_path_entry.grid(column=1, row=0, padx=5, pady=5)

update_images_path_button = tk.Button(root, text="Atualizar", command=update_images_path, bg="#4CAF50", fg="white", relief="raised")
update_images_path_button.grid(column=2, row=0, padx=5, pady=5)

valor_position_label = tk.Label(root, text="Valor Position:", bg="#F0F0F0")
valor_position_label.grid(column=0, row=1, padx=5, pady=5, sticky='W')

valor_position_entry = tk.Entry(root)
valor_position_entry.grid(column=1, row=1, padx=5, pady=5)

venda_position_label = tk.Label(root, text="Venda Position:", bg="#F0F0F0")
venda_position_label.grid(column=0, row=2, padx=5, pady=5, sticky='W')

venda_position_entry = tk.Entry(root)
venda_position_entry.grid(column=1, row=2, padx=5, pady=5)

update_positions_button = tk.Button(root, text="Atualizar", command=update_positions, bg="#4CAF50", fg="white", relief="raised")
update_positions_button.grid(column=2, row=1, padx=5, pady=5)

region_label = tk.Label(root, text="Região:", bg="#F0F0F0")
region_label.grid(column=0, row=3, padx=5, pady=5, sticky='W')

region_entry = tk.Entry(root)
region_entry.grid(column=1, row=3, padx=5, pady=5)

update_region_button = tk.Button(root, text="Atualizar", command=update_region, bg="#4CAF50", fg="white", relief="raised")
update_region_button.grid(column=2, row=3, padx=5, pady=5)

export_config_button = tk.Button(root, text="Salvar CFG", command=export_config, bg="#4CAF50", fg="white", relief="raised")
export_config_button.grid(column=2, row=4, padx=5, pady=5)

import_config_button = tk.Button(root, text="Importar CFG", command=import_config, bg="#4CAF50", fg="white", relief="raised")
import_config_button.grid(column=3, row=4, padx=5, pady=5)

item_var = tk.StringVar()
item_var.trace("w", lambda *args: on_item_select())

tk.Label(root, text="Escolha o item:", bg="#F0F0F0").grid(column=0, row=4, padx=5, pady=5, sticky='W')

anel_rb = tk.Radiobutton(root, text="Anel", variable=item_var, value="anel", bg="#F0F0F0", selectcolor="#F0F0F0", indicatoron=0)
anel_rb.grid(column=0, row=5, padx=5, pady=5, sticky='W')

perna_rb = tk.Radiobutton(root, text="Pernas de lã", variable=item_var, value="perna", bg="#F0F0F0", selectcolor="#F0F0F0", indicatoron=0)
perna_rb.grid(column=0, row=6, padx=5, pady=5, sticky='W')

ovo_rb = tk.Radiobutton(root, text="Bacon e ovos", variable=item_var, value="ovo", bg="#F0F0F0", selectcolor="#F0F0F0", indicatoron=0)
ovo_rb.grid(column=0, row=7, padx=5, pady=5, sticky='W')

radio_buttons = {anel_rb: "anel", perna_rb: "perna", ovo_rb: "ovo"}

start_button = tk.Button(root, text="INICIAR", command=select_item, bg="#4CAF50", fg="white", relief="raised")
start_button.grid(column=3, row=8, padx=5, pady=5)

cancel_button = tk.Button(root, text="Cancelar", command=stop_process, bg="#F44336", fg="white", relief="raised")
cancel_button.grid(column=2, row=8, padx=5, pady=10)

discover_parameters_button = tk.Button(root, text="Descobrir parâmetros", command=open_parameter_discovery_window, bg="#4CAF50", fg="white", relief="raised")
discover_parameters_button.grid(column=1, row=9, padx=5, pady=10)

root.mainloop()


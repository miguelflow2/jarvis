"""HUD holographique Iron Man - overlay transparent PyQt6 / Tkinter"""
import os

def launch_hud():
    """Lance le HUD transparent (fenetre toujours au dessus)"""
    try:
        import tkinter as tk
        root = tk.Tk()
        root.title("JARVIS HUD")
        root.attributes("-topmost", True)
        root.attributes("-alpha", 0.85)
        root.overrideredirect(True)
        root.geometry("340x220+20+20")
        root.configure(bg="#0a0a0f")
        # Canvas circulaire
        import psutil, math, time
        canvas = tk.Canvas(root, width=340, height=220, bg="#0a0a0f", highlightthickness=0)
        canvas.pack()
        def draw():
            canvas.delete("all")
            # anneaux
            for r, col in [(80,"#3a5bff"), (60,"#00ffcc"), (40,"#ff3a5b")]:
                canvas.create_oval(170-r,110-r,170+r,110+r, outline=col, width=2)
            # stats
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            canvas.create_text(170, 30, text=f"JARVIS HUD", fill="#e6e6ff", font=("Consolas", 10, "bold"))
            canvas.create_text(170, 180, text=f"CPU {cpu:.0f}%  RAM {ram:.0f}%", fill="#aaa", font=("Consolas", 9))
            canvas.create_text(170, 195, text="Salut Jarvis", fill="#3a5bff", font=("Consolas", 8))
            # bouton fermer
            canvas.create_rectangle(300,10,330,30, outline="#ff3a5b")
            canvas.create_text(315,20, text="X", fill="#ff3a5b", font=("Consolas", 9))
            def on_click(e):
                if 300 <= e.x <= 330 and 10 <= e.y <= 30:
                    root.destroy()
            canvas.bind("<Button-1>", on_click)
            canvas.create_text(170,110, text="●", fill="#00ffcc", font=("Consolas", 48))
            root.after(1000, draw)
        draw()
        # draggable
        def start_move(e): root._x, root._y = e.x, e.y
        def do_move(e): root.geometry(f"+{root.winfo_x()+e.x-root._x}+{root.winfo_y()+e.y-root._y}")
        canvas.bind("<ButtonPress-1>", start_move)
        canvas.bind("<B1-Motion>", do_move)
        root.mainloop()
        return "HUD ferme"
    except Exception as e:
        return f"Erreur HUD: {e}. Installe tkinter (de base) ou PyQt6: pip install PyQt6"

def hud_rainmeter_hint() -> str:
    return "Pour un HUD Rainmeter Stark: installe Rainmeter + skin 'JARVIS HUD' depuis deviantart.com - JARVIS peut generer le .ini sur demande"

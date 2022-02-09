from tkinter import *
from tkinter import ttk
from tkinter import messagebox as msg
from tkinter import scrolledtext
import os
import subprocess

root = Tk()
root.title('Minecraft Launcher')
root.geometry('1280x720')
root['bg'] = '#262626'
icondir = 'assets/'
iconfile = os.path.join(icondir, 'icon.ico')
root.iconbitmap(default=iconfile)
root.resizable(0,0)

canvas = Canvas(root, width = 1280, height = 500,bd=0, highlightthickness=0,bg="#262626")      
canvas.pack()      
img = PhotoImage(file="assets/preview.png")      
canvas.create_image(-100,-80, anchor=NW, image=img) 

dev_mode=True

def run():
    root.wm_withdraw()
    command = 'minecraft.exe'
    process = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    output,error = process.communicate()

    if error:
        msg.showerror("Minecraft Launcher",f"{error}")

    if dev_mode == True:
        save_prompt = Toplevel()
        save_prompt.resizable(0,0)
        text = scrolledtext.ScrolledText(save_prompt)
        text.config(state='normal')
        text.insert('end', output)
        text.insert('end', error)
        text.yview('end')
        text.config(state='disabled')
        text.pack()
        return

    root.deiconify()

run_button = Button(text="Play",
                    command=run,
                    fg = 'white',
                    bg = '#008945',
                    highlightcolor="white", 
                    highlightbackground="white", 
                    borderwidth=4,
                    width="15",
                    font="Consolas 20 bold")
run_button.pack(pady=5)

root.mainloop()
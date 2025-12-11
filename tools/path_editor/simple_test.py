#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox

def test_click(event):
    print(f"Clicked at: {event.x}, {event.y}")
    canvas.create_oval(event.x-10, event.y-10, event.x+10, event.y+10, 
                      fill="red", outline="black", width=2)
    canvas.create_text(event.x, event.y-20, text=f"({event.x},{event.y})", 
                      fill="blue", font=("Arial", 10))

if __name__ == "__main__":
    # Create main window
    root = tk.Tk()
    root.title("Simple Path Test")
    root.geometry("800x600+200+200")
    
    # Show a message box to confirm GUI is working
    messagebox.showinfo("Test", "GUI is working! Click OK to continue.")
    
    # Create canvas
    canvas = tk.Canvas(root, width=600, height=500, bg="yellow", relief="solid", borderwidth=3)
    canvas.pack(pady=20)
    
    # Add instructions
    canvas.create_text(300, 50, text="CLICK ANYWHERE ON THIS YELLOW AREA", 
                      fill="red", font=("Arial", 16, "bold"))
    canvas.create_text(300, 80, text="You should see red circles appear where you click", 
                      fill="blue", font=("Arial", 12))
    
    # Bind click event
    canvas.bind("<Button-1>", test_click)
    
    # Add quit button
    tk.Button(root, text="QUIT", command=root.quit, font=("Arial", 14), 
             bg="red", fg="white").pack(pady=10)
    
    print("Simple test GUI should now be visible!")
    print("Look for a window with a YELLOW canvas area")
    
    root.mainloop()
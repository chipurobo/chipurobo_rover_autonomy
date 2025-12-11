#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog
import json


class PathEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("ChipuRobo Path Editor (Simple Version)")

        # Canvas where we click to make points
        self.canvas = tk.Canvas(root, width=1000, height=700, bg="white", 
                               relief="solid", borderwidth=2, highlightthickness=1)
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Draw grid for better visibility
        self.draw_grid()

        # Waypoint list
        self.points = []

        # Side panel
        right_frame = tk.Frame(root)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Add title
        tk.Label(right_frame, text="Path Editor Controls", font=("Arial", 14, "bold")).pack(pady=10)
        
        tk.Button(right_frame, text="💾 Save Path", command=self.save_path, 
                 font=("Arial", 12), bg="lightgreen", width=15).pack(pady=5)
        tk.Button(right_frame, text="📁 Load Path", command=self.load_path, 
                 font=("Arial", 12), bg="lightblue", width=15).pack(pady=5)
        tk.Button(right_frame, text="🗑️ Clear All", command=self.clear, 
                 font=("Arial", 12), bg="lightcoral", width=15).pack(pady=5)
        
        tk.Label(right_frame, text="Waypoints:", font=("Arial", 12, "bold")).pack(pady=(20,5))

        self.list_box = tk.Listbox(right_frame, width=25, height=20, font=("Arial", 10))
        self.list_box.pack(pady=10)
        
        # Add status label
        self.status_label = tk.Label(right_frame, text="Click on canvas to add waypoints!", 
                                   font=("Arial", 10), fg="blue")
        self.status_label.pack(pady=10)

        # Bind click event
        self.canvas.bind("<Button-1>", self.add_point)
        
        # Add instructions
        self.canvas.create_text(500, 30, text="Click anywhere on this canvas to create waypoints!", 
                               fill="darkblue", font=("Arial", 16, "bold"))
        self.canvas.create_text(500, 50, text="Each click creates a red waypoint connected by blue arrows", 
                               fill="darkgreen", font=("Arial", 12))
    
    def draw_grid(self):
        """Draw a grid for better visual reference"""
        # Draw vertical lines
        for i in range(0, 1000, 50):
            self.canvas.create_line(i, 0, i, 700, fill="white", width=1)
        
        # Draw horizontal lines
        for i in range(0, 700, 50):
            self.canvas.create_line(0, i, 1000, i, fill="white", width=1)

    def add_point(self, event):
        x, y = event.x, event.y

        # Store point
        self.points.append((x, y))
        self.list_box.insert(tk.END, f"Waypoint {len(self.points)}: ({x}, {y})")
        
        # Update status
        self.status_label.config(text=f"Added waypoint {len(self.points)} at ({x}, {y})")

        # Draw point - much larger and more visible
        r = 8
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="red", outline="darkred", width=3)
        
        # Add point number text
        self.canvas.create_text(x, y - 15, text=str(len(self.points)), fill="black", font=("Arial", 12, "bold"))

        # Draw line from previous point - thicker and more visible
        if len(self.points) > 1:
            x1, y1 = self.points[-2]
            self.canvas.create_line(x1, y1, x, y, fill="blue", width=4, smooth=True)
            # Add arrow to show direction
            self.canvas.create_line(x1, y1, x, y, fill="darkblue", width=2, arrow=tk.LAST, arrowshape=(16, 20, 6))

    def save_path(self):
        if not self.points:
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".path",
            filetypes=[("ChipuRobo Path File", "*.path")]
        )
        if not filepath:
            return

        # Convert screen coords to robot coords (meters later)
        data = {"points": self.points}
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)

        print("Saved:", filepath)

    def load_path(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("ChipuRobo Path File", "*.path")]
        )
        if not filepath:
            return

        with open(filepath, "r") as f:
            data = json.load(f)

        self.clear()

        for pt in data.get("points", []):
            self.points.append(tuple(pt))
            self.list_box.insert(tk.END, str(pt))

        self.redraw()

    def clear(self):
        self.points = []
        self.canvas.delete("all")
        self.list_box.delete(0, tk.END)
        self.draw_grid()  # Redraw grid
        self.status_label.config(text="Cleared all waypoints. Click to add new ones!")
        
        # Re-add instructions
        self.canvas.create_text(500, 30, text="Click anywhere on this canvas to create waypoints!", 
                               fill="darkblue", font=("Arial", 16, "bold"))
        self.canvas.create_text(500, 50, text="Each click creates a red waypoint connected by blue arrows", 
                               fill="darkgreen", font=("Arial", 12))

    def redraw(self):
        self.canvas.delete("all")
        self.draw_grid()  # Redraw grid
        
        # Draw all lines first
        for i in range(1, len(self.points)):
            x1, y1 = self.points[i - 1]
            x2, y2 = self.points[i]
            self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=4, smooth=True)
            self.canvas.create_line(x1, y1, x2, y2, fill="darkblue", width=2, arrow=tk.LAST, arrowshape=(16, 20, 6))
        
        # Draw all points on top
        for i, (x, y) in enumerate(self.points):
            r = 8
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="red", outline="darkred", width=3)
            self.canvas.create_text(x, y - 15, text=str(i + 1), fill="black", font=("Arial", 12, "bold"))


if __name__ == "__main__":
    root = tk.Tk()
    
    # Force window to appear and be visible
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    
    # Set window size and position
    root.geometry("1300x750+100+100")
    root.resizable(True, True)
    
    print("Starting Path Editor GUI...")
    print("Window should appear shortly...")
    
    app = PathEditor(root)
    
    print("Path Editor initialized successfully!")
    print("If you can't see the window, try clicking on the Python icon in your dock")
    
    root.mainloop()
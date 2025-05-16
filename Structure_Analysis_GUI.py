import numpy as np
from Structure_Analysis import *
import tkinter as tk
from tkinter import ttk
from utils import *

def main():

    structure = Structure(name="Test Structure")

    def update_structure_from_slider(_=None):
        angle = round(alpha_var.get(), 2)
        alpha_var.set(angle)
        l = round(l_var.get(),1)
        l_var.set(l)
        structure.bars.clear()
        p = p_var.get()

        width = width_var.get()
        height = height_var.get()

        hollow =  section_type.get() == "hollow"
        section_type.trace_add("write", lambda *args: update_structure_from_slider())

        if hollow:
            width_thickness = width_thickness_var.get()
            height_thickness = height_thickness_var.get()
        else:
            width_thickness = 0.0
            height_thickness = 0.0
        # Recalculate h
        h = l * np.sin(np.deg2rad(angle))
        h_var.set(f"{h:.2f}")

        # Redefine bars
        bar1 = Bar(length=l, width=width, height=height, hollow=hollow, section='rectangular',
                material='aluminum', alpha=angle, width_thickness=width_thickness, height_thickness=height_thickness)
        bar2 = Bar(length=l, width=width, height=height, hollow=hollow, section='rectangular',
                material='aluminum', alpha=180 - angle, width_thickness=width_thickness, height_thickness=height_thickness)
        bar3 = Bar(length=l_platform, width=0.1, height=0.1, hollow=hollow, section='rectangular',
                material='abs', alpha=0)

        structure.add_bar(bar1)
        structure.add_bar(bar2)
        structure.add_bar(bar3)


        bar1.start(Node("A", 0, 0))
        bar1.end()

        bar2.start(Node("D", l * np.cos(np.deg2rad(angle)), 0))
        bar2.end()

        bar3.start(Node("", -5, h))
        bar3.end()
        bar3.add_load(0.5, 0, -p, 0)

        # Calculate the x-coordinate of the center of the platform
        xbaricenter_platform = bar3.start_node.x + 0.5 * (bar3.end_node.x - bar3.start_node.x)
        # Calculate the distance from the start node of bar1 to the center of the platform
        d = xbaricenter_platform - bar1.start_node.x
        f = p/np.tan(np.deg2rad(angle))
        
        # Add loads to the bars
        # Bar AE
        bar1.add_load(0, f, p - p * d / (l * np.cos(np.deg2rad(angle))), 0) #A
        bar1.add_load(0.5, -f, (2*p*d/(l*np.cos(np.deg2rad(angle))))-p, 0) #C
        bar1.add_load(1, 0, -p*d/(l*np.cos(np.deg2rad(angle))), 0) #E

        # Bar BD
        bar2.add_load(0, -f, p*d/(l*np.cos(np.deg2rad(angle))), 0) #B
        bar2.add_load(1/2, f, -((2*p*d/(bar2.length*np.cos(np.deg2rad(angle)))) - p), 0) #C
        bar2.add_load(1, 0, -(p - p*d/(l*np.cos(np.deg2rad(angle)))), 0) #D

        # Calculate stresses 
        stresses_bar1 = compute_stress(bar1)
        # stresses_bar2 = compute_stress(bar2)

        draw_structure_on_canvas(canvas_frame, structure)
        draw_stress_on_canvas(canvas_frame2, bar1)
        draw_stress_on_canvas(canvas_frame3, bar2)
        draw_section_plot(resistance_canvas_frame, bar1)

        # Finding the section of maximum stress along the bar --> The index is the position along the bar
        proxy = abs(stresses_bar1[1]) + abs(stresses_bar1[2]) + abs(stresses_bar1[3])
        idx = np.argmax(proxy)
        
        # Update the label to show which is the most stressed section
        most_stressed_section_label.config(text=f"Most stressed section is at: {np.round(stresses_bar1[0][idx+1], 2)} (mm)", foreground="black")

        # Evaluate resistance check
        von_mises_stress, limit, _, _ = bar1.resistance_analysis(stresses_bar1[1][idx], stresses_bar1[2][idx], stresses_bar1[3][idx])
        if von_mises_stress < limit:
            # Update the label to show the result
            check_resistance_label.config(text=f"Resistance Check: PASS ✅\nVon Mises {np.round(von_mises_stress, 2)} (MPa) < {limit} (MPa) {bar1.material} yield strength", foreground="green")
        else:
            # Update the label to show the result
            check_resistance_label.config(text=f"Resistance Check: FAIL ❌\nVon Mises {np.round(von_mises_stress, 2)} (MPa) > {limit} (MPa) {bar1.material} yield strength", foreground="red") 

    # Tkinter interface
    root = tk.Tk()
    root.title("Visualizzatore Struttura Reticolare")
    root.geometry("800x600")  # Set initial window size here

    def on_closing():
        print("Window closed. Program terminated.")
        root.quit()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    alpha0 = 30
    l0 = 40
    h0 = l0*np.sin(np.deg2rad(alpha0))
    hmax = h0 + 20
    l_platform = 50
    p = 10

    width = 3  # mm
    height = 1 # mm

    # Initialaze the variables that are going to be used in the sliders
    alpha_var = tk.DoubleVar(value=alpha0)
    h_var = tk.DoubleVar(value=h0)
    l_var = tk.DoubleVar(value=l0)
    p_var = tk.DoubleVar(value=p)   

    width_var = tk.DoubleVar(value=width)
    height_var = tk.DoubleVar(value=height)

    width_thickness_var = tk.DoubleVar(value=0.0)
    height_thickness_var = tk.DoubleVar(value=0.0)
    
    # Enable resizing
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    mainframe = ttk.Frame(root, padding="10")
    mainframe.grid(row=0, column=0, sticky="nsew")
    mainframe.rowconfigure(0, weight=1)  # Top row (structure canvas)
    mainframe.columnconfigure(0, weight=2)  # Left column (structure, wider)
    mainframe.columnconfigure(1, weight=1)  # Right column (stress plots)

    # Create a canvas frame for the structure
    canvas_frame = ttk.Frame(mainframe)
    canvas_frame.grid(row=0, column=0, sticky="nsew")
    canvas_frame.rowconfigure(0, weight=1)
    canvas_frame.columnconfigure(0, weight=1)

    # Container frame for stress plots (right side)
    stress_container = ttk.Frame(mainframe)
    stress_container.grid(row=0, column=1, sticky="nsew")
    # Configure stress_container grid
    stress_container.rowconfigure(0, weight=1)  # Top stress plot
    stress_container.rowconfigure(1, weight=1)  # Bottom stress plot
    stress_container.columnconfigure(0, weight=1)  # Single column

    # Stress canvases inside container (stacked vertically)
    canvas_frame2 = ttk.Frame(stress_container)  # Top stress plot
    canvas_frame2.grid(row=0, column=0, sticky="nsew")

    canvas_frame3 = ttk.Frame(stress_container)  # Bottom stress plot
    canvas_frame3.grid(row=1, column=0, sticky="nsew")  

    # Create a frame for controls (below canvases)
    controls_frame = ttk.Frame(mainframe)
    controls_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)  # Span all columns
    # Configure controls_frame grid
    controls_frame.columnconfigure(0, weight=0)  # Label (no expansion)
    controls_frame.columnconfigure(1, weight=1)  # Slider (fills space)
    controls_frame.columnconfigure(2, weight=0)  # Entry (fixed width)

    resistance_frame = ttk.Frame(mainframe) # Check if root ormainframe
    resistance_frame.grid(row=0, column=2, sticky="nsew")  # Span all columns
    # Configure resistance frame grid
    resistance_frame.rowconfigure(0, weight=1)  # Top plot
    resistance_frame.rowconfigure(1, weight=1)  # Bottom stress plot
    resistance_frame.columnconfigure(0, weight=1)  # Single column

    # addframe for resistance
    resistance_canvas_frame = ttk.Frame(resistance_frame)  # Section Plot
    resistance_canvas_frame.grid(row=0, column=0, columnspan = 2,sticky="nsew")

    width_entry = ttk.Entry(resistance_frame, textvariable=width_var, font=("Arial", 24))
    width_entry.grid(row=1, column=1, sticky="ew", padx=5)
    
    width_label = ttk.Label(resistance_frame, text="Width (b) (mm):", font=("Arial", 24))
    width_label.grid(row=1, column=0, sticky="w", padx=5)
    
    height_label = ttk.Label(resistance_frame, text="Height (h) (mm):", font=("Arial", 24))
    height_label.grid(row=2, column=0, sticky="w", padx=5)

    height_entry = ttk.Entry(resistance_frame, textvariable=height_var, font=("Arial", 24)) 
    height_entry.grid(row=2, column=1, sticky="ew", padx=5)

   # Section type variable
    section_type = tk.StringVar(value="full")  # default selection

    # Label
    section_label = ttk.Label(resistance_frame, text="Section Type:", font=("Arial", 24))
    section_label.grid(row=3, column=0, sticky="w", padx=5, pady=10)

    # Radiobuttons
    rbtn_full = ttk.Radiobutton(resistance_frame, text="Full", variable=section_type, value="full")
    rbtn_hollow = ttk.Radiobutton(resistance_frame, text="Hollow", variable=section_type, value="hollow")

    rbtn_full.grid(row=3, column=1, sticky="w", padx=5)
    rbtn_hollow.grid(row=4, column=1, sticky="w", padx=5)

    # Thickness entries
    width_t_label = ttk.Label(resistance_frame, text="Width Thickness (t) (mm):", font=("Arial", 24))
    width_t_label.grid(row=5, column=0, sticky="w", padx=5)
    height_t_label = ttk.Label(resistance_frame, text="Height Thickness (t) (mm):", font=("Arial", 24))
    height_t_label.grid(row=6, column=0, sticky="w", padx=5)

    # Create entry fields for width and height
    width_thickness_entry = ttk.Entry(resistance_frame, textvariable=width_thickness_var, font=("Arial", 24))
    width_thickness_entry.grid(row=5, column=1, sticky="ew", padx=5)

    height_thickness_entry = ttk.Entry(resistance_frame, textvariable=height_thickness_var, font=("Arial", 24))
    height_thickness_entry.grid(row=6, column=1, sticky="ew", padx=5)
    
    # Show if the section is able to resist the load
    most_stressed_section_label = ttk.Label(resistance_frame, text="Most stressed section is at:", font=("Arial", 24))
    most_stressed_section_label.grid(row=7, column=0, columnspan=2, sticky="ew", pady=10)
    
    # Show if the section is able to resist the load
    check_resistance_label = ttk.Label(resistance_frame, text="Resistance Check ...", font=("Arial", 24))
    check_resistance_label.grid(row=8, column=0, columnspan=2, sticky="ew", pady=10)

    # Row 2: Length slider
    length_slider = ttk.Scale(controls_frame, from_=l0, to=2*l0, variable=l_var, orient='horizontal', command=update_structure_from_slider)
    length_label = ttk.Label(controls_frame, text="Length (l) (mm):", font=("Arial", 24))
    length_entry = ttk.Entry(controls_frame, textvariable=l_var, width=10, font=("Arial", 24))

    length_slider.grid(row=0, column=1, sticky="ew", padx=5)
    length_label.grid(row=0, column=0, sticky="w", padx=5)
    length_entry.grid(row=0, column=2, sticky="ew", padx=5)

    # Row 3: Alpha slider
    angle_slider = ttk.Scale(controls_frame, from_=10, to=80, variable=alpha_var, orient='horizontal', command=update_structure_from_slider)
    alpha_label = ttk.Label(controls_frame, text="Alpha angle (deg):", font=("Arial", 24))
    alpha_entry = ttk.Entry(controls_frame, textvariable=alpha_var, width=10, font=("Arial", 24))

    angle_slider.grid(row=1, column=1, sticky="ew", padx=5)
    alpha_label.grid(row=1, column=0, sticky="w", padx=5)
    alpha_entry.grid(row=1, column=2, sticky="ew", padx=5)

    # Row 4: h display (read-only)
    h_label = ttk.Label(controls_frame, text="Height (h) (mm):", font=("Arial", 24))
    h_entry = ttk.Entry(controls_frame, textvariable=h_var, font=("Arial", 24))

    h_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=5)
    h_entry.grid(row=2, column=2, sticky="e", padx=5)

    # Row 5: Load entry
    p_label = ttk.Label(controls_frame, text="P (Load on Platform) (N):", font=("Arial", 24))
    p_label.grid(row=3, column=0, columnspan=2, padx=5, sticky='w')

    p_entry = ttk.Entry(controls_frame, textvariable=p_var, font=("Arial", 24))
    p_entry.grid(row=3, column=2, padx=5, sticky='e')

    # Function to apply entry manually
    def apply_alpha_from_entry(*args):
        try:
            val = float(alpha_var.get())
            if 10 <= val <= 80:
                update_structure_from_slider(val)
            else:
                print("Alpha must be between 10 and 80.")
                show_temporary_message(mainframe=mainframe, message="Alpha must be between 10 and 80!", duration=2000)

        except ValueError:
            print("Invalid input for alpha.")
    
    def apply_h_from_entry(*args):
        try:
            h_val = float(h_var.get())
            l_val = l_var.get()
            if 0 < h_val < l_val:  # h must be less than l for sin to be valid
                alpha_deg = np.rad2deg(np.arcsin(h_val / l_val))
                alpha_var.set(alpha_deg)
                update_structure_from_slider()
            else:
                show_temporary_message(mainframe, "Invalid h: must be 0 < h < l", 2000)
        except ValueError:
            show_temporary_message(mainframe, "Invalid input for h", 2000)
    
    def apply_l_from_entry(*args):
        try:
            new_l = float(l_var.get())
            if new_l > 0:
                alpha_deg = float(alpha_var.get())
                new_h = new_l * np.sin(np.deg2rad(alpha_deg))
                h_var.set(new_h)
                update_structure_from_slider()
            else:
                show_temporary_message(mainframe, "l must be > 0", 2000)
        except ValueError:
            show_temporary_message(mainframe, "Invalid input for l", 2000)

    def apply_p_from_entry(*args):
        try:
            new_p = float(p_var.get())
            if new_p > 0:
                update_structure_from_slider()
            else:
                show_temporary_message(mainframe, "P must be > 0", 2000)
        except ValueError:
            show_temporary_message(mainframe, "Invalid input for P", 2000)

    def apply_width_from_entry(*args):
        try:
            new_width = float(width_var.get())
            if new_width > 0:
                update_structure_from_slider()
            else:
                show_temporary_message(mainframe, "Width must be > 0", 2000)
        except ValueError:
            show_temporary_message(mainframe, "Invalid input for Width", 2000)

    def apply_height_from_entry(*args): 
        try:
            new_height = float(height_var.get())
            if new_height > 0:
                update_structure_from_slider()
            else:
                show_temporary_message(mainframe, "Height must be > 0", 2000)
        except ValueError:
            show_temporary_message(mainframe, "Invalid input for Height", 2000)

    def apply_width_thickness_from_entry(*args):
        try:
            new_width_thickness = float(width_thickness_var.get())
            if new_width_thickness > 0:
                update_structure_from_slider()
            else:
                show_temporary_message(mainframe, "Width thickness must be > 0", 2000)
        except ValueError:
            show_temporary_message(mainframe, "Invalid input for Width thickness", 2000)

    def apply_height_thickness_from_entry(*args):
        try:
            new_height_thickness = float(height_thickness_var.get())
            if new_height_thickness > 0:
                update_structure_from_slider()
            else:
                show_temporary_message(mainframe, "Height thickness must be > 0", 2000)
        except ValueError:
            show_temporary_message(mainframe, "Invalid input for Height thickness", 2000)

    # Optional: bind Enter key in the Entry box
    alpha_entry.bind("<Return>", apply_alpha_from_entry)
    h_entry.bind("<Return>", apply_h_from_entry)
    length_entry.bind("<Return>", apply_l_from_entry)
    p_entry.bind("<Return>", apply_p_from_entry)
    width_entry.bind("<Return>", apply_width_from_entry)
    height_entry.bind("<Return>", apply_height_from_entry)
    width_thickness_entry.bind("<Return>", apply_width_thickness_from_entry)
    height_thickness_entry.bind("<Return>", apply_height_thickness_from_entry)
    
    # Bind <Configure> events
    canvas_frame.bind("<Configure>", lambda e: draw_structure_on_canvas(canvas_frame, structure))
    canvas_frame2.bind("<Configure>", lambda e: draw_stress_on_canvas(canvas_frame2, structure.bars[0]))
    canvas_frame3.bind("<Configure>", lambda e: draw_stress_on_canvas(canvas_frame3, structure.bars[1]))

    resistance_canvas_frame.bind("<Configure>", lambda e: draw_section_plot(resistance_canvas_frame, structure.bars[0]))
    

    
    # Draw initial structure based on default alpha (30)
    update_structure_from_slider(alpha_var.get())

    root.mainloop()


if __name__ == '__main__':
    main()

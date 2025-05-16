import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
from Structure_Analysis import Bar, Node
from tkinter import ttk

def show_temporary_message(mainframe, message, duration=2000):
    # Create a label to show the message
    message_label = ttk.Label(mainframe, text=message, foreground="red", font=("Arial", 18))
    message_label.grid(row=2, column=1, columnspan=2, pady=10, padx=5)
    
    # Hide the message after the specified duration (in milliseconds)
    mainframe.after(duration, lambda: message_label.grid_forget())

def draw_forces_on_canvas(ax, structure):
    for bar in structure.bars:
        # Iterate over forces applied at the fixed position
        for position, force in bar.load.items():
            Fx, Fy, M = force

            # Calculate the position on the bar where the forces are applied (fixed position)
            x_pos = bar.start_node.x + position * (bar.end_node.x - bar.start_node.x)
            y_pos = bar.start_node.y + position * (bar.end_node.y - bar.start_node.y)

            # Draw horizontal force (Fx) as an arrow
            if Fx != 0:
                # Draw the horizontal force (Fx) as an arrow
                ax.arrow(x_pos, y_pos, Fx * 0.5, 0, head_width=0.3, head_length=0.5, fc='red', ec='red')
                ax.text(x_pos + Fx * 0.5 + np.sign(Fx), y_pos, f'F_x={round(Fx,2)}N', fontsize=15, color='red')
            if Fy != 0: 
                # Draw vertical force (Fy) as an arrow
                ax.arrow(x_pos, y_pos, 0, Fy * 0.5, head_width=0.3, head_length=0.5, fc='red', ec='red')
                ax.text(x_pos, y_pos + Fy * 0.5 + np.sign(Fy), f'F_y={round(Fy,2)}N', fontsize=15, color='red')
            
            # If a moment M is applied, draw a moment arc at this point
            if M != 0:
                moment_radius = 1  # Adjust as needed
                angle = np.deg2rad(90)  # Moment direction (clockwise, counter-clockwise can be adjusted)

                # Draw the moment arc (representation of rotation)
                moment_arc = patches.Arc((x_pos, y_pos), width=moment_radius * 2, height=moment_radius * 2,
                                         angle=0, theta1=0, theta2=90, edgecolor='red', linestyle='-', linewidth=2)
                ax.add_patch(moment_arc)
                
                # Optionally, label the moment value
                ax.text(x_pos + moment_radius * np.cos(angle), y_pos + moment_radius * np.sin(angle), f'M={M}', fontsize=10, color='red')

def draw_structure_on_canvas(canvas_frame, structure):
    plt.close('all')  # Close all previous figures to prevent memory leaks
    # Close previous figures to prevent memory leaks
    for widget in canvas_frame.winfo_children():
        widget.destroy()

    # Get the current width and height of the canvas
    canvas_width = canvas_frame.winfo_width()
    canvas_height = canvas_frame.winfo_height()
    
    # Create a new figure with the size of the canvas
    fig, ax = plt.subplots(figsize=(canvas_width / 100, canvas_height / 100))  # Size in inches, 100 dpi

    for bar in structure.bars:
        x_vals = [bar.start_node.x, bar.end_node.x]
        y_vals = [bar.start_node.y, bar.end_node.y]
        ax.plot(x_vals, y_vals, 'bo-')

        # Placing the label of the start node
        # bar.info()
        if round(bar.start_node.y,2) == 0:
            ax.text(bar.start_node.x, bar.start_node.y - 1.5, s=f"{bar.start_node.id}", fontsize=12, color='green')
        else:
            ax.text(bar.start_node.x, bar.start_node.y + 1, s=f"{bar.start_node.id}", fontsize=12, color='green')
        
        # Placing the label of the end node
        if round(bar.end_node.y,2) == 0:
            ax.text(bar.end_node.x, bar.end_node.y - 1.5, s=f"{bar.end_node.id}", fontsize=12, color='green')   
        else:
            ax.text(bar.end_node.x, bar.end_node.y + 1, s=f"{bar.end_node.id}", fontsize=12, color='green')
        
    # Draw the forces on the bars (custom function)
    draw_forces_on_canvas(ax, structure)

    ax.axhline(y=0, color='brown', linestyle='--', linewidth=1)
    ax.set_aspect('equal')
    ax.set_title("Structure Analysis")
    ax.grid(True)
    ax.set_xlabel("Length (m)")
    if structure.bars[0].length <= 20:
        ax.set_xlim(-5, 25)
        ax.set_ylim(-2, 20)
    else:
        ax.set_xlim(-5, structure.bars[0].length + 5)
        ax.set_ylim(-2, structure.bars[0].length + 5)

    for widget in canvas_frame.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=canvas_frame)

    # Example angle in degrees
    angle = structure.bars[0].alpha if structure.bars else 30  # fallback if not defined

    # Create an arc (start angle 0°, sweep 'angle' degrees counter-clockwise)
    arc = patches.Arc((0, 0), width=6, height=6, theta1=0, theta2=angle,
                      edgecolor='purple', linestyle='-', linewidth=2)
    ax.add_patch(arc)

    # Add alpha symbol label
    ax.text(3, 0.2, r'$\alpha$', fontsize=14, color='purple')

    plt.tight_layout()
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)

def draw_stress_on_canvas(canvas_frame, bar: Bar):
    """Draw the stress on the canvas for a given bar.
    Args:
        canvas_frame (tk.Frame): The frame where the canvas is located.
        bar (Bar): The bar object containing the properties."""
    
    # Close previous figures to prevent memory leaks
    for widget in canvas_frame.winfo_children():
        widget.destroy()

    # Unpack the stress list
    x_data, shear_stress, normal_stress, flexion_stress = compute_stress(bar)

    # Get the current width and height of the canvas
    canvas_width = canvas_frame.winfo_width()
    canvas_height = canvas_frame.winfo_height()
    
    # Create a new figure with the size of the canvas
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(canvas_width / 100, canvas_height / 100))
    fig.subplots_adjust(hspace=0.8)  # Adjust space between subplots

    arrow_up, arrow_down, arrow_r, arrow_l, arrow_mr, arrow_ml = draw_arrow(bar)

    ax1.add_patch(arrow_down)
    ax1.add_patch(arrow_up)
    ax1.plot([0, bar.length], [0, 0], color='black', linewidth=3)
    ax1.plot(x_data, shear_stress)
    ax1.set_title(f"Shear in Bar {bar.start_node.id}{bar.end_node.id}")
    ax1.set_ylabel("Shear Stress (N)")
    ax1.fill_between(x_data, shear_stress, where=(shear_stress > 0), color='skyblue', alpha=0.4, label='Shear Stress Positive')
    ax1.fill_between(x_data, shear_stress, where=(shear_stress < 0), color='salmon', alpha=0.4, label='Shear Stress Negative')
    ax1.text(-2, 0.2, f"{bar.start_node.id}", fontsize=10, color='green')
    ax1.text(bar.length + 2, 0.2, f"{bar.end_node.id}", fontsize=10, color='green')
    ax1.grid(True)

    ax2.add_patch(arrow_l)
    ax2.add_patch(arrow_r)
    ax2.plot([0, bar.length], [0, 0], color='black', linewidth=3)
    ax2.plot(x_data, normal_stress)
    ax2.set_title(f"Normal tension in Bar {bar.start_node.id}{bar.end_node.id}")
    ax2.set_ylabel("Normal Stress (N)")
    ax2.fill_between(x_data, normal_stress, where=(normal_stress > 0), color='skyblue', alpha=0.4, label='Normal Stress Positive')
    ax2.fill_between(x_data, normal_stress, where=(normal_stress < 0), color='salmon', alpha=0.4, label='Normal Stress Negative')
    ax2.text(-2, 0.2, f"{bar.start_node.id}", fontsize=10, color='green')
    ax2.text(bar.length + 2, 0.2, f"{bar.end_node.id}", fontsize=10, color='green')
    ax2.grid(True)

    ax3.add_patch(arrow_mr)
    ax3.add_patch(arrow_ml)
    ax3.plot([0, bar.length], [0, 0], color='black', linewidth=3)
    ax3.plot(x_data, flexion_stress)
    ax3.set_title(f"flexion tension in Bar {bar.start_node.id}{bar.end_node.id}")
    ax3.set_ylabel("flexion Stress (N)")
    ax3.fill_between(x_data, flexion_stress, where=(flexion_stress > 0), color='skyblue', alpha=0.4, label='flexion Stress Positive')
    ax3.fill_between(x_data, flexion_stress, where=(flexion_stress < 0), color='salmon', alpha=0.4, label='flexion Stress Negative')
    ax3.text(-2, 0.2, f"{bar.start_node.id}", fontsize=10, color='green')
    ax3.text(bar.length + 2, 0.2, f"{bar.end_node.id}", fontsize=10, color='green')
    ax3.grid(True)

    canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)
    
def compute_stress(bar: Bar) -> list:
    """Compute the stress in a bar given the loads applied to it.
    Args:
        bar (Bar): The bar object containing the loads and properties.
    Returns:
        list: x_data, shear_stress, normal_stress, flexion_stress"""
    n_samples = 100
    x_data = np.linspace(0, bar.length, n_samples) # 100 points from 0 to bar.length
    # Calculate shear stress
    shear_stress = np.zeros(len(x_data))
    normal_stress = np.zeros(len(x_data))
    flexion_stress = np.zeros(len(x_data))

    p_list = []
    forces_list = []
    for pos, forces in bar.load.items():
        forces_list.append(forces)
        p_list.append(pos)

    for i, p in enumerate(p_list):
        fx = forces_list[i][0]
        fy = forces_list[i][1]

        # Find the index of the position in x_data --> where the load is applied
        # The stresses are then computed by cumulating the stress from that point to the end of the bar
        try:
            index = [int(p*(n_samples - 1))] # x_data is a list of samples, so we multiply by the relative position to find the index
        except ValueError:
            print("Element not found in the list")

        # Compute shear stress
        shear_stress[index[0]:] = shear_stress[index[0]] + fy*np.cos(np.deg2rad(bar.alpha)) - fx*np.sin(np.deg2rad(bar.alpha))
        # Compute normal stress
        normal_stress[index[0]:] = normal_stress[index[0]] - fx*np.cos(np.deg2rad(bar.alpha)) - fy*np.sin(np.deg2rad(bar.alpha))
        # Compute flexion stress
        flexion_stress[index[0]:] += (fy*np.cos(np.deg2rad(bar.alpha)) - fx*np.sin(np.deg2rad(bar.alpha))) * (x_data[index[0]:] - p*bar.length)
    
    return [x_data, shear_stress, normal_stress, flexion_stress]

def draw_arrow(bar: Bar):
    """Draw arrows to indicate the direction of forces and moments on the bar.
    Args:
        bar (Bar): The bar object containing the properties.
    Returns:
        tuple: arrow_up, arrow_down, arrow_r, arrow_l, arrow_mr, arrow_ml"""
    arrow_up = FancyArrowPatch(
    posA=(bar.length + 1, -1),       # Start point
    posB=(bar.length + 1, 1),       # End point
    arrowstyle="simple", # Styles: "simple", "wedge", etc.
    mutation_scale=10,  # Controls head size
    color="purple",
    lw=2,
    )
    arrow_down = FancyArrowPatch(
    posA=(-2, 1),       # Start point
    posB=(-2, -1),       # End point
    arrowstyle="simple", # Styles: "simple", "wedge", etc.
    mutation_scale=10,  # Controls head size
    color="purple",
    lw=2,
    )
    arrow_r = FancyArrowPatch(
    posA=(bar.length + 1, 0),       # Start point
    posB=(bar.length + 6, 0),       # End point
    arrowstyle="simple", # Styles: "simple", "wedge", etc.
    mutation_scale=10,  # Controls head size
    color="purple",
    lw=2,
    )
    arrow_l = FancyArrowPatch(
    posA=(-1, 0),       # Start point
    posB=(-6, 0),       # End point
    arrowstyle="simple", # Styles: "simple", "wedge", etc.
    mutation_scale=10,  # Controls head size
    color="purple",
    lw=2,
    )
    arrow_mr = FancyArrowPatch(
    posA=(-1, -1),       # Start point
    posB=(-1, 1),       # End point
    arrowstyle="simple", # Styles: "simple", "wedge", etc.
    mutation_scale=10,  # Controls head size
    connectionstyle="arc3,rad=-0.8", # Arc style
    color="purple",
    lw=2,
    )
    arrow_ml = FancyArrowPatch(
    posA=(bar.length + 1, -1),     # Start point
    posB=(bar.length + 1, 1),      # End point
    arrowstyle="simple", # Styles: "simple", "wedge", etc.
    mutation_scale=10,  # Controls head size
    connectionstyle="arc3,rad=0.8", # Arc style
    color="purple",
    lw=2,
    )
    return arrow_up, arrow_down, arrow_r, arrow_l, arrow_mr, arrow_ml

def resistance_analysis(bar: Bar):
    """Compute the resistance of a bar given the loads applied to it.
    Args:
        bar (Bar): The bar object containing the loads and properties."""
    
    # Compute the stresses in the bar
    x_data, shear_stress, normal_stress, flexion_stress = compute_stress(bar)

    # Calculate the maximum stress values
    max_shear_stress = np.max(np.abs(shear_stress))
    max_normal_stress = np.max(np.abs(normal_stress))
    max_flexion_stress = np.max(np.abs(flexion_stress))

    sigma = max_normal_stress/bar.sectional_area() + max_flexion_stress/bar.moment_of_inertia()
    tau = (max_shear_stress * bar.static_moment()) / (bar.moment_of_inertia() * bar.height)
    # Von Mises stress calculation
    von_mises_stress = np.sqrt(max_normal_stress**2 + 3 * max_shear_stress**2)

    return max_shear_stress, max_normal_stress, max_flexion_stress

def draw_section_plot(canvas_frame, bar: Bar):
    """Draw the section plot of a bar."""
    # Close all previous figures to prevent memory leaks
    plt.close('all')  # Close all previous figures to prevent memory leaks
    # Close previous figures to prevent memory leaks
    for widget in canvas_frame.winfo_children():
        widget.destroy()

    canvas_width = canvas_frame.winfo_width() 
    canvas_height = canvas_frame.winfo_height()

    # Get the current width and height of the canvas_frame
    width = bar.width
    height = bar.height
    hollow = bar.hollow
    width_thickness = bar.width_thickness
    height_thickness = bar.height_thickness
    radius = bar.radius
    # Create a new figure with the size of the canvas_frame
    fig, ax = plt.subplots(figsize=(canvas_width / 100, canvas_height / 100))  # Size in inches, 100 dpi

    if bar.section == "rectangular":
        # # Draw a rectangle for the section
        # outside_rect = patches.Rectangle((-width/2, -height/2), width, height, linewidth=1, edgecolor='black', facecolor='lightgrey')
        # inside_rect = patches.Rectangle((-width/2 + width_thickness, -height/2 + height_thickness), width - 2*width_thickness, height - 2*height_thickness, linewidth=1, edgecolor='black', facecolor='white')
        # ax.add_patch(outside_rect)
        # ax.add_patch(inside_rect)
        # Draw a rectangle centered at origin
        outside_rect = patches.Rectangle((-width/2, -height/2), width, height, linewidth=1, edgecolor='black', facecolor='lightgrey')
        ax.add_patch(outside_rect)

        if hollow:
            inner_w = width - 2 * width_thickness
            inner_h = height - 2 * height_thickness
            if inner_w > 0 and inner_h > 0:
                inside_rect = patches.Rectangle((-inner_w/2, -inner_h/2), inner_w, inner_h, linewidth=1, edgecolor='black', facecolor='white')
                ax.add_patch(inside_rect)

        # Set symmetric limits
        margin = max(width, height) * 0.2
        ax.set_xlim(-width/2 - margin, width/2 + margin)
        ax.set_ylim(-height/2 - margin, height/2 + margin)

    elif bar.section == "circular":
        # # Draw a circle for the section
        # outer_circle = patches.Circle((0, 0), radius=radius, linewidth=1, edgecolor='black', facecolor='lightgrey')
        # inner_circle = patches.Circle((0, 0), radius=radius - width_thickness, linewidth=1, edgecolor='black', facecolor='white')
        # ax.add_patch(outer_circle)
        # ax.add_patch(inner_circle)
        outer_circle = patches.Circle((0, 0), radius=radius, linewidth=1, edgecolor='black', facecolor='lightgrey')
        ax.add_patch(outer_circle)

        if hollow and (radius - width_thickness) > 0:
            inner_circle = patches.Circle((0, 0), radius=radius - width_thickness, linewidth=1, edgecolor='black', facecolor='white')
            ax.add_patch(inner_circle)

        margin = radius * 0.2
        ax.set_xlim(-radius - margin, radius + margin)
        ax.set_ylim(-radius - margin, radius + margin)

    
    # Draw the section plot here
    # Set symmetric limits
    ax.set_title("Section Plot")
    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.set_aspect('equal', 'box')
    
    canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)
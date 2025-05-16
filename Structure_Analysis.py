import numpy as np
import matplotlib.pyplot as plt 
import pandas as pd
import os
import scipy   


class Node:
    def __init__(self, id: str, x: float, y: float):
        """
        Initialize a Node object with given coordinates.
        Parameters:
        - id: Unique identifier for the node.
        - x: X-coordinate of the node.
        - y: Y-coordinate of the node.
        """
        self.id = id
        self.x = x
        self.y = y 

class Bar:
    def __init__(self, length: float= 0.0, width: float = 0.0, height: float = 0.0, radius: float = None, hollow: bool = False, section: str = 'rectangular', 
                width_thickness: float = 0, height_thickness: float = 0, material: str = 'steel',
                alpha: float = 0.0, start_node: Node = Node("1", 0, 0), end_node: Node = Node("2", 0, 10)):
        """
        Initialize a Bar object with given dimensions and properties.
        Parameters:
        - length: Length of the bar.
        - width: Width of the bar section.
        - height: Height of the bar section.
        - hollow: Boolean indicating if the bar is hollow (True) or solid (False).
        - section: Type of the bar section ('rectangular' or 'circular').
        if circular, width is considered as the diameter of the hollow section.
        - width_thickness: Thickness of the width for hollow sections (default is 0).
        - height_thickness: Thickness of the height for hollow sections (default is 0).
        - material: Material of the bar (default is steel).
        - alpha: Angle of the bar in degrees respect to the horizontal (default is 0).
        - start_node: Node object representing the start node of the bar.
        - end_node: Node object representing the end node of the bar.

        """

        self.length = length
        self.width = width
        self.height = height
        self.hollow = hollow
        self.alpha = alpha
        self.load = {}
        

        if section not in ['rectangular', 'circular']:
            raise ValueError("section must be either 'rectangular' or 'circular'")
        self.section = section

        # Set the radius for circular sections  
        self.radius = radius
        
        self.width_thickness = width_thickness
        self.height_thickness = height_thickness
        
        self.material = material
        self.material_density = None
        self.start_node = start_node
        self.end_node = end_node
        
        self.get_material_density() 

    
    def start(self, start_node: Node):
        """
        Set the start node of the bar.
        Parameters:
        - start_node: Node object representing the start node of the bar.
        """
        self.start_node = start_node  

    def end(self, end_node: Node = None):
        """
        Set the end node of the bar.
        If end_node is not provided, it will be calculated based on the start node, length, and angle.
        Parameters:
        - end_node: Node object representing the end node of the bar.
        """
        if end_node is None:
            if self.start_node.id is None or self.start_node.id == "":
                id_ = ""
            else:
                id_ = chr(ord(self.start_node.id) + 1)
            end_node = Node(id = id_, x = self.start_node.x + self.length * np.cos(np.radians(self.alpha)), y = self.start_node.y + self.length * np.sin(np.radians(self.alpha)))
        self.end_node = end_node
        # self.check_on_length()
    
    def set_length(self, new_length: float):
        """
        Set the length of the bar and recalculate the end node coordinates.
        Parameters:
        - new_length: New length of the bar.
        """
        self.length = new_length
        self._recalculate_nodes_from_alpha()

    def set_alpha(self, alpha_deg: float):
        """
        Set the angle of the bar in degrees and recalculate the end node coordinates.
        Parameters:
        - alpha_deg: Angle of the bar in degrees.
        """
        self.alpha = alpha_deg
        self._recalculate_nodes_from_alpha()

    def set_h(self, h_val: float):
        """
        Set the height of the bar and recalculate the angle.
        Parameters:
        - h_val: Height of the bar.
        """
        if self.length == 0:
            raise ValueError("Cannot compute alpha with zero length.")
        self.alpha = np.degrees(np.arcsin(h_val / self.length))
        self._recalculate_nodes_from_alpha()

    def _recalculate_nodes_from_alpha(self):
        """Update end_node coordinates based on length and alpha."""
        self.end_node.x = self.start_node.x + self.length * np.cos(np.radians(self.alpha))
        self.end_node.y = self.start_node.y + self.length * np.sin(np.radians(self.alpha))

    def get_height(self):
        """Return the vertical projection (h = l * sin(alpha))"""
        return self.length * np.sin(np.radians(self.alpha))

    def check_on_length(self):
        """
        Check if the bar is within the specified length.
        """
        
        if self.length <= 0:
            raise ValueError("Length must be greater than zero.")
        if self.width <= 0:
            raise ValueError("Width must be greater than zero.")
        if self.height <= 0:
            raise ValueError("Height must be greater than zero.")
        if self.start_node.x == self.end_node.x and self.start_node.y == self.end_node.y:
            raise ValueError("Start and end nodes cannot be the same.")
        
        l = round(np.sqrt((self.end_node.x - self.start_node.x)**2 + (self.end_node.y - self.start_node.y)**2), 3) # Round to 3 decimal places to avoid floating point errors
        if l != self.length:
            raise ValueError("Length of the bar ({}) does not match the distance between start and end nodes ({}).".format(self.length, l))
        print(f"Bar length is valid: {self.length} mm")
        print(f"Start Node: {self.start_node.id} ({self.start_node.x}, {self.start_node.y})")
        print(f"End Node: {self.end_node.id} ({self.end_node.x}, {self.end_node.y})")

    def volume(self):
        """
        Calculate the volume of the bar based on its dimensions and whether it is hollow or solid.
        """
        if self.section == 'rectangular':
            if self.hollow:
                outer_volume = self.length * self.width * self.height
                inner_volume = (self.length * (self.width - self.width_thickness*2) * (self.height - self.height_thickness*2))
                return outer_volume - inner_volume
            else:
                return self.length * self.width * self.height
        elif self.section == 'circular':
            if self.hollow:
                outer_volume = np.pi * (self.radius ** 2) * self.length
                inner_volume = np.pi * ((self.radius - self.width_thickness) ** 2) * self.length
                return outer_volume - inner_volume
            else:
                return np.pi * (self.radius ** 2) * self.length
        return self.length * self.width * self.height
    
    def mass(self):
        return self.volume() * self.material_density * 10**-6  # Convert from mm^3 to m^3 for density calculation
    
    def sectional_area(self):
        """
        Calculate the sectional area of the bar based on its dimensions and whether it is hollow or solid.
        Parameters:
        - width_thickness: Thickness of the width for hollow sections (default is 0).
        - height_thickness: Thickness of the height for hollow sections (default is 0).
        if circular, width_thickness is considered as the thickness of the section.
        """
        if self.section == 'rectangular':
            if self.hollow:
                outer_area = self.width * self.height
                inner_area = (self.width - self.width_thickness*2) * (self.height - self.height_thickness*2)
                return outer_area - inner_area
            else:
                return self.length * self.width
            
        elif self.section == 'circular':
            if self.hollow:
                outer_area = np.pi * (self.radius ** 2)
                inner_area = np.pi * ((self.radius - self.width_thickness) ** 2)
                return outer_area - inner_area
            else:
                return np.pi * (self.radius ** 2)
        else:
            raise ValueError("section must be either 'rectangular' or 'circular'")
        
    def moment_of_inertia(self):
        """
        Calculate the moment of inertia of the bar based on its dimensions and whether it is hollow or solid.
        """
        if self.section == 'rectangular':
            if self.hollow:
                outer_inertia = (self.width * self.height ** 3) / 12
                inner_inertia = ((self.width - self.width_thickness*2) * (self.height - self.height_thickness*2) ** 3) / 12
                return outer_inertia - inner_inertia
            else:
                return (self.width * self.height ** 3) / 12
            
        elif self.section == 'circular':
            if self.hollow:
                outer_inertia = (np.pi * (self.radius ** 4)) / 4
                inner_inertia = (np.pi * ((self.radius - self.width_thickness) ** 4)) / 4
                return outer_inertia - inner_inertia
            else:
                return (np.pi * (self.radius ** 4)) / 4
        else:
            raise ValueError("section must be either 'rectangular' or 'circular'")
        
    def static_moment(self):
        """
        Calculate the static moment of the bar based on its dimensions and whether it is hollow or solid.
        """
        if self.section == 'rectangular':
            if self.hollow:
                return ((self.width* self.height ** 3) - ((self.width - self.width_thickness*2) * (self.height - self.height_thickness) ** 3)) / (6 * self.height)
            else:
                return (self.width * self.height ** 2) / 6
            
        elif self.section == 'circular':
            if self.hollow:
                return (np.pi * ((2*self.radius)**4 - (2*(self.radius - self.width_thickness))**4))/(32*2*self.radius)
            else:
                return (np.pi * (self.radius ** 3)) / 4
        else:
            raise ValueError("section must be either 'rectangular' or 'circular'")
        
    def add_load(self, position: float, fx: float, fy: float, m: float):
        """Add a load to the bar at a specified position.
        Args:
            position: Position of the load in the bar based on the length of itself.
            fx: Force in the x direction.
            fy: Force in the y direction.
            m: Moment.
        """
        if position < 0 or position > self.length:
            raise ValueError("Position must be within the length of the bar.")
        self.load[position] = [fx, fy, m]

    def resistance_analysis(self, n, t, m, yield_strength: float = None) -> tuple :
        """
        Perform resistance analysis on the bar.
        Args:
            n: Normal force applied on the section with maximum stress.
            t: Shear force applied on the section with maximum stress.
            m: Moment applied on the section with maximum stress.
            yield_strength: Yield strength of the material in Pa (optional).
        Returns:
            tuple: Von Mises stress, yield strength, normal stress, and shear stress.
        """
        if self.section == 'rectangular':
            if self.hollow:
                b = self.width_thickness
            else:
                b = self.width
        if self.section == 'circular':
            if self.hollow:
                b = self.width_thickness
            else:
                b = 2*self.radius

        sigma = n / self.sectional_area() + m / self.moment_of_inertia() # Normal Stress
        tau = (t * self.static_moment()) / (self.moment_of_inertia() * b) # Shear stress

        # Von Mises stress
        von_mises_stress = np.sqrt(sigma**2 + 3*tau**2)

        # Yield strength of the material
        if yield_strength is None:
            yield_strength = self.get_material_yield_strength()

        if von_mises_stress > yield_strength or von_mises_stress == None:
            print(f"Warning: The bar is yielding! Von Mises stress: {von_mises_stress:.2f} MPa, Yield strength: {yield_strength:.2f} MPa")
        else:
            print(f"The bar is safe. Von Mises stress: {von_mises_stress:.2f} MPa, Yield strength: {yield_strength:.2f} MPa")
        return von_mises_stress, yield_strength, sigma, tau


    def get_material_density(self):
        """
        Get the material density based on the material type.
        """
        material_densities = {
            'steel': 7850,  # kg/m^3
            'aluminum': 2700,  # kg/m^3
            'concrete': 2400,  # kg/m^3
            'wood': 600,  # kg/m^3
            'plastic': 950,  # kg/m^3
            'abs': 1050,  # kg/m^3
        }
        self.material_density = material_densities.get(self.material.lower())
        if self.material_density is None:
            raise ValueError(f"Material '{self.material}' not recognized. Please use one of the following: {', '.join(material_densities.keys())}")
        
    def get_material_yield_strength(self):
        """
        Get the yield strength of the material based on the material type.
        """
        material_yield_strengths = {
            'steel': 250,  # MPa
            'aluminum': 70,  # MPa
            'concrete': 30,  # MPa
            'wood': 40,  # MPa
            'plastic': 20,  # MPa
            'abs': 50,  # MPa
        }
        return material_yield_strengths.get(self.material.lower())
        
    def info(self):
        """
        Print the properties of the bar.
        """
        print(f"Bar Properties:")
        print(f"Length: {self.length} mm")
        print(f"Node Start: {self.start_node.id} ({self.start_node.x}, {self.start_node.y})")
        print(f"Node End: {self.end_node.id} ({self.end_node.x}, {self.end_node.y})")
        print(f"Section: {self.section}")
        if self.section == 'circular':
            print(f"Radius: {self.radius} mm")
        else:
            print(f"Width: {self.width} mm")
            print(f"Height: {self.height} mm")
        print(f"hollow: {self.hollow}")
        if self.hollow:
            print(f"Width Thickness: {self.width_thickness} mm")
            print(f"Height Thickness: {self.height_thickness} mm")
        print(f"Volume: {self.volume()} mm^3")
        print(f"Material: {self.material}")
        print(f"Material Density: {self.material_density} kg/m^3")
        print(f"Mass: {self.mass()} kg")
        print(f"Sectional Area: {self.sectional_area()} mm^2")
        print(f"Moment of Inertia: {self.moment_of_inertia()} mm^4")

        print(f"Angle: {self.alpha} degrees")
        print(f"Load:")
        print(f"{'Position (mm)':>14} | {'Fx (N)':>8} | {'Fy (N)':>8} | {'M (Nmm)':>10}")
        for position, (fx, fy, m) in self.load.items():
            print(f"{position:14.2f} | {fx:8.2f} | {fy:8.2f} | {m:10.2f}")
        print("===================================")


# Structure class
# This class is used to create a structure with multiple bars.
class Structure:
    def __init__(self, name: str):
        """
        Initialize a Structure object with a name and a bar.
        Parameters:
        - name: Name of the structure.
        - bars: list of Bar objects .
        """
        self.name = name
        self.bars = []
        
    def add_bar(self, bar: Bar):
        """
        Add a bar to the structure.
        Parameters:
        - bar: Bar object to be added.
        """
        if not isinstance(bar, Bar):
            raise ValueError("bar must be an instance of the Bar class.")
        self.bars.append(bar)
        
    def info(self):
        """
        Print the properties of the structure and its associated bar.
        """
        print(f"Structure Name: {self.name}")
        for bar in self.bars:
            bar.info()


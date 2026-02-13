"""
Manual VTK writer for Kratos results
This ensures each time step gets written with correct displacement data
"""

import KratosMultiphysics
import os


def write_vtk_step(model_part, output_dir, step_number, file_prefix="result"):
    """
    Manually write a VTK file for a single time step
    
    Parameters:
    -----------
    model_part : KratosMultiphysics.ModelPart
        The model part containing the mesh and results
    output_dir : str
        Directory to save VTK files
    step_number : int
        Step number for filename
    file_prefix : str
        Prefix for the filename
    """
    import os
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create filename
    filename = os.path.join(output_dir, f"{file_prefix}_{step_number}.vtk")
    
    # Open file for writing
    with open(filename, 'w') as f:
        # Write VTK header
        f.write("# vtk DataFile Version 3.0\n")
        f.write(f"Kratos Results - Step {step_number}\n")
        f.write("ASCII\n")
        f.write("DATASET UNSTRUCTURED_GRID\n")
        
        # Write points (nodes)
        num_nodes = model_part.NumberOfNodes()
        f.write(f"POINTS {num_nodes} float\n")
        
        # Store node IDs for element connectivity
        node_id_map = {}
        node_index = 0
        
        for node in model_part.Nodes:
            x = node.X
            y = node.Y
            z = node.Z
            f.write(f"{x} {y} {z}\n")
            node_id_map[node.Id] = node_index
            node_index += 1
        
        # Write cells (elements)
        num_elements = model_part.NumberOfElements()
        
        # Count total size needed for cell list
        cell_list_size = 0
        for element in model_part.Elements:
            num_nodes_in_element = len(element.GetNodes())
            cell_list_size += 1 + num_nodes_in_element  # 1 for count + node IDs
        
        f.write(f"\nCELLS {num_elements} {cell_list_size}\n")
        
        for element in model_part.Elements:
            nodes = element.GetNodes()
            f.write(f"{len(nodes)}")
            for node in nodes:
                f.write(f" {node_id_map[node.Id]}")
            f.write("\n")
        
        # Write cell types
        f.write(f"\nCELL_TYPES {num_elements}\n")
        for element in model_part.Elements:
            num_nodes_in_element = len(element.GetNodes())
            # VTK cell type codes
            if num_nodes_in_element == 2:
                cell_type = 3  # VTK_LINE
            elif num_nodes_in_element == 3:
                cell_type = 5  # VTK_TRIANGLE
            elif num_nodes_in_element == 4:
                cell_type = 9  # VTK_QUAD
            elif num_nodes_in_element == 8:
                cell_type = 12  # VTK_HEXAHEDRON
            else:
                cell_type = 7  # VTK_POLYGON (generic)
            f.write(f"{cell_type}\n")
        
        # Write point data (nodal results)
        f.write(f"\nPOINT_DATA {num_nodes}\n")
        
        # Write displacement vectors
        f.write("VECTORS DISPLACEMENT float\n")
        for node in model_part.Nodes:
            disp = node.GetSolutionStepValue(KratosMultiphysics.DISPLACEMENT)
            f.write(f"{disp[0]} {disp[1]} {disp[2]}\n")
        
        # Write displacement magnitude as scalar
        f.write("\nSCALARS DISPLACEMENT_MAGNITUDE float 1\n")
        f.write("LOOKUP_TABLE default\n")
        for node in model_part.Nodes:
            disp = node.GetSolutionStepValue(KratosMultiphysics.DISPLACEMENT)
            mag = (disp[0]**2 + disp[1]**2 + disp[2]**2)**0.5
            f.write(f"{mag}\n")
        
        # Write reactions if available
        try:
            f.write("\nVECTORS REACTION float\n")
            for node in model_part.Nodes:
                react = node.GetSolutionStepValue(KratosMultiphysics.REACTION)
                f.write(f"{react[0]} {react[1]} {react[2]}\n")
        except:
            pass  # REACTION not available
        
        # Write rotations if available (for beam/shell elements)
        try:
            f.write("\nVECTORS ROTATION float\n")
            for node in model_part.Nodes:
                rot = node.GetSolutionStepValue(KratosMultiphysics.ROTATION)
                f.write(f"{rot[0]} {rot[1]} {rot[2]}\n")
        except:
            pass  # ROTATION not available
    
    print(f"    Written: {filename}")
    return filename


def write_vtk_series(model_part, output_dir, num_steps, file_prefix="result"):
    """
    Write a series of VTK files
    Useful when you want to write multiple time steps
    """
    files_written = []
    for step in range(num_steps):
        filename = write_vtk_step(model_part, output_dir, step, file_prefix)
        files_written.append(filename)
    return files_written
import KratosMultiphysics
import KratosMultiphysics.StructuralMechanicsApplication as StructuralMechanicsApplication
from KratosMultiphysics import kratos_utilities
import vtk_writer

if kratos_utilities.CheckIfApplicationsAvailable("LinearSolversApplication"):
    from KratosMultiphysics import LinearSolversApplication
else:
    raise ImportError("LinearSolversApplication is required but not available")


class PrebucklingAnalysis:
    """
    Prebuckling analysis of a simply supported square plate under compressive loading.
    Full plate model (2m × 2m).
    Reference solution from ABAQUS (element S4R):
    http://130.149.89.49:2080/v6.8/books/bmk/default.htm?startat=ch01s02ach17.html
    """
    
    def __init__(self):
        self.current_model = KratosMultiphysics.Model()
        self.mp = None
        
    def add_dofs(self, mp):
        """Add degrees of freedom and their corresponding reactions"""
        KratosMultiphysics.VariableUtils().AddDof(KratosMultiphysics.DISPLACEMENT_X, KratosMultiphysics.REACTION_X, mp)
        KratosMultiphysics.VariableUtils().AddDof(KratosMultiphysics.DISPLACEMENT_Y, KratosMultiphysics.REACTION_Y, mp)
        KratosMultiphysics.VariableUtils().AddDof(KratosMultiphysics.DISPLACEMENT_Z, KratosMultiphysics.REACTION_Z, mp)
        KratosMultiphysics.VariableUtils().AddDof(KratosMultiphysics.ROTATION_X, KratosMultiphysics.REACTION_MOMENT_X, mp)
        KratosMultiphysics.VariableUtils().AddDof(KratosMultiphysics.ROTATION_Y, KratosMultiphysics.REACTION_MOMENT_Y, mp)
        KratosMultiphysics.VariableUtils().AddDof(KratosMultiphysics.ROTATION_Z, KratosMultiphysics.REACTION_MOMENT_Z, mp)

    def add_variables(self, mp):
        """Add solution step variables"""
        mp.AddNodalSolutionStepVariable(KratosMultiphysics.DISPLACEMENT)
        mp.AddNodalSolutionStepVariable(KratosMultiphysics.REACTION)
        mp.AddNodalSolutionStepVariable(KratosMultiphysics.REACTION_MOMENT)
        mp.AddNodalSolutionStepVariable(KratosMultiphysics.ROTATION)

    def create_nodes(self, mp, num_nodes, length):
        """Create nodes for the plate mesh"""
        counter = 0
        for y in range(num_nodes):
            for x in range(num_nodes):
                counter += 1
                x_coord = x / (num_nodes - 1) * length
                y_coord = y / (num_nodes - 1) * length
                mp.CreateNewNode(counter, x_coord, y_coord, 0.0)

    def create_elements(self, mp, num_nodes):
        """Create shell elements for the plate"""
        element_name = "ShellThinElementCorotational3D4N"
        counter = 0
        for y in range(num_nodes - 1):
            for x in range(num_nodes - 1):
                counter += 1
                # Nodes aligned counter-clockwise
                node1 = num_nodes * y + (x + 1)
                node2 = num_nodes * y + (x + 2)
                node3 = num_nodes * (y + 1) + (x + 2)
                node4 = num_nodes * (y + 1) + (x + 1)
                mp.CreateNewElement(element_name, counter, [node1, node2, node3, node4], mp.GetProperties()[0])

    def apply_material_properties(self, mp):
        """Define material properties for the plate"""
        mp.GetProperties()[0].SetValue(KratosMultiphysics.YOUNG_MODULUS, 1e8)
        mp.GetProperties()[0].SetValue(KratosMultiphysics.POISSON_RATIO, 0.3)
        mp.GetProperties()[0].SetValue(KratosMultiphysics.THICKNESS, 0.01)
        mp.GetProperties()[0].SetValue(KratosMultiphysics.DENSITY, 1.0)

        cl = StructuralMechanicsApplication.LinearElasticPlaneStress2DLaw()
        mp.GetProperties()[0].SetValue(KratosMultiphysics.CONSTITUTIVE_LAW, cl)

    def apply_bcs_sym_vertical(self, mp):
        """Apply symmetry boundary conditions (vertical edge)"""
        KratosMultiphysics.VariableUtils().ApplyFixity(KratosMultiphysics.DISPLACEMENT_X, True, mp.Nodes)
        KratosMultiphysics.VariableUtils().ApplyFixity(KratosMultiphysics.ROTATION_Y, True, mp.Nodes)
        KratosMultiphysics.VariableUtils().ApplyFixity(KratosMultiphysics.ROTATION_Z, True, mp.Nodes)

    def apply_bcs_sym_horizontal(self, mp):
        """Apply symmetry boundary conditions (horizontal edge)"""
        KratosMultiphysics.VariableUtils().ApplyFixity(KratosMultiphysics.DISPLACEMENT_Y, True, mp.Nodes)
        KratosMultiphysics.VariableUtils().ApplyFixity(KratosMultiphysics.ROTATION_X, True, mp.Nodes)
        KratosMultiphysics.VariableUtils().ApplyFixity(KratosMultiphysics.ROTATION_Z, True, mp.Nodes)

    def apply_bcs_simple_vertical(self, mp):
        """Apply simple support boundary conditions (vertical edge)"""
        KratosMultiphysics.VariableUtils().ApplyFixity(KratosMultiphysics.DISPLACEMENT_Z, True, mp.Nodes)
        KratosMultiphysics.VariableUtils().ApplyFixity(KratosMultiphysics.ROTATION_X, True, mp.Nodes)

    def apply_bcs_simple_horizontal(self, mp):
        """Apply simple support boundary conditions (horizontal edge)"""
        KratosMultiphysics.VariableUtils().ApplyFixity(KratosMultiphysics.DISPLACEMENT_Z, True, mp.Nodes)
        KratosMultiphysics.VariableUtils().ApplyFixity(KratosMultiphysics.ROTATION_Y, True, mp.Nodes)

    def update_conditions(self, mp, num_nodes):
        """Update load conditions based on current load multiplier"""
        conditions = mp.GetConditions()
        load_multiplier = mp.ProcessInfo[KratosMultiphysics.TIME]
        
        for i, condition in enumerate(conditions):
            tmp = condition.GetValue(StructuralMechanicsApplication.POINT_LOAD)
            load = 0.25
            # Corner nodes have different values
            if i < 2 or i == num_nodes or i == num_nodes + 1:
                load = 0.125
            
            if tmp[0] > 0.0:
                tmp[0] = load_multiplier * load
            else:
                tmp[0] = -1 * load_multiplier * load
            
            condition.SetValue(StructuralMechanicsApplication.POINT_LOAD, tmp)

    def set_conditions(self, mp, nodes, num_nodes, direction, counter):
        """Set point load conditions on plate edges"""
        # Corner Nodes
        cond1 = mp.CreateNewCondition("PointLoadCondition3D1N", counter, [nodes[0]], mp.GetProperties()[0])
        cond2 = mp.CreateNewCondition("PointLoadCondition3D1N", counter + 1, [nodes[1]], mp.GetProperties()[0])
        counter += 1
        
        load_on_cond1 = KratosMultiphysics.Vector(3)
        load_on_cond1[0] = direction * 0.125
        load_on_cond1[1] = 0.0
        load_on_cond1[2] = 0.0
        cond1.SetValue(StructuralMechanicsApplication.POINT_LOAD, load_on_cond1)
        cond2.SetValue(StructuralMechanicsApplication.POINT_LOAD, load_on_cond1)
        
        load_on_cond2 = KratosMultiphysics.Vector(3)
        load_on_cond2[0] = direction * 0.25
        load_on_cond2[1] = 0.0
        load_on_cond2[2] = 0.0
        
        # Center Nodes
        if direction > 0:
            max_ = num_nodes * (num_nodes - 1)
        else:
            max_ = num_nodes ** 2 - 1

        for i in range(nodes[0] + num_nodes, max_, num_nodes):
            counter += 1
            cond_tmp = mp.CreateNewCondition("PointLoadCondition3D1N", counter, [i], mp.GetProperties()[0])
            cond_tmp.SetValue(StructuralMechanicsApplication.POINT_LOAD, load_on_cond2)

    def apply_bcs_symmetry(self, mp, num_nodes):
        """Apply boundary conditions for symmetry model (quarter plate)"""
        # Left Edge - symmetry vertical
        bcs_dirichlet_left = mp.CreateSubModelPart("BoundaryConditionsDirichlet_left")
        bcs_dirichlet_left.AddNodes(range(1, num_nodes * num_nodes, num_nodes))
        self.apply_bcs_sym_vertical(bcs_dirichlet_left)
        
        # Right Edge - simple support
        bcs_dirichlet_right = mp.CreateSubModelPart("BoundaryConditionsDirichlet_right")
        bcs_dirichlet_right.AddNodes(range(num_nodes, num_nodes * num_nodes + 1, num_nodes))
        self.apply_bcs_simple_vertical(bcs_dirichlet_right)
        
        # Lower Edge - symmetry horizontal
        bcs_dirichlet_lower = mp.CreateSubModelPart("BoundaryConditionsDirichlet_lower")
        bcs_dirichlet_lower.AddNodes(range(1, num_nodes + 1, 1))
        self.apply_bcs_sym_horizontal(bcs_dirichlet_lower)
        
        # Upper Edge - simple support
        bcs_dirichlet_upper = mp.CreateSubModelPart("BoundaryConditionsDirichlet_upper")
        bcs_dirichlet_upper.AddNodes(range((num_nodes - 1) * num_nodes + 1, num_nodes * num_nodes + 1, 1))
        self.apply_bcs_simple_horizontal(bcs_dirichlet_upper)

    def apply_bcs_full(self, mp, num_nodes):
        """Apply boundary conditions for full model"""
        # Left Edge - simple support
        bcs_dirichlet_left = mp.CreateSubModelPart("BoundaryConditionsDirichlet_left")
        bcs_dirichlet_left.AddNodes(range(1, num_nodes * num_nodes, num_nodes))
        self.apply_bcs_simple_vertical(bcs_dirichlet_left)
        
        # Right Edge - simple support
        bcs_dirichlet_right = mp.CreateSubModelPart("BoundaryConditionsDirichlet_right")
        bcs_dirichlet_right.AddNodes(range(num_nodes, num_nodes * num_nodes + 1, num_nodes))
        self.apply_bcs_simple_vertical(bcs_dirichlet_right)
        
        # Lower Edge - simple support
        bcs_dirichlet_lower = mp.CreateSubModelPart("BoundaryConditionsDirichlet_lower")
        bcs_dirichlet_lower.AddNodes(range(1, num_nodes + 1, 1))
        self.apply_bcs_simple_horizontal(bcs_dirichlet_lower)
        
        # Upper Edge - simple support
        bcs_dirichlet_upper = mp.CreateSubModelPart("BoundaryConditionsDirichlet_upper")
        bcs_dirichlet_upper.AddNodes(range((num_nodes - 1) * num_nodes + 1, num_nodes ** 2 + 1, 1))
        self.apply_bcs_simple_horizontal(bcs_dirichlet_upper)
        
        # Additional constraints to make the plate statically determinate
        bcs_dirichlet_center_up = mp.CreateSubModelPart("BoundaryConditionsDirichlet_center_up")
        bcs_dirichlet_center_low = mp.CreateSubModelPart("BoundaryConditionsDirichlet_center_low")
        bcs_dirichlet_center = mp.CreateSubModelPart("BoundaryConditionsDirichlet_center")
        
        # Upper center node
        bcs_dirichlet_center_up.AddNodes([int(num_nodes ** 2 - (num_nodes - 1) / 2)])
        KratosMultiphysics.VariableUtils().ApplyFixity(KratosMultiphysics.DISPLACEMENT_X, True, bcs_dirichlet_center_up.Nodes)
        
        # Lower center node
        bcs_dirichlet_center_low.AddNodes([int((num_nodes + 1) / 2)])
        KratosMultiphysics.VariableUtils().ApplyFixity(KratosMultiphysics.DISPLACEMENT_X, True, bcs_dirichlet_center_low.Nodes)
        
        # Center node
        bcs_dirichlet_center.AddNodes([int((num_nodes ** 2) / 2 + 1)])
        KratosMultiphysics.VariableUtils().ApplyFixity(KratosMultiphysics.DISPLACEMENT_X, True, bcs_dirichlet_center.Nodes)
        KratosMultiphysics.VariableUtils().ApplyFixity(KratosMultiphysics.DISPLACEMENT_Y, True, bcs_dirichlet_center.Nodes)

    def solve_prebuckling_problem(self, mp, num_nodes, iterations, echo_level=0, write_vtk=False):
        """Solve the prebuckling problem"""
        eigensolver_settings = KratosMultiphysics.Parameters("""
        {
            "max_iteration"         : 1000,
            "tolerance"             : 1e-6,
            "number_of_eigenvalues" : 1,
            "echo_level"            : 0,
            "normalize_eigenvectors": false
        }
        """)

        buckling_settings = KratosMultiphysics.Parameters("""
        {
            "initial_load_increment"    : 1.0,
            "small_load_increment"      : 0.0005,
            "path_following_step"       : 0.5,
            "convergence_ratio"         : 0.005,
            "make_matrices_symmetric"   : true
        }
        """)

        eigen_solver = LinearSolversApplication.EigensystemSolver(eigensolver_settings)
        eigen_solver_ = KratosMultiphysics.ResidualBasedEliminationBuilderAndSolver(eigen_solver)
        convergence_criterion = KratosMultiphysics.DisplacementCriteria(1e-4, 1e-9)
        scheme = KratosMultiphysics.ResidualBasedIncrementalUpdateStaticScheme()
        linear_solver = KratosMultiphysics.SkylineLUFactorizationSolver()
        builder_and_solver = KratosMultiphysics.ResidualBasedEliminationBuilderAndSolver(linear_solver)
        convergence_criterion.SetEchoLevel(echo_level)

        eig_strategy = StructuralMechanicsApplication.PrebucklingStrategy(
            mp,
            scheme,
            eigen_solver_,
            builder_and_solver,
            convergence_criterion,
            10,
            buckling_settings
        )
        
        eig_strategy.SetEchoLevel(echo_level)
        
        # Prepare output directory for VTK
        if write_vtk:
            import os
            output_dir = os.path.join("vtk_output", mp.Name)
            os.makedirs(output_dir, exist_ok=True)
            print(f"  VTK files will be written to: {output_dir}/")
        
        load_factor = []
        for i in range(iterations):
            eig_strategy.Solve()
            if i % 2 == 1:
                load_factor.append(mp.ProcessInfo[StructuralMechanicsApplication.EIGENVALUE_VECTOR][0])
            
            # Write VTK output at each load step using manual writer
            if write_vtk:
                vtk_writer.write_vtk_step(mp, output_dir, i, mp.Name)
            
            self.update_conditions(mp, num_nodes)
        
        return load_factor

    def set_up_system(self, num_nodes, length):
        """Set up the complete system"""
        self.mp = self.current_model.CreateModelPart("Structure_Full")
        print(f"  Setting up FULL model ({num_nodes}x{num_nodes} nodes, {length}x{length} m)")

        self.add_variables(self.mp)
        self.apply_material_properties(self.mp)
        self.create_nodes(self.mp, num_nodes, length)
        self.add_dofs(self.mp)
        self.create_elements(self.mp, num_nodes)

        self.apply_bcs_full(self.mp, num_nodes)
        # Loads on right edge
        self.set_conditions(self.mp, [num_nodes, num_nodes ** 2], num_nodes, -1, 1)
        # Loads on left edge
        self.set_conditions(self.mp, [1, num_nodes * (num_nodes - 1) + 1], num_nodes, 1, num_nodes + 1)

        return self.mp

    def run(self, num_nodes, length, iterations, echo_level=0, write_vtk=True):
        """Run the complete prebuckling analysis"""
        self.set_up_system(num_nodes, length)
        print(f"  Solving prebuckling problem with {iterations} load steps...")
        load_factors = self.solve_prebuckling_problem(self.mp, num_nodes, iterations, echo_level, write_vtk)
        if write_vtk:
            print(f"  Total VTK files written: {iterations}")
        return load_factors


def main():
    """Main function"""
    print("=" * 70)
    print("PREBUCKLING ANALYSIS OF SIMPLY SUPPORTED SQUARE PLATE")
    print("Under Compressive Loading")
    print("=" * 70)
    print("\nProblem Description:")
    print("  - Square plate under in-plane compression")
    print("  - Simply supported on all edges")
    print("  - Material: E = 1e8 Pa, ν = 0.3")
    print("  - Thickness: 0.01 m")
    print("  - Full plate model (2m × 2m)")
    print("=" * 70)
    
    # Reference value from ABAQUS
    reference_value = 92.80
    
    # Run full model (whole plate, 2x2 m)
    print("\n" + "=" * 70)
    print("RUNNING FULL MODEL (Complete Plate)")
    print("=" * 70)
    num_nodes_full = 9
    load_steps_full = 10
    length_full = 2
    
    analysis_full = PrebucklingAnalysis()
    load_factors_full = analysis_full.run(num_nodes_full, length_full, load_steps_full, echo_level=1, write_vtk=True)
    
    # Print results
    print("\n" + "=" * 70)
    print("PREBUCKLING ANALYSIS RESULTS")
    print("=" * 70)
    
    print("\nCritical Buckling Load Multipliers:")
    print(f"  Full Model:")
    print(f"    First load step:  λ = {load_factors_full[0]:.4f}")
    print(f"    Last load step:   λ = {load_factors_full[-1]:.4f}")
    print(f"    Variation:        {abs(1 - load_factors_full[0] / load_factors_full[-1]) * 100:.4f}%")
    
    print(f"\n  Reference (ABAQUS S4R):")
    print(f"    Load multiplier:  λ = {reference_value:.4f}")
    
    print("\n" + "-" * 70)
    print("Comparison:")
    error_full_vs_ref = abs(load_factors_full[0] - reference_value) / reference_value * 100
    
    print(f"  Full vs Reference:     {error_full_vs_ref:.2f}% error")
    
    print("\n" + "=" * 70)
    
    # Check convergence
    variation = abs(1 - load_factors_full[0] / load_factors_full[-1])
    if variation < 1e-4:
        print("✓ Load multiplier converged (variation < 0.01%)")
    else:
        print("✗ Warning: Load multiplier not fully converged")
    
    if abs(load_factors_full[0] - reference_value) / reference_value < 0.01:
        print("✓ Results match reference within 1%")
    else:
        print("✗ Warning: Results differ from reference by >1%")
    
    print("=" * 70)
    
    print("\nVisualization:")
    print("  VTK files have been written to the 'vtk_output' directory")
    print("  Open them in ParaView to visualize:")
    print("    - Deformed shape (buckling mode)")
    print("    - Displacement field evolution")
    print("    - Reaction forces")
    print("=" * 70)


if __name__ == '__main__':
    main()
import KratosMultiphysics
import KratosMultiphysics.StructuralMechanicsApplication as StructuralMechanicsApplication
from KratosMultiphysics import kratos_utilities

if kratos_utilities.CheckIfApplicationsAvailable("LinearSolversApplication"):
    from KratosMultiphysics import LinearSolversApplication
else:
    raise ImportError("LinearSolversApplication is required but not available")


class EigenvalueAnalysis:
    """
    Eigenvalue analysis and modal decomposition with beam elements.
    Based on: C. Petersen, Dynamic der Baukonstruktionen, Viehweg Verlag, 2000, p. 252
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
        mp.AddNodalSolutionStepVariable(KratosMultiphysics.NODAL_MASS)
        mp.AddNodalSolutionStepVariable(KratosMultiphysics.VOLUME_ACCELERATION)

    def create_nodes(self, mp):
        """Create nodes for the beam structure"""
        mp.CreateNewNode(1, 0.0, 12.0, 0.0)
        mp.CreateNewNode(2, 0.0, 10.8, 0.0)
        mp.CreateNewNode(3, 0.0, 9.6, 0.0)
        mp.CreateNewNode(4, 0.0, 8.4, 0.0)
        mp.CreateNewNode(5, 0.0, 7.2, 0.0)
        mp.CreateNewNode(6, 0.0, 6.0, 0.0)
        mp.CreateNewNode(7, 0.0, 4.8, 0.0)
        mp.CreateNewNode(8, 0.0, 3.6, 0.0)
        mp.CreateNewNode(9, 0.0, 2.4, 0.0)
        mp.CreateNewNode(10, 0.0, 1.2, 0.0)
        mp.CreateNewNode(11, 0.0, 0.0, 0.0)

    def create_elements(self, mp):
        """Create beam elements and nodal masses"""
        element_name = "CrLinearBeamElement2D2N"
        
        # Create beam elements
        mp.CreateNewElement(element_name, 1, [11, 10], mp.GetProperties()[0])
        mp.CreateNewElement(element_name, 2, [10, 9], mp.GetProperties()[0])
        mp.CreateNewElement(element_name, 3, [9, 8], mp.GetProperties()[0])
        mp.CreateNewElement(element_name, 4, [8, 7], mp.GetProperties()[0])
        mp.CreateNewElement(element_name, 5, [7, 6], mp.GetProperties()[0])
        mp.CreateNewElement(element_name, 6, [6, 5], mp.GetProperties()[0])
        mp.CreateNewElement(element_name, 7, [5, 4], mp.GetProperties()[0])
        mp.CreateNewElement(element_name, 8, [4, 3], mp.GetProperties()[0])
        mp.CreateNewElement(element_name, 9, [3, 2], mp.GetProperties()[0])
        mp.CreateNewElement(element_name, 10, [2, 1], mp.GetProperties()[0])

        # Create nodal masses
        mass_1 = mp.CreateNewElement("NodalConcentratedElement2D1N", 11, [1], mp.GetProperties()[0])
        mass_2 = mp.CreateNewElement("NodalConcentratedElement2D1N", 12, [6], mp.GetProperties()[0])
        mass_1.SetValue(KratosMultiphysics.NODAL_MASS, 250)
        mass_2.SetValue(KratosMultiphysics.NODAL_MASS, 500)
        mass_1.Initialize(mp.ProcessInfo)
        mass_2.Initialize(mp.ProcessInfo)

    def apply_material_properties(self, mp):
        """Define material properties"""
        mp.GetProperties()[0].SetValue(KratosMultiphysics.YOUNG_MODULUS, 2e7)
        mp.GetProperties()[0].SetValue(KratosMultiphysics.DENSITY, 0.01)
        mp.GetProperties()[0].SetValue(StructuralMechanicsApplication.CROSS_AREA, 10)
        mp.GetProperties()[0].SetValue(StructuralMechanicsApplication.I33, 1.0)

        cl = StructuralMechanicsApplication.LinearElastic3DLaw()
        mp.GetProperties()[0].SetValue(KratosMultiphysics.CONSTITUTIVE_LAW, cl)

    def apply_boundary_conditions(self, mp):
        """Apply boundary conditions (fixities)"""
        KratosMultiphysics.VariableUtils().ApplyFixity(KratosMultiphysics.DISPLACEMENT_X, True, mp.Nodes)
        KratosMultiphysics.VariableUtils().ApplyFixity(KratosMultiphysics.DISPLACEMENT_Y, True, mp.Nodes)
        KratosMultiphysics.VariableUtils().ApplyFixity(KratosMultiphysics.ROTATION_Z, True, mp.Nodes)

    def solve_eigenvalue_problem(self, mp, use_block_builder=True, echo_level=1):
        """Solve the eigenvalue problem"""
        eigensolver_settings = KratosMultiphysics.Parameters("""
        {
            "max_iteration"         : 1000,
            "tolerance"             : 1e-6,
            "number_of_eigenvalues" : 2,
            "echo_level"            : 0,
            "normalize_eigenvectors": true
        }
        """)

        eigen_solver = LinearSolversApplication.EigensystemSolver(eigensolver_settings)
        
        if use_block_builder:
            builder_and_solver = KratosMultiphysics.ResidualBasedBlockBuilderAndSolver(eigen_solver)
        else:
            builder_and_solver = KratosMultiphysics.ResidualBasedEliminationBuilderAndSolver(eigen_solver)

        eigen_scheme = StructuralMechanicsApplication.EigensolverDynamicScheme()
        compute_modal_decomposition = True
        mass_matrix_diagonal_value = 0.0
        stiffness_matrix_diagonal_value = 1.0
        
        eig_strategy = StructuralMechanicsApplication.EigensolverStrategy(
            mp,
            eigen_scheme,
            builder_and_solver,
            mass_matrix_diagonal_value,
            stiffness_matrix_diagonal_value,
            compute_modal_decomposition
        )
        
        eig_strategy.SetEchoLevel(echo_level)
        eig_strategy.Solve()

    def set_up_system(self):
        """Set up the complete system"""
        self.mp = self.current_model.CreateModelPart("Structure")

        self.add_variables(self.mp)
        self.apply_material_properties(self.mp)
        self.create_nodes(self.mp)
        self.add_dofs(self.mp)
        self.create_elements(self.mp)

        # Create a submodelpart for Dirichlet boundary conditions
        bcs_dirichlet = self.mp.CreateSubModelPart("BoundaryConditionsDirichlet")
        bcs_dirichlet.AddNodes([11])
        self.apply_boundary_conditions(bcs_dirichlet)

        return self.mp

    def print_results(self):
        """Print eigenvalue analysis results"""
        eigenvalues = self.mp.ProcessInfo[StructuralMechanicsApplication.EIGENVALUE_VECTOR]
        modal_mass = self.mp.ProcessInfo[StructuralMechanicsApplication.MODAL_MASS_MATRIX]
        modal_stiffness = self.mp.ProcessInfo[StructuralMechanicsApplication.MODAL_STIFFNESS_MATRIX]

        print("\n" + "="*60)
        print("EIGENVALUE ANALYSIS RESULTS")
        print("="*60)
        
        print("\nEigenvalues:")
        for i, eigenvalue in enumerate(eigenvalues):
            frequency = (eigenvalue ** 0.5) / (2.0 * 3.14159265359)
            print(f"  Mode {i+1}: λ = {eigenvalue:.4f}, f = {frequency:.4f} Hz")
        
        print("\nModal Mass Matrix:")
        for i in range(len(eigenvalues)):
            row = "  "
            for j in range(len(eigenvalues)):
                row += f"{modal_mass[i,j]:8.4f} "
            print(row)
        
        print("\nModal Stiffness Matrix:")
        for i in range(len(eigenvalues)):
            row = "  "
            for j in range(len(eigenvalues)):
                row += f"{modal_stiffness[i,j]:8.4f} "
            print(row)
        
        print("\n" + "="*60)
        
        # Compare with reference values
        reference_eigenvalues = [115.1882, 3056.9526]
        print("\nComparison with Reference Values:")
        for i, (computed, reference) in enumerate(zip(eigenvalues, reference_eigenvalues)):
            error = abs(computed - reference) / reference * 100
            print(f"  Mode {i+1}: Computed = {computed:.4f}, Reference = {reference:.4f}, Error = {error:.2f}%")
        print("="*60 + "\n")

    def write_vtk_output(self, output_name="Structure"):
        """Write results to VTK format for visualization"""
        vtk_output_parameters = KratosMultiphysics.Parameters("""{
            "model_part_name"                    : "Structure",
            "file_format"                        : "binary",
            "output_precision"                   : 7,
            "output_control_type"                : "step",
            "output_interval"                    : 1.0,
            "output_sub_model_parts"             : false,
            "output_path"                        : "vtk_output",
            "save_output_files_in_folder"        : true,
            "nodal_solution_step_data_variables" : ["DISPLACEMENT","REACTION","ROTATION","REACTION_MOMENT"],
            "nodal_data_value_variables"         : [],
            "element_data_value_variables"       : [],
            "condition_data_value_variables"     : [],
            "gauss_point_variables_extrapolated_to_nodes" : []
        }""")
        
        # Update the model part name in parameters
        vtk_output_parameters["model_part_name"].SetString(self.mp.Name)
        
        # Create VTK output
        vtk_io = KratosMultiphysics.VtkOutput(self.mp, vtk_output_parameters)
        vtk_io.PrintOutput()
        
        print(f"\nVTK output written to: vtk_output/{self.mp.Name}/")
        print("Open in ParaView to visualize the mode shapes")

    def run(self, use_block_builder=True, echo_level=1, write_vtk=True):
        """Run the complete eigenvalue analysis"""
        print("\nSetting up the system...")
        self.set_up_system()
        
        print(f"Solving eigenvalue problem (using {'block' if use_block_builder else 'elimination'} builder)...")
        self.solve_eigenvalue_problem(self.mp, use_block_builder, echo_level)
        
        self.print_results()
        
        if write_vtk:
            self.write_vtk_output()


def main():
    """Main function"""
    print("="*60)
    print("Dynamic Eigenvalue Analysis")
    print("Based on: C. Petersen, Dynamic der Baukonstruktionen")
    print("          Viehweg Verlag, 2000, p. 252")
    print("="*60)
    
    # Create and run analysis with block builder
    analysis = EigenvalueAnalysis()
    analysis.run(use_block_builder=True, echo_level=1, write_vtk=True)
    
    # Optionally run with elimination builder
    print("\n\nRunning analysis with elimination builder...")
    analysis2 = EigenvalueAnalysis()
    analysis2.run(use_block_builder=False, echo_level=1, write_vtk=False)
    
    print("\n" + "="*60)
    print("Visualization:")
    print("  VTK files have been written to the 'vtk_output' directory")
    print("  Open them in ParaView to visualize:")
    print("    - Mode shapes (eigenvectors)")
    print("    - Deformed configurations")
    print("    - Natural vibration modes of the cantilever beam")
    print("="*60)


if __name__ == '__main__':
    main()
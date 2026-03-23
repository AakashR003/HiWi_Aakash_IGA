import os
import KratosMultiphysics
import KratosMultiphysics.StructuralMechanicsApplication as StructuralMechanicsApplication
from KratosMultiphysics import kratos_utilities

if kratos_utilities.CheckIfApplicationsAvailable("LinearSolversApplication"):
    from KratosMultiphysics import LinearSolversApplication
else:
    raise ImportError("LinearSolversApplication is required but not available")


# -----------------------------------------------------------------------
# BCs and loads  
#
#   bc_nodes  : { node_id: (ux, uy, uz, rx, ry, rz) }
#               'c' = constrained,  'f' = free
#
#   load_nodes: { node_id: (Fx, Fy, Fz) }
# -----------------------------------------------------------------------
bc_nodes = {
    1: ('c', 'c', 'c', 'c', 'c', 'c'),   
    2: ('c', 'c', 'c', 'c', 'c', 'c'),   
}

load_nodes = {
    21: (0.0, -5.0, 0.0),  
    22: (0.0, -5.0, 0.0),   
}


def make_vtk_output(model_part):
    """Create a VtkOutput instance for a given model part."""
    name = model_part.Name
    path = f"vtk_output/{name}"
    os.makedirs(path, exist_ok=True)
    params = KratosMultiphysics.Parameters()
    params.AddString("model_part_name",  name)
    params.AddString("output_path",      path)
    params.AddString("file_format",      "ascii")
    params.AddInt("output_precision",    7)
    params.AddString("output_control_type", "step")
    params.AddDouble("output_interval",  1.0)
    params.AddBool("save_output_files_in_folder", True)
    params.AddBool("output_sub_model_parts",      False)
    params.AddBool("write_deformed_configuration", True)
    params.AddValue("nodal_solution_step_data_variables",
        KratosMultiphysics.Parameters('["DISPLACEMENT","REACTION","ROTATION","REACTION_MOMENT"]'))
    params.AddValue("condition_data_value_variables",
        KratosMultiphysics.Parameters('["POINT_LOAD"]'))
    return KratosMultiphysics.VtkOutput(model_part, params)


def run_prebuckling():
    model = KratosMultiphysics.Model()
    mp = model.CreateModelPart("Structure")

    # Variables
    mp.AddNodalSolutionStepVariable(KratosMultiphysics.DISPLACEMENT)
    mp.AddNodalSolutionStepVariable(KratosMultiphysics.REACTION)
    mp.AddNodalSolutionStepVariable(KratosMultiphysics.REACTION_MOMENT)
    mp.AddNodalSolutionStepVariable(KratosMultiphysics.ROTATION)

    # Material
    mp.GetProperties()[0].SetValue(KratosMultiphysics.YOUNG_MODULUS,  1e6)
    mp.GetProperties()[0].SetValue(KratosMultiphysics.POISSON_RATIO,   0.0)
    mp.GetProperties()[0].SetValue(KratosMultiphysics.THICKNESS,        1)
    mp.GetProperties()[0].SetValue(KratosMultiphysics.DENSITY,          1.0)
    mp.GetProperties()[0].SetValue(
        KratosMultiphysics.CONSTITUTIVE_LAW,
        StructuralMechanicsApplication.LinearElasticPlaneStress2DLaw()
    )

    # Geometry
    num_nodes_x = 2
    num_nodes_y = 11
    length_x    = 2.0
    length_y    = 100.0

    # Nodes (outer y, inner x)
    counter = 0
    for y in range(num_nodes_y):
        for x in range(num_nodes_x):
            counter += 1
            mp.CreateNewNode(
                counter,
                x / (num_nodes_x - 1) * length_x,
                y / (num_nodes_y - 1) * length_y,
                0.0
            )

    # DOFs
    dof_vars = [
        KratosMultiphysics.DISPLACEMENT_X,
        KratosMultiphysics.DISPLACEMENT_Y,
        KratosMultiphysics.DISPLACEMENT_Z,
        KratosMultiphysics.ROTATION_X,
        KratosMultiphysics.ROTATION_Y,
        KratosMultiphysics.ROTATION_Z,
    ]
    dof_reactions = [
        KratosMultiphysics.REACTION_X,
        KratosMultiphysics.REACTION_Y,
        KratosMultiphysics.REACTION_Z,
        KratosMultiphysics.REACTION_MOMENT_X,
        KratosMultiphysics.REACTION_MOMENT_Y,
        KratosMultiphysics.REACTION_MOMENT_Z,
    ]
    for var, reaction in zip(dof_vars, dof_reactions):
        KratosMultiphysics.VariableUtils().AddDof(var, reaction, mp)

    # Elements
    for y in range(num_nodes_y - 1):
        for x in range(num_nodes_x - 1):
            mp.CreateNewElement(
                "ShellThickElementCorotational3D4N",
                num_nodes_x * y + x + 1,
                [
                    num_nodes_x * y       + x + 1,
                    num_nodes_x * y       + x + 2,
                    num_nodes_x * (y + 1) + x + 2,
                    num_nodes_x * (y + 1) + x + 1,
                ],
                mp.GetProperties()[0]
            )

    # -------------------------------------------------------------------
    # BCs — apply from hardcoded bc_nodes dict
    # -------------------------------------------------------------------
    bc_smp = mp.CreateSubModelPart("BC_Nodes")
    bc_smp.AddNodes(list(bc_nodes.keys()))
    for node_id, (ux, uy, uz, rx, ry, rz) in bc_nodes.items():
        node = mp.GetNode(node_id)
        for var, state in zip(dof_vars, [ux, uy, uz, rx, ry, rz]):
            if state == 'c':
                node.Fix(var)

    # -------------------------------------------------------------------
    # Loads — apply from hardcoded load_nodes dict
    # -------------------------------------------------------------------
    load_smp = mp.CreateSubModelPart("PointLoad_Nodes")
    load_smp.AddNodes(list(load_nodes.keys()))
    for cond_id, (node_id, (fx, fy, fz)) in enumerate(load_nodes.items(), start=1):
        load_vec = KratosMultiphysics.Vector(3)
        load_vec[0], load_vec[1], load_vec[2] = fx, fy, fz
        cond = mp.CreateNewCondition(
            "PointLoadCondition3D1N", cond_id, [node_id], mp.GetProperties()[0]
        )
        cond.SetValue(StructuralMechanicsApplication.POINT_LOAD, load_vec)

    # Solver setup
    eigen_solver = KratosMultiphysics.ResidualBasedEliminationBuilderAndSolver(
        LinearSolversApplication.EigensystemSolver(KratosMultiphysics.Parameters("""{
            "max_iteration": 1000, "tolerance": 1e-6,
            "number_of_eigenvalues": 1, "echo_level": 0,
            "normalize_eigenvectors": false
        }"""))
    )
    builder_and_solver = KratosMultiphysics.ResidualBasedEliminationBuilderAndSolver(
        KratosMultiphysics.SkylineLUFactorizationSolver()
    )
    convergence_criterion = KratosMultiphysics.DisplacementCriteria(1e-4, 1e-9)
    convergence_criterion.SetEchoLevel(0)

    eig_strategy = StructuralMechanicsApplication.PrebucklingStrategy(
        mp,
        KratosMultiphysics.ResidualBasedIncrementalUpdateStaticScheme(),
        eigen_solver,
        builder_and_solver,
        convergence_criterion,
        10,
        KratosMultiphysics.Parameters("""{
            "initial_load_increment"  : 1.0,
            "small_load_increment"    : 0.0005,
            "path_following_step"     : 0.5,
            "convergence_ratio"       : 0.005,
            "make_matrices_symmetric" : true
        }""")
    )
    eig_strategy.SetEchoLevel(0)


    all_parts = [mp] + [mp.GetSubModelPart(name) for name in mp.GetSubModelPartNames()]
    vtk_outputs = [make_vtk_output(part) for part in all_parts]
    print("VTK outputs initialised for:")
    for part in all_parts:
        print(f"  vtk_output/{part.Name}/")

    # Solve
    load_factors = []
    for i in range(10):
        eig_strategy.Solve()
        if i % 2 == 1:
            load_factors.append(
                mp.ProcessInfo[StructuralMechanicsApplication.EIGENVALUE_VECTOR][0]
            )

        # Write VTK for every model part
        for vtk in vtk_outputs:
            vtk.PrintOutput()

        lm = mp.ProcessInfo[KratosMultiphysics.TIME]
        for cond in mp.GetConditions():
            node_id = cond.GetNodes()[0].Id
            if node_id in load_nodes:
                fx_orig, fy_orig, fz_orig = load_nodes[node_id]
                tmp = cond.GetValue(StructuralMechanicsApplication.POINT_LOAD)
                tmp[0] = fx_orig * lm
                tmp[1] = fy_orig * lm
                tmp[2] = fz_orig * lm
                cond.SetValue(StructuralMechanicsApplication.POINT_LOAD, tmp)

    return load_factors


if __name__ == '__main__':
    load_factors = run_prebuckling()
    print(f"\nCritical Buckling Load: λ = {load_factors[-1]:.6f}")
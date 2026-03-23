# Isogeometric Analysis (IGA) with Kratos Framework

## Overview
This HiWi (Student Research Assistant) project explores **Isogeometric Analysis** using the **Kratos Multiphysics** framework. It contains multiple case studies demonstrating structural mechanics analysis using IGA elements, including plates, shells, and complex geometries.

## Project Structure

The project is organized into the following case studies:

### 1. **Scodrillo Roof - Single Patch** (`1.Scodrillo Roof_Single_Patch/`)
- Analysis of a roof structure modeled as a single IGA patch
- Demonstrates single-patch IGA formulation for complex geometries

### 2. **Plate with Hole** (`2.Plate with hole/`)
- Linear structural analysis of a plate with a circular hole
- Tests mesh refinement and convergence studies
- Configuration: `Document_Files/2/`
  - **Materials**: Steel plate with elastic properties
  - **Analysis Type**: Linear static analysis
  - **Key Files**: `geometry.cad.json`, `ProjectParameters.json`, `materials.json`

### 3. **NonLinear Cantilever - Multipatch** (`3.NonLinear Cantiliver - Multipatch/`)
- Nonlinear analysis of a cantilever beam modeled with multiple patches
- Multiple refinement levels (2.1, 2.2, 2.3, 2.4, 2.5)
- Tests patch coupling and multipatch IGA formulation
- Subdirectories for different configurations:
  - **Match**: Continuous coupling between patches
  - **NonMatch**: Non-matching interfaces between patches

### 4. **Penalty Study** (`4.Penalty Study/`)
- Investigation of penalty parameters for multipatch coupling
- Multiple penalty values tested in configurations 2.1, 2.2, 2.3
- Used to optimize coupling between non-matching patches

### 5. **Reissner-Mindlin Shell Element** (`5.Reissner-Mindlin Shell Element/`)
- Nonlinear shell analysis using Reissner-Mindlin theory
- Configuration: `NonlinearCant/`
- Demonstrates shell element formulation in IGA
- Analysis of cantilever plates under large deformations

### 6. **Buckling Analysis** (`6.Buckling Analysis/`)
- Eigenvalue analysis for structural stability
- Multiple configurations (2.2, 2.3, 2.4, 2.5)
- Buckling capacity and critical loads determination

## Project Files

### Common File Types

| File Type | Description |
|-----------|-------------|
| `.3dm` | Rhino 3D geometry files (CAD models) |
| `geometry.cad.json` | IGA geometry in JSON format (control points, weights, knots) |
| `ProjectParameters.json` | Kratos solver configuration and analysis parameters |
| `physics.iga.json` | IGA-specific settings (basis functions, integration rules) |
| `materials.json` | Material properties (Young's modulus, Poisson ratio, density) |
| `refinements.iga.json` | Mesh refinement parameters for p- and h-refinement |
| `kratos_main_iga.py` | Main Python script to run the analysis |
| `.post.res` | Kratos output results file |
| `*_integrationdomain.json` | Integration domain specifications |
| `.georhino.json` | Geometric and Rhino-related metadata |

### Running a Simulation

Each case study has a `run_kratos.bat` batch file that executes:

```bash
kratos_main_iga.py
```

**Prerequisites:**
- Kratos Multiphysics installed with IGA Application module
- Python 3.x
- Required modules: `KratosMultiphysics.IgaApplication`, `KratosMultiphysics.StructuralMechanicsApplication`

**To run a simulation:**

1. Navigate to the case study directory:
   ```bash
   cd "2.Plate with hole/Document_Files/2"
   ```

2. Execute the main script:
   ```bash
   python kratos_main_iga.py
   ```

3. Results are generated in the same directory as `.post.res` files

## Key Technologies

- **Kratos Multiphysics**: Finite element framework
- **Isogeometric Analysis (IGA)**: Uses NURBS basis functions for geometry and analysis
- **Structural Mechanics**: Linear and nonlinear static analysis
- **Shell Elements**: Reissner-Mindlin formulation for thin shells
- **Multipatch IGA**: Handles complex geometries with multiple surface patches

## Analysis Types

### Linear Analysis
- Static linear elastic problems
- Suitable for small deformations
- Example: Basic plate with hole analysis

### Nonlinear Analysis
- Geometric nonlinearity (large deformations)
- Material nonlinearity (plasticity, in some cases)
- Used in cantilever and shell analysis studies

### Eigenvalue Analysis (Buckling)
- Determines critical loads and buckling modes
- Linear eigenvalue problem using stiffness and geometric stiffness matrices

## Key Parameters

### Solver Settings
- **Analysis Type**: Linear or nonlinear
- **Time Stepping**: Static or transient
- **Solver Type**: Direct (sparse LU) or iterative solvers
- **Convergence Criteria**: Displacement or residual-based

### IGA-Specific
- **Refinement**: p-refinement (degree elevation), h-refinement (knot insertion)
- **Integration Method**: Gaussian quadrature
- **Basis Functions**: NURBS (Non-Uniform Rational B-Splines)
- **Multipatch Coupling**: Continuous (matching), penalty-based, or Lagrange multipliers

## Output & Visualization

Results are saved in Kratos native format (`.post.res`). These can be visualized in:
- **Rhino with Grasshopper** plugins
- **ParaView** (with appropriate Kratos converters)
- **Custom post-processing scripts**

Key output quantities:
- Displacements
- Stresses (Von Mises, principal)
- Strains
- Reactions at supports
- Buckling modes and factors

## Directory Naming Convention

- **Document_Files/**: Contains analysis input files and results
- **Images/**: Stores visualization outputs and figures
- **Old/**: Archive of previous versions or preliminary studies
- **NonlinearCant/**, **NonlinearCant2Patch/**: Different simulation configurations
- **Match/**: Continuous patch coupling configurations
- **NonMatch_CurveTrimmed/**, **NonMatch_trimmed/**: Non-matching interfaces with trimming

## Notes for Researchers

- IGA provides smoother geometry representation with fewer DOFs compared to standard FEM
- Multipatch IGA requires careful handling of patch interfaces
- h and p-refinement can significantly affect convergence behavior
- Penalty methods are commonly used; study convergence with penalty parameter
- Results should be compared with analytical solutions or reference FEM studies

## Version Control

This project uses Git for version control. Check commit history for evolution of models and parameters.

---

**Project Lead**: Ricky  
**Student Researcher**: Aakash  
**Research Area**: Isogeometric Analysis, Structural Mechanics, Multipatch Analysis

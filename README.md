# Isogeometric Analysis (IGA) with Kratos Framework

## Overview
This folder is a part of HiWi (Student Research Assistant) my work in **Isogeometric Analysis** using the **Kratos Multiphysics** framework. It contains multiple case studies and validations for for IGA elements.

## Structure

The repository contains 6 case studies and eahc case study has followinf documents:

1. Report for corresponding work
2. Reference or Benchmark (if needed)
3. Simulation files

Breif explanation to the case study: 

### 1. **Scodrillo Roof - Single Patch** (`1.Scodrillo Roof_Single_Patch/`)
- Validation of Shell3pelement (Kirchoff Shell element) in Kratos with single patch Scodrillo roof. 
- Benchmark: Josef M. Kiendl Dissertation (Can found in the folder)

### 2. **Plate with Hole** (`2.Plate with hole/`)
- Validation of Shell3pelement in Kratos with single patch Plate with Hole. 
- Benchmark: Michael Breitenberger Dissertation (Can found in the folder)

### 3. **NonLinear Cantilever - Multipatch** (`3.NonLinear Cantiliver - Multipatch/`)
- Validation of Geometric Nonlinearity of Shell3pelement with cantilever beam modeled for single and multiple patches
- Both conforming and non-conforming patches are studied
- Benchmark: Michael Breitenberger Dissertation (Can found in the folder)

### 4. **Penalty Study** (`4.Penalty Study/`)
- Investigation of penalty parameters for conforming and non-conforming multipatch on Scodrillo Roof
- Reference: "Penalty coupling of non-matching isogeometric Kirchhoff–Love shell patches with application to composite wind turbine blades"

### 5. **Reissner-Mindlin Shell Element** (`5.Reissner-Mindlin Shell Element/`)
- Validation of Geometric Nonlinearity of Shell6pelement with cantilever beam modeled for single patch

### 6. **Buckling Analysis** (`6.Buckling Analysis/`)
- Validation of Buckling analysis for Shell3pelement (Kirchoff Shell element)and Shell6pelement (Reissner-Mindlin) with cantilever beam modeled for single patch

## Simulation Files

The simulation files will contain files needed for simulating the case studies in the report. 
All the case studies in the report will be available in the simulation files. 
For better location of simulation files, refer to the serial number of a particular simulation in the report. 
This serial number is the folder name. 

- All the simulations are carried out with KratosMultiphysics - 10.4.0 main branch. 
- Also complied version of Kratos (Pull request: pr13933) is used for shell6pelement. 
- Required modules: `KratosMultiphysics.IgaApplication`, `KratosMultiphysics.StructuralMechanicsApplication`

<!-- ### Common File Types

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
| `.georhino.json` | Geometric and Rhino-related metadata | -->



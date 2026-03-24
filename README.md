# Isogeometric Analysis (IGA) with KratosMultiphysics

## Overview
This folder is a part of HiWi (Student Research Assistant) work in **Isogeometric Analysis** using the **Kratos Multiphysics** framework. It contains multiple case studies and validations for IGA elements.

## Structure

The repository contains 6 case studies and each case study has the following documents:

1. Report for corresponding work
2. Reference or Benchmark (if needed)
3. Simulation files

Brief explanation to the case study:

### 1. [Scordelis-Lo Roof - Single Patch](./1.Scodrillo%20Roof_Single_Patch/)
- Validation of Shell3p element (Kirchhoff Shell element) in Kratos with single patch Scordelis-Lo Roof.
- Benchmark: Josef M. Kiendl Dissertation (Can be found in the folder)

### 2. [Plate with Hole](./2.Plate%20with%20hole/)
- Validation of Shell3p element in Kratos with single patch Plate with Hole.
- Benchmark: Michael Breitenberger Dissertation (Can be found in the folder)

### 3. [NonLinear Cantilever - Multipatch](./3.NonLinear%20Cantiliver%20-%20Multipatch/)
- Validation of Geometric Nonlinearity of Shell3p element with cantilever beam modeled for single and multiple patches
- Both conforming and non-conforming patches are studied
- Benchmark: Michael Breitenberger Dissertation (Can be found in the folder)

### 4. [Penalty Study](./4.Penalty%20Study/)
- Investigation of penalty parameters for conforming and non-conforming multipatch on Scordelis-Lo Roof
- Reference: "Penalty coupling of non-matching isogeometric Kirchhoff–Love shell patches with application to composite wind turbine blades"

### 5. [Reissner-Mindlin Shell Element](./5.Reissner-Mindlin%20Shell%20Element/)
- Validation of Geometric Nonlinearity of Shell6p element with cantilever beam modeled for single patch

### 6. [Buckling Analysis](./6.Buckling%20Analysis/)
- Validation of Buckling analysis for Shell3p element (Kirchhoff Shell element) and Shell6p element (Reissner-Mindlin) with cantilever beam modeled for single patch

## Simulation Files

The simulation files will contain files needed for simulating the case studies in the report.
All the case studies in the report will be available in the simulation files.
For better location of simulation files, refer to the serial number of a particular simulation in the report.
This serial number is the folder name.

- All the simulations are carried out with KratosMultiphysics - 10.4.0 main branch.
- Also compiled version of Kratos (Pull request: pr13933) is used for Shell6p element.
- Required modules: `KratosMultiphysics.IgaApplication`, `KratosMultiphysics.StructuralMechanicsApplication`

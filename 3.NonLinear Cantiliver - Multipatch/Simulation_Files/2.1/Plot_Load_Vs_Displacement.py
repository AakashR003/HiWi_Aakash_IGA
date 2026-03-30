import re
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# ─────────────────────────────────────────────
NODE_ID   = 105
FILE_PATH = "NonlinearCant_kratos_shell_1.post.res"
# ─────────────────────────────────────────────

min_load  = float(input("Enter min load value: ").strip())
max_load  = float(input("Enter max load value: ").strip())
step_size = float(input("Enter step size: ").strip())

load_steps = []
dx_list = []  # Added for X-displacement
dz_list = []

in_displacement_block = False
current_step = None

with open(FILE_PATH, "r") as f:
    for line in f:
        line = line.strip()

        match = re.match(r'Result\s+"DISPLACEMENT"\s+"Load Case"\s+(\d+)\s+Vector\s+OnNodes', line)
        if match:
            in_displacement_block = True
            current_step = int(match.group(1))
            continue

        if line == "End Values":
            in_displacement_block = False
            current_step = None
            continue

        if in_displacement_block and current_step is not None:
            parts = line.split()
            # Kratos format: NodeID DX DY DZ
            if len(parts) == 4 and parts[0] == str(NODE_ID):
                load_steps.append(current_step)
                dx_list.append(abs(float(parts[1])))  # Index 1 is X-displacement
                dz_list.append(abs(float(parts[3])))  # Index 3 is Z-displacement

# Build y-axis values using min, max and step size
y_values = [min_load + i * step_size for i in range(len(load_steps))]

expected_steps = round((max_load - min_load) / step_size) + 1
if len(load_steps) != expected_steps:
    print(f"⚠️  Warning: {len(load_steps)} data points found in file, "
          f"but min/max/step implies {expected_steps} steps.")

# ─────────────────────────────────────────────
# MODIFICATIONS START HERE
# ─────────────────────────────────────────────

# 1. Aspect Ratio and Size: Kept compact for Markdown
plt.figure(figsize=(5.5, 4.5)) 

# 2. Styling: Original colors and circular data points
# Curve for Z-displacement (Green)
plt.plot(dz_list, y_values,
         marker="o",        
         markersize=4,      
         color="#2ca02c",   
         linewidth=1.5,     
         label="W$_{tip}$ (Z)", 
         linestyle='-')     

# Curve for X-displacement (Blue)
plt.plot(dx_list, y_values,
         marker="o",        
         markersize=4,      
         color="#1f77b4",   
         linewidth=1.5,     
         label="U$_{tip}$ (X)", 
         linestyle='-')    

plt.xlabel("Tip deflections", fontsize=9) 
plt.ylabel("End force", fontsize=9)
plt.xticks(fontsize=8)
plt.yticks(fontsize=8)
plt.grid(True, linestyle="--", alpha=0.3) 

plt.legend(fontsize=8)

# 3. Text Annotations: RESTORED to show on ALL points
for x, z, y in zip(dx_list, dz_list, y_values):
    # Annotate Z-displacement (Green)
    plt.annotate(
        f"({z:.3f}, {y:.2f})",
        xy=(z, y),
        xytext=(4, -2), # Slight offset so text doesn't sit exactly on the dot
        textcoords="offset points",
        fontsize=6,     # Kept small to prevent clutter
        color="#2ca02c", 
    )
    # Annotate X-displacement (Blue)
    plt.annotate(
        f"({x:.3f}, {y:.2f})",
        xy=(x, y),
        xytext=(4, -2), # Slight offset so text doesn't sit exactly on the dot
        textcoords="offset points",
        fontsize=6,     # Kept small to prevent clutter
        color="#1f77b4",
    )

# ─────────────────────────────────────────────
# 4. Save and Show
# ─────────────────────────────────────────────
plt.tight_layout()
plt.savefig(f"LoadStep_vs_Displacement_XZ_Node{NODE_ID}_matching.png", dpi=120, bbox_inches='tight', pad_inches=0.1) 
plt.show()
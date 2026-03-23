import re
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# ─────────────────────────────────────────────
NODE_ID   = 216
FILE_PATH = "NonlinearCant2PatchNonMatch_trimmed_kratos_shell_1.post.res"
# ─────────────────────────────────────────────

min_load  = float(input("Enter min load value: ").strip())
max_load  = float(input("Enter max load value: ").strip())
step_size = float(input("Enter step size: ").strip())

load_steps = []
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
            if len(parts) == 4 and parts[0] == str(NODE_ID):
                load_steps.append(current_step)
                dz_list.append(abs(float(parts[3])))

# Build y-axis values using min, max and step size
y_values = [min_load + i * step_size for i in range(len(load_steps))]

# Warn if generated steps don't align with max_load
expected_steps = round((max_load - min_load) / step_size) + 1
if len(load_steps) != expected_steps:
    print(f"⚠️  Warning: {len(load_steps)} data points found in file, "
          f"but min/max/step implies {expected_steps} steps.")

plt.figure(figsize=(8, 5))
plt.plot(dz_list, y_values, marker="o", color="#2ca02c", linewidth=1.8, markersize=5)
plt.xlabel("Displacement Z")
plt.ylabel("Load")
plt.title(f"Z-Displacement vs Load — Point {NODE_ID}")
plt.grid(True, linestyle="--", alpha=0.5)
for x, y in zip(dz_list, y_values):
    plt.annotate(
        f"({x:.2f}, {y:.2f})",
        xy=(x, y),
        # xytext=(10, 20),
        # textcoords="offset points",
        fontsize=7,
        color="#333333",
    )
plt.tight_layout()
plt.savefig(f"LoadStep_vs_Displacement_Z_Node{NODE_ID}.png", dpi=150)
plt.show()
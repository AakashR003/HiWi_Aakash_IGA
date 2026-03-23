import re
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# ─────────────────────────────────────────────
NODE_ID   = 400
FILE_PATH = "NonlinearCant2Patch_kratos_shell_1.post.res"
# ─────────────────────────────────────────────

max_load_input = input("Enter max load value (or press Enter to use Load Step): ").strip()
try:
    max_load = float(max_load_input)
except ValueError:
    max_load = None

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

# Build y-axis values
if max_load is not None:
    total_steps = max(load_steps)
    y_values = [max_load * (s / total_steps) for s in load_steps]
    y_label  = "Load"
else:
    y_values = load_steps
    y_label  = "Load Step"

plt.figure(figsize=(8, 5))
plt.plot(dz_list, y_values, marker="o", color="#2ca02c", linewidth=1.8, markersize=5)
plt.xlabel("Displacement Z")
plt.ylabel(y_label)
plt.title(f"Z-Displacement vs {y_label} — Point {NODE_ID}")
if max_load is None:
    plt.gca().yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.savefig(f"LoadStep_vs_Displacement_Z_Node{NODE_ID}.png", dpi=150)
plt.show()
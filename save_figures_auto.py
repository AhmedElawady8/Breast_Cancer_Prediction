import os
import matplotlib.pyplot as plt

plots_dir = "figures"
os.makedirs(plots_dir, exist_ok=True)

_plot_counter = 1

def save_current_plot():
    global _plot_counter
    filename = f"plot_{_plot_counter}.png"
    filepath = os.path.join(plots_dir, filename)
    plt.savefig(filepath, bbox_inches='tight')
    print(f"Saved plot as: {filepath}")
    _plot_counter += 1

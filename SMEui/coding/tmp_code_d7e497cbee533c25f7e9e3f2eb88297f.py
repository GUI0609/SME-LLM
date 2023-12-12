import numpy as np
import matplotlib.pyplot as plt

# Generate random data for demonstration
# Replace this data with your actual data
distances = np.random.randint(0, 10, size=100)
conductances = np.random.uniform(0, 1, size=100)

# Set up the histogram
bins = 10
heatmap, xedges, yedges = np.histogram2d(distances, conductances, bins=bins)

# Plot the histogram
plt.imshow(heatmap.T, cmap='hot', origin='lower', extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]])
plt.colorbar(label='Count')
plt.xlabel('Distance')
plt.ylabel('Condutance')
plt.title('Condutance-Distance Histogram')

# Show the plot
plt.show()
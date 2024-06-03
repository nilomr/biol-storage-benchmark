import os
import time
from tracemalloc import start

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

# Define the directories to test
directories = [
    "/data/BS/userdata/nilo/projects/storage-tests",
    "/data/BS/test_for_nilo_nfs",
    "/data/BS/test_for_nilo_smb",
]

# Define the size of the chunks to write in bytes (100MB)
chunk_size = 100 * 1024 * 1024

# Define the number of times to write and read the chunks
num_iterations = 10

# Define the results dictionary
results = {}

# Define the data to write
data = os.urandom(1024)

# Loop through each directory
for directory in tqdm(directories, desc="Testing directories"):
    # Define the file path
    file_path = os.path.join(directory, "tempfile")

    # Define the lists to store the speeds
    write_speeds = []
    read_speeds = []

    # Repeat the write and read operations multiple times
    for _ in range(num_iterations):
        # Measure the time taken to write the chunk
        start_time = time.time()
        with open(file_path, "wb") as f:
            for _ in range(chunk_size // 1024):
                f.write(data)
        write_time = time.time() - start_time

        # Measure the time taken to read the chunk
        start_time = time.time()
        with open(file_path, "rb") as f:
            while f.read(1024):
                pass
        read_time = time.time() - start_time
        write_speeds.append((chunk_size / write_time) / 1024 / 1024)
        read_speeds.append((chunk_size / read_time) / 1024 / 1024)

    results[directory] = {
        "write_speeds": write_speeds,
        "read_speeds": read_speeds,
    }

    os.remove(file_path)

# Plot the results as box plots
plt.figure(figsize=(6, 6))
plt.boxplot(
    [results[directory]["write_speeds"] for directory in directories],
    labels=directories,
)
plt.ylabel("Speed (MB/s)")
plt.title("Write Speeds for Different Filesystems")
mean_values = [np.mean(results[directory]["write_speeds"]) for directory in directories]
for i, mean in enumerate(mean_values):
    plt.text(i + 1.3, mean, f"   {mean:.2f}\nMB/s", ha="center", va="center")
plt.xticks([1, 2, 3], ["local", "nfs", "smb"])
plt.savefig("output/write_speeds.png")

# Now for read speeds
plt.figure(figsize=(6, 6))
plt.boxplot(
    [results[directory]["read_speeds"] for directory in directories],
    labels=directories,
)
plt.ylabel("Speed (MB/s)")
plt.title("Read Speeds for Different Filesystems")
mean_values = [np.mean(results[directory]["read_speeds"]) for directory in directories]
for i, mean in enumerate(mean_values):
    plt.text(i + 1.3, mean, f"   {mean:.2f}\nMB/s", ha="center", va="center")
plt.xticks([1, 2, 3], ["local", "nfs", "smb"])
plt.savefig("output/os_read_speeds.png")
plt.savefig("output/os_read_speeds.png")

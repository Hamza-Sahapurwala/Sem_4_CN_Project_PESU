import csv
import matplotlib.pyplot as plt

file_sizes = []
times = []

# read csv data
with open("performance.csv", "r") as f:
    reader = csv.reader(f)

    for row in reader:
        size = float(row[0])
        time = float(row[1])

        file_sizes.append(size)
        times.append(time)

# convert bytes → KB (for nicer graph)
file_sizes_kb = [s/1024 for s in file_sizes]

plt.figure()

plt.plot(file_sizes_kb, times, marker='o')

plt.title("Performance vs File Size Analysis")
plt.xlabel("File Size (KB)")
plt.ylabel("Transfer Time (seconds)")

plt.grid(True)

plt.show()
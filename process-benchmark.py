import json
import os

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt


def load_json_file(file_path):
    with open(file_path, "r") as f:
        return json.load(f)


def convert_bytes_to_MB(b):
    return b / 1024 / 1024


def plot_bandwidth(df):
    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=df,
        x="volume",
        y="bw",
        hue="jobtype",
        ci=None,
        palette=["#5083a7", "#ecad00"],
    )
    plt.ylabel("Bandwidth (MB/s)")
    plt.title("Bandwidth (MB/s) for randread and randwrite operations")
    # plt.ylim(520, 600)  # Truncate y-axis from 0 to 250 MB/s
    plt.savefig("output/bandwidth.png")


def process_files(directory):
    stats = []
    for filename in os.listdir(directory):
        if filename.endswith(".json") and "summary" not in filename:
            data = load_json_file(os.path.join(directory, filename))
            volume = filename.split("_")[:-2][-1]
            for job in data["jobs"]:
                job_stats = {
                    "volume": volume,
                    "jobname": job["jobname"],
                    "read_io_bytes": job["read"]["io_bytes"],
                    "read_bw_bytes": job["read"]["bw_bytes"],
                    "read_iops": job["read"]["iops"],
                    "read_runtime": job["read"]["runtime"],
                    "write_io_bytes": job["write"]["io_bytes"],
                    "write_bw_bytes": job["write"]["bw_bytes"],
                    "write_iops": job["write"]["iops"],
                    "write_runtime": job["write"]["runtime"],
                }
                stats.append(job_stats)
    return stats


def main():
    directory = "output/"
    stats = process_files(directory)

    for stat in stats:
        stat["read_bw_MB/s"] = convert_bytes_to_MB(stat["read_bw_bytes"])
        stat["write_bw_MB/s"] = convert_bytes_to_MB(stat["write_bw_bytes"])

    df = pd.DataFrame(stats)
    df["jobtype"] = df["jobname"].apply(lambda x: "read" if "read" in x else "write")

    iops = df[df["jobname"].str.contains("iops")]

    bw_long = iops.melt(
        id_vars=["volume", "jobname", "jobtype"],
        value_vars=["read_bw_MB/s", "write_bw_MB/s"],
        var_name="bw_type",
        value_name="bw",
    )
    # Chnage 'storage-tests' to 'local'
    bw_long["volume"] = bw_long["volume"].apply(
        lambda x: "local" if x == "storage-tests" else x
    )
    # Change order of rows so in volume local is first, then nfs, then smb
    # (only if "local", "nfs", "smb")
    if all(x in bw_long["volume"].unique() for x in ["local", "nfs", "smb"]):
        bw_long["volume"] = pd.Categorical(bw_long["volume"], ["local", "nfs", "smb"])

    # remove rows with 0 bandwidth
    bw_long = bw_long[bw_long["bw"] > 0]
    plot_bandwidth(bw_long)

    with open("output/summary.json", "w") as f:
        json.dump(stats, f, indent=4)


if __name__ == "__main__":
    main()

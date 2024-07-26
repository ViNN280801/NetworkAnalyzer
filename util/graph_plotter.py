import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import logging
import os


class GraphPlotter:
    def __init__(self, network_usage_file, network_speed_file):
        self.network_usage_file = network_usage_file
        self.network_speed_file = network_speed_file

    def plot_graphs(self, xticks: int):
        """
        Plots the network usage and speed graphs from the given CSV files.
        """
        try:
            # Check if the files exist before attempting to read them
            if not os.path.exists(self.network_usage_file) or not os.path.exists(
                self.network_speed_file
            ):
                logging.error("One or both CSV files do not exist.")
                return

            # Load data from CSV files
            df_usage = pd.read_csv(self.network_usage_file)
            df_speed = pd.read_csv(self.network_speed_file)

            # Convert timestamp to HH:MM format
            df_usage["time"] = pd.to_datetime(df_usage["timestamp"]).dt.strftime(
                "%H:%M"
            )
            df_speed["time"] = pd.to_datetime(df_speed["timestamp"]).dt.strftime(
                "%H:%M"
            )

            # Convert bytes to megabytes for data usage
            df_usage["sent_MB"] = df_usage["sent_bytes"] / (1024 * 1024)
            df_usage["recv_MB"] = df_usage["recv_bytes"] / (1024 * 1024)

            # Convert speed to Mbps
            df_speed["download_Mbps"] = df_speed["download_speed"] / 1_000_000
            df_speed["upload_Mbps"] = df_speed["upload_speed"] / 1_000_000

            # Calculate average speeds
            avg_download_speed = df_speed["download_Mbps"].mean()
            avg_upload_speed = df_speed["upload_Mbps"].mean()

            plt.figure(figsize=(14, 7))

            # Data usage plot
            plt.subplot(2, 1, 1)
            plt.plot(
                df_usage["time"], df_usage["sent_MB"], "r-", label="Sent Data (MB)"
            )
            plt.plot(
                df_usage["time"], df_usage["recv_MB"], "b-", label="Received Data (MB)"
            )
            plt.xlabel("Time (HH:MM)")
            plt.ylabel("Data (MB)")
            plt.title("Data Usage Over Time")
            plt.xticks(np.arange(0, len(df_usage["time"]), step=xticks), rotation=45)
            plt.legend()
            plt.grid(True)

            # Speed plot
            plt.subplot(2, 1, 2)
            plt.plot(
                df_speed["time"],
                df_speed["download_Mbps"],
                "r-",
                label=f"Download Speed (Mbps), Avg: {avg_download_speed:.2f} Mbps",
            )
            plt.plot(
                df_speed["time"],
                df_speed["upload_Mbps"],
                "b-",
                label=f"Upload Speed (Mbps), Avg: {avg_upload_speed:.2f} Mbps",
            )
            plt.xlabel("Time (HH:MM)")
            plt.ylabel("Speed (Mbps)")
            plt.title("Speed Over Time")
            plt.xticks(np.arange(0, len(df_speed["time"]), step=xticks), rotation=45)
            plt.legend()
            plt.grid(True)

            plt.tight_layout()
            plt.show()
        except Exception as e:
            logging.error(f"Error plotting graphs: {e}")

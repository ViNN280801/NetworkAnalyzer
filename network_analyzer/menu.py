import schedule
import time
import signal
import sys
import os
import logging
from datetime import datetime
from .network_usage_analyzer import NetworkUsageAnalyzer, NETWORK_USAGE_ANALYZER
from .network_speed_analyzer import NetworkSpeedAnalyzer, NETWORK_SPEED_ANALYZER
from util import GraphPlotter


def setup_logger(name, log_file, level=logging.INFO):
    handler = logging.FileHandler(log_file)
    console_handler = logging.StreamHandler()

    handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(message)s"))
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
    )

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(console_handler)

    return logger


class Menu:
    def __init__(self):
        self.analysis_duration = 60
        self.analyze_speed = True
        self.analyze_usage = True
        self.frequency = 1
        self.xtick_interval = 5
        self.speed_logger = None
        self.usage_logger = None
        self.usage_analyzer = None
        self.speed_analyzer = None
        self.plotter = None
        signal.signal(signal.SIGINT, self.exit_gracefully)
        if hasattr(signal, "SIGALRM"):
            signal.signal(signal.SIGALRM, self.exit_gracefully)

    def show_menu(self):
        while True:
            print("\nMenu:")
            print("1. Start scan")
            print("2. Change settings")
            print("3. Show settings")
            print("4. Exit")
            choice = input("Enter your choice: ")

            if choice == "1":
                self.start_analysis()
            elif choice == "2":
                self.change_settings()
            elif choice == "3":
                self.show_settings()
            elif choice == "4":
                self.exit_program()
            else:
                print("Invalid choice. Please try again.")

    def show_settings(self):
        print("\nCurrent Settings:")
        print(f"Analysis Duration: {self.analysis_duration} minutes")
        print(f"Analyze Speed: {'Yes' if self.analyze_speed else 'No'}")
        print(f"Analyze Network Usage: {'Yes' if self.analyze_usage else 'No'}")
        print(f"Frequency of Measurements: {self.frequency} minutes")
        print(f"X-Tick Interval for Graphs: {self.xtick_interval}")

    def change_settings(self):
        while True:
            print("\nSettings:")
            print("1. Set analysis duration (in minutes)")
            print("2. Analyze speed? (yes/no)")
            print("3. Analyze network usage? (yes/no)")
            print("4. Set frequency of measurements (in minutes)")
            print("5. Set X-tick interval for graphs")
            print("6. Back to main menu")
            choice = input("Enter your choice: ")

            if choice == "1":
                self.set_analysis_duration()
            elif choice == "2":
                self.set_analyze_speed()
            elif choice == "3":
                self.set_analyze_usage()
            elif choice == "4":
                self.set_frequency()
            elif choice == "5":
                self.set_xtick_interval()
            elif choice == "6":
                break
            else:
                print("Invalid choice. Please try again.")

    def set_analysis_duration(self):
        try:
            self.analysis_duration = int(
                input("Enter analysis duration (in minutes): ")
            )
        except ValueError:
            print("Invalid input. Please enter a number.")

    def set_analyze_speed(self):
        choice = input("Analyze speed? (yes/no): ").strip().lower()
        if choice in ["y", "yes"]:
            self.analyze_speed = True
        elif choice in ["n", "no"]:
            self.analyze_speed = False
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

    def set_analyze_usage(self):
        choice = input("Analyze network usage? (yes/no): ").strip().lower()
        if choice in ["y", "yes"]:
            self.analyze_usage = True
        elif choice in ["n", "no"]:
            self.analyze_usage = False
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

    def set_frequency(self):
        try:
            self.frequency = int(
                input("Enter frequency of measurements (in minutes): ")
            )
        except ValueError:
            print("Invalid input. Please enter a number.")

    def set_xtick_interval(self):
        try:
            self.xtick_interval = int(input("Enter X-tick interval for graphs: "))
        except ValueError:
            print("Invalid input. Please enter a number.")

    def start_analysis(self):
        if not self.analyze_speed and not self.analyze_usage:
            print("No analysis selected. Exiting.")
            return

        if not os.path.exists("logs"):
            os.makedirs("logs")

        if not os.path.exists("results"):
            os.makedirs("results")

        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        speed_csv_file = None
        usage_csv_file = None

        if self.analyze_speed:
            speed_log_file = os.path.join("logs", f"{now}_speed.log")
            speed_csv_file = os.path.join("results", f"{now}_speed_measurement.csv")
            self.speed_logger = setup_logger("speed", speed_log_file)
            self.speed_analyzer = NetworkSpeedAnalyzer(
                speed_csv_file, self.speed_logger
            )
            schedule.every(self.frequency).minutes.do(self.speed_job)

        if self.analyze_usage:
            usage_log_file = os.path.join("logs", f"{now}_data_usage.log")
            usage_csv_file = os.path.join("results", f"{now}_network_usage.csv")
            self.usage_logger = setup_logger("usage", usage_log_file)
            self.usage_analyzer = NetworkUsageAnalyzer(
                usage_csv_file, self.usage_logger
            )
            schedule.every(self.frequency).minutes.do(self.usage_job)

        self.plotter = GraphPlotter(
            usage_csv_file if self.analyze_usage else None,
            speed_csv_file if self.analyze_speed else None,
        )

        if hasattr(signal, "SIGALRM"):
            signal.alarm(self.analysis_duration * 60)

        if self.usage_logger:
            self.usage_logger.info(
                f"{NETWORK_USAGE_ANALYZER}: Starting the analysis..."
            )
        if self.speed_logger:
            self.speed_logger.info(
                f"{NETWORK_SPEED_ANALYZER}: Starting the analysis..."
            )

        while True:
            schedule.run_pending()
            time.sleep(1)

    def usage_job(self):
        sent_bytes, recv_bytes = self.usage_analyzer.get_network_usage()
        if sent_bytes is not None and recv_bytes is not None:
            self.usage_analyzer.write_to_csv(sent_bytes, recv_bytes)

    def speed_job(self):
        download_speed, upload_speed = self.speed_analyzer.measure_speed()
        if download_speed is not None and upload_speed is not None:
            self.speed_analyzer.write_to_csv(download_speed, upload_speed)

    def exit_gracefully(self, signum, frame):
        if self.usage_logger:
            self.usage_logger.info(
                f"{NETWORK_USAGE_ANALYZER}: Received exit signal. Cleaning up..."
            )
        if self.speed_logger:
            self.speed_logger.info(
                f"{NETWORK_SPEED_ANALYZER}: Received exit signal. Cleaning up..."
            )
        schedule.clear()
        if self.plotter:
            self.plotter.plot_graphs(self.xtick_interval)
        sys.exit(0)

    def exit_program(self):
        if self.usage_logger:
            self.usage_logger.info(f"{NETWORK_USAGE_ANALYZER}: Exiting program...")
        if self.speed_logger:
            self.speed_logger.info(f"{NETWORK_SPEED_ANALYZER}: Exiting program...")
        schedule.clear()
        sys.exit(0)

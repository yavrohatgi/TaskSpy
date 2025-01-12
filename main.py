import time
import json
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os

LOG_INTERVAL = 2  # Time interval to sample activity (in seconds)
END_TIME = datetime.now() + timedelta(minutes=1)  # Run for how many minutes
LOG_FILE = "activity_log.json" # File to store activity logs
REPORT_DIR = "reports" # Directory to store generated reports

current_activity = {"application": None, "start_time": None} # Current activity being monitored
os.makedirs(REPORT_DIR, exist_ok=True) # Create the report directory if it doesn't exist

def get_active_window():
    """Get the currently active window's title."""
    try:
        import win32gui
        return win32gui.GetWindowText(win32gui.GetForegroundWindow())
    except ImportError:
        return "Unknown Application"

def log_activity(activity_name):
    """Log the current activity into the activity log."""
    global current_activity

    if current_activity["application"] == activity_name:
        return  # No change in activity

    # End previous activity and log it
    if current_activity["application"]:
        end_time = time.time()
        duration = end_time - current_activity["start_time"]
        entry = {
            "application": current_activity["application"],
            "start_time": datetime.fromtimestamp(current_activity["start_time"]).isoformat(),
            "end_time": datetime.fromtimestamp(end_time).isoformat(),
            "duration": duration
        }
        save_log(entry)

    # Start new activity
    current_activity["application"] = activity_name
    current_activity["start_time"] = time.time()

def save_log(entry):
    """Save a log entry to the log file."""
    try:
        with open(LOG_FILE, "a") as f:
            json.dump(entry, f)
            f.write("\n")
    except Exception as e:
        print(f"Error saving log: {e}")

def generate_reports():
    """Generate usage reports based on logged data."""
    try:
        # Read and summarize data
        with open(LOG_FILE, "r") as f:
            summary = {}
            for line in f:
                log = json.loads(line)
                app = log["application"]
                summary[app] = summary.get(app, 0) + log["duration"]

        # Plot the data
        if summary:
            plt.pie(summary.values(), labels=summary.keys(), autopct="%1.1f%%", startangle=140)
            plt.title("Time Usage Summary")
            timestamp = str(int(time.time()))
            report_file = os.path.join(REPORT_DIR, f"summary_{timestamp}.png")
            plt.savefig(report_file)
            plt.show()
            print(f"Report saved at: {report_file}")
        else:
            print("No data to generate a report.")

    except Exception as e:
        print(f"Error generating reports: {e}")

def main():
    """Main function to monitor and log activity."""
    print("Starting TimeSpy...")
    try:
        while datetime.now() < END_TIME:
            active_window = get_active_window()
            log_activity(active_window)
            time.sleep(LOG_INTERVAL)

        print("Reached the end time. Generating report...")
        generate_reports()

    except KeyboardInterrupt:
        print("Exiting TimeSpy early...")
        generate_reports()

if __name__ == "__main__":
    main()
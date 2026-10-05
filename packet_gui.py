import tkinter as tk
import subprocess
import re
import csv
import os
from datetime import datetime
import matplotlib.pyplot as plt


# Stores latest test information
response_times = []
packet_numbers = []
packet_details = []

comparison_text = "No comparison available yet."


# ---------------- GRAPH ----------------

def show_graph():

    if not response_times:
        result_label.config(
            text="Run a test first to view the graph."
        )
        return

    plt.figure(figsize=(7, 4))

    plt.plot(
        packet_numbers,
        response_times,
        marker="o"
    )

    plt.title("Packet Response Time")
    plt.xlabel("Packet Number")
    plt.ylabel("Response Time (ms)")
    plt.grid(True)

    plt.show()


# ---------------- HISTORY ----------------

def view_history():

    if not os.path.exists("test_history.csv"):
        result_label.config(
            text="No test history available."
        )
        return

    history_window = tk.Toplevel(window)

    history_window.title("Test History")
    history_window.geometry("800x400")
    history_window.configure(bg="#eef3f7")

    heading = tk.Label(
        history_window,
        text="Previous Network Tests",
        font=("Arial", 16, "bold"),
        bg="#eef3f7",
        fg="#1f3b57"
    )

    heading.pack(pady=15)

    text_box = tk.Text(
        history_window,
        width=95,
        height=17,
        font=("Consolas", 9)
    )

    text_box.pack(
        padx=15,
        pady=10
    )

    file = open(
        "test_history.csv",
        "r"
    )

    reader = csv.reader(file)

    for row in reader:
        text_box.insert(
            "end",
            " | ".join(row) + "\n"
        )

    file.close()


# ---------------- PACKET DETAILS ----------------

def show_packet_details():

    if not packet_details:
        result_label.config(
            text="Run a test first to view packet details."
        )
        return

    details_window = tk.Toplevel(window)

    details_window.title("Packet Details")
    details_window.geometry("450x450")
    details_window.configure(bg="#eef3f7")

    heading = tk.Label(
        details_window,
        text="Individual Packet Details",
        font=("Arial", 15, "bold"),
        bg="#eef3f7",
        fg="#1f3b57"
    )

    heading.pack(pady=15)

    text_box = tk.Text(
        details_window,
        width=48,
        height=19,
        font=("Consolas", 10)
    )

    text_box.pack(
        padx=15,
        pady=10
    )

    for detail in packet_details:

        text_box.insert(
            "end",
            detail + "\n"
        )


# ---------------- COMPARISON ----------------

def compare_with_previous(host, current_average):

    if not os.path.exists("test_history.csv"):
        return "No previous test available."

    file = open(
        "test_history.csv",
        "r"
    )

    reader = csv.reader(file)

    rows = list(reader)

    file.close()

    previous_average = None

    # Check previous tests from latest to oldest
    for row in reversed(rows):

        if len(row) >= 7 and row[1].lower() == host.lower():

            try:

                previous_average = float(row[6])
                break

            except ValueError:

                continue


    if previous_average is None:

        return "No previous test found for " + host


    difference = current_average - previous_average


    if abs(difference) < 5:

        result = "Response time is almost the same."

    elif difference > 0:

        result = "Response time has increased."

    else:

        result = "Response time has decreased."


    text = (
        "Previous Average : " +
        str(round(previous_average, 2)) + " ms"

        "\nCurrent Average  : " +
        str(round(current_average, 2)) + " ms"

        "\nDifference       : " +
        str(round(difference, 2)) + " ms"

        "\n\n" + result
    )

    return text


def show_comparison():

    compare_window = tk.Toplevel(window)

    compare_window.title("Network Comparison")
    compare_window.geometry("430x260")
    compare_window.configure(bg="#eef3f7")

    heading = tk.Label(
        compare_window,
        text="Test Comparison",
        font=("Arial", 15, "bold"),
        bg="#eef3f7",
        fg="#1f3b57"
    )

    heading.pack(pady=20)

    label = tk.Label(
        compare_window,
        text=comparison_text,
        font=("Arial", 11),
        bg="white",
        justify="left",
        padx=20,
        pady=15
    )

    label.pack(
        padx=25,
        fill="x"
    )


# ---------------- NETWORK TEST ----------------

def start_test():

    host = host_entry.get().strip()

    try:

        total_packets = int(
            packet_entry.get()
        )

    except ValueError:

        result_label.config(
            text="Please enter a valid number of packets."
        )

        return


    if total_packets <= 0:

        result_label.config(
            text="Number of packets should be greater than 0."
        )

        return


    if host == "":

        result_label.config(
            text="Please enter a website or IP address."
        )

        return


    global response_times
    global packet_numbers
    global packet_details
    global comparison_text


    received_packets = 0
    lost_packets = 0

    response_times = []
    packet_numbers = []
    packet_details = []


    result_label.config(
        text="Testing network...\nPlease wait."
    )

    window.update()


    # Send packets one by one
    for i in range(1, total_packets + 1):

        result = subprocess.run(
            [
                "ping",
                "-4",
                "-n",
                "1",
                host
            ],
            capture_output=True,
            text=True
        )


        # Return code 0 means ping succeeded
        if result.returncode == 0:

            received_packets += 1


            # Get response time from actual ping output
            match = re.search(
                r"time[=<]\s*(\d+)\s*ms",
                result.stdout,
                re.IGNORECASE
            )


            if match:

                response_time = int(
                    match.group(1)
                )

                response_times.append(
                    response_time
                )

                packet_numbers.append(i)

                packet_details.append(
                    "Packet " +
                    str(i) +
                    " -> Received | " +
                    str(response_time) +
                    " ms"
                )


            else:

                packet_details.append(
                    "Packet " +
                    str(i) +
                    " -> Received"
                )


        else:

            lost_packets += 1

            packet_details.append(
                "Packet " +
                str(i) +
                " -> Lost"
            )


        # Update GUI while test is running
        window.update()


    # Packet loss
    loss = (
        lost_packets /
        total_packets
    ) * 100


    # Response time calculation
    if response_times:

        average_time = (
            sum(response_times) /
            len(response_times)
        )

        minimum_time = min(
            response_times
        )

        maximum_time = max(
            response_times
        )

    else:

        average_time = 0
        minimum_time = 0
        maximum_time = 0


    # Show actual network results
    result_text = (
        "Packets Sent       : " +
        str(total_packets) +

        "\nPackets Received   : " +
        str(received_packets) +

        "\nPackets Lost       : " +
        str(lost_packets) +

        "\nPacket Loss        : " +
        str(round(loss, 2)) + "%"

        "\n\nAverage Delay      : " +
        str(round(average_time, 2)) + " ms"

        "\nMinimum Delay      : " +
        str(minimum_time) + " ms"

        "\nMaximum Delay      : " +
        str(maximum_time) + " ms"
    )


    result_label.config(
        text=result_text
    )


    # Compare with previous test
    # This is done before saving current test
    if response_times:

        comparison_text = compare_with_previous(
            host,
            average_time
        )

    else:

        comparison_text = (
            "No comparison available."
        )


    # ---------------- SAVE HISTORY ----------------

    file_name = "test_history.csv"

    file_exists = os.path.exists(
        file_name
    )

    current_time = datetime.now().strftime(
        "%d-%m-%Y %H:%M:%S"
    )


    file = open(
        file_name,
        "a",
        newline=""
    )

    writer = csv.writer(file)


    if not file_exists:

        writer.writerow([
            "Date & Time",
            "Destination",
            "Packets Sent",
            "Packets Received",
            "Packets Lost",
            "Packet Loss %",
            "Average Delay (ms)"
        ])


    writer.writerow([
        current_time,
        host,
        total_packets,
        received_packets,
        lost_packets,
        round(loss, 2),
        round(average_time, 2)
    ])


    file.close()


# ==================================================
#                     GUI
# ==================================================

window = tk.Tk()

window.title(
    "Packet Loss Detective"
)

window.geometry(
    "700x720"
)

window.configure(
    bg="#e8eef4"
)

window.resizable(
    False,
    False
)


# ---------------- HEADING ----------------

header = tk.Frame(
    window,
    bg="#1f3b57",
    height=100
)

header.pack(
    fill="x"
)


title = tk.Label(
    header,
    text="PACKET LOSS DETECTIVE",
    font=("Arial", 22, "bold"),
    bg="#1f3b57",
    fg="white"
)

title.pack(
    pady=(18, 2)
)


subtitle = tk.Label(
    header,
    text="Network Connectivity and Delay Analyzer",
    font=("Arial", 10),
    bg="#1f3b57",
    fg="#d9e4ee"
)

subtitle.pack()


# ---------------- NETWORK INPUT ----------------

input_frame = tk.LabelFrame(
    window,
    text="  Network Test  ",
    font=("Arial", 11, "bold"),
    bg="white",
    fg="#1f3b57",
    padx=25,
    pady=18
)

input_frame.pack(
    padx=45,
    pady=20,
    fill="x"
)


host_label = tk.Label(
    input_frame,
    text="Website / IP Address",
    font=("Arial", 10),
    bg="white"
)

host_label.grid(
    row=0,
    column=0,
    sticky="w",
    pady=8
)


host_entry = tk.Entry(
    input_frame,
    width=32,
    font=("Arial", 10)
)

host_entry.grid(
    row=0,
    column=1,
    padx=20,
    pady=8
)


packet_label = tk.Label(
    input_frame,
    text="Number of Packets",
    font=("Arial", 10),
    bg="white"
)

packet_label.grid(
    row=1,
    column=0,
    sticky="w",
    pady=8
)


packet_entry = tk.Entry(
    input_frame,
    width=32,
    font=("Arial", 10)
)

packet_entry.grid(
    row=1,
    column=1,
    padx=20,
    pady=8
)


start_button = tk.Button(
    input_frame,
    text="START NETWORK TEST",
    width=22,
    height=2,
    bg="#2d6a9f",
    fg="white",
    font=("Arial", 10, "bold"),
    command=start_test
)

start_button.grid(
    row=2,
    column=0,
    columnspan=2,
    pady=(15, 0)
)


# ---------------- RESULT AREA ----------------

result_frame = tk.LabelFrame(
    window,
    text="  Test Result  ",
    font=("Arial", 11, "bold"),
    bg="white",
    fg="#1f3b57"
)

result_frame.pack(
    padx=45,
    fill="x"
)


result_label = tk.Label(
    result_frame,
    text="Run a network test to view the result.",
    justify="left",
    anchor="w",
    font=("Arial", 10),
    bg="white",
    fg="#333333",
    padx=20,
    pady=15
)

result_label.pack(
    fill="x"
)


# ---------------- OPTIONS ----------------

option_label = tk.Label(
    window,
    text="More Options",
    font=("Arial", 11, "bold"),
    bg="#e8eef4",
    fg="#1f3b57"
)

option_label.pack(
    pady=(20, 7)
)


button_frame = tk.Frame(
    window,
    bg="#e8eef4"
)

button_frame.pack()


graph_button = tk.Button(
    button_frame,
    text="Show Graph",
    width=17,
    command=show_graph
)

graph_button.grid(
    row=0,
    column=0,
    padx=8,
    pady=6
)


history_button = tk.Button(
    button_frame,
    text="View History",
    width=17,
    command=view_history
)

history_button.grid(
    row=0,
    column=1,
    padx=8,
    pady=6
)


details_button = tk.Button(
    button_frame,
    text="Packet Details",
    width=17,
    command=show_packet_details
)

details_button.grid(
    row=1,
    column=0,
    padx=8,
    pady=6
)


compare_button = tk.Button(
    button_frame,
    text="Compare Test",
    width=17,
    command=show_comparison
)

compare_button.grid(
    row=1,
    column=1,
    padx=8,
    pady=6
)






window.mainloop()
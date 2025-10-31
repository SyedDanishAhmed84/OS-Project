import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random

st.set_page_config(page_title="CPU Scheduling Simulator", layout="wide")
st.title("🎓 CPU Scheduling Algorithms (Simple Version)")

# -----------------------------------------------------------
# 1️⃣  FCFS Algorithm
# -----------------------------------------------------------
def fcfs(processes):
    processes.sort(key=lambda p: p['arrival'])
    time = 0
    gantt = []
    results = {}

    for p in processes:
        if time < p['arrival']:
            # CPU is idle
            gantt.append({'pid': 'IDLE', 'start': time, 'end': p['arrival']})
            time = p['arrival']
        start = time
        end = start + p['burst']
        gantt.append({'pid': p['pid'], 'start': start, 'end': end})
        results[p['pid']] = {'arrival': p['arrival'], 'burst': p['burst'], 'completion': end}
        time = end
    return gantt, results

# -----------------------------------------------------------
# 2️⃣  SJF (Shortest Job First) - Non-preemptive
# -----------------------------------------------------------
def sjf(processes):
    processes.sort(key=lambda p: p['arrival'])
    ready = []
    gantt = []
    results = {}
    time = processes[0]['arrival']
    i = 0

    while len(results) < len(processes):
        while i < len(processes) and processes[i]['arrival'] <= time:
            ready.append(processes[i])
            i += 1

        if not ready:
            time = processes[i]['arrival']
            continue

        # pick process with shortest burst
        ready.sort(key=lambda p: p['burst'])
        p = ready.pop(0)
        start = time
        end = start + p['burst']
        gantt.append({'pid': p['pid'], 'start': start, 'end': end})
        results[p['pid']] = {'arrival': p['arrival'], 'burst': p['burst'], 'completion': end}
        time = end
    return gantt, results

# -----------------------------------------------------------
# 3️⃣  Priority Scheduling - Non-preemptive
# -----------------------------------------------------------
def priority(processes):
    processes.sort(key=lambda p: p['arrival'])
    ready = []
    gantt = []
    results = {}
    time = processes[0]['arrival']
    i = 0

    while len(results) < len(processes):
        while i < len(processes) and processes[i]['arrival'] <= time:
            ready.append(processes[i])
            i += 1

        if not ready:
            time = processes[i]['arrival']
            continue

        # pick process with smallest priority number (1 = highest)
        ready.sort(key=lambda p: p['priority'])
        p = ready.pop(0)
        start = time
        end = start + p['burst']
        gantt.append({'pid': p['pid'], 'start': start, 'end': end})
        results[p['pid']] = {'arrival': p['arrival'], 'burst': p['burst'], 'completion': end}
        time = end
    return gantt, results

# -----------------------------------------------------------
# 4️⃣  Round Robin
# -----------------------------------------------------------
def round_robin(processes, quantum):
    processes.sort(key=lambda p: p['arrival'])
    time = processes[0]['arrival']
    gantt = []
    ready = []
    remaining = {p['pid']: p['burst'] for p in processes}
    completed = {}
    i = 0

    while len(completed) < len(processes):
        while i < len(processes) and processes[i]['arrival'] <= time:
            ready.append(processes[i])
            i += 1

        if not ready:
            time = processes[i]['arrival']
            continue

        p = ready.pop(0)
        pid = p['pid']
        run_time = min(quantum, remaining[pid])
        start = time
        end = start + run_time
        gantt.append({'pid': pid, 'start': start, 'end': end})
        remaining[pid] -= run_time
        time = end

        # add new arrivals to queue
        while i < len(processes) and processes[i]['arrival'] <= time:
            ready.append(processes[i])
            i += 1

        if remaining[pid] > 0:
            ready.append(p)
        else:
            completed[pid] = time

    results = {p['pid']: {'arrival': p['arrival'], 'burst': p['burst'], 'completion': completed[p['pid']]} for p in processes}
    return gantt, results

# -----------------------------------------------------------
# Helper: Calculate Waiting & Turnaround Time
# -----------------------------------------------------------
def calculate_metrics(results):
    data = []
    for pid, r in results.items():
        tat = r['completion'] - r['arrival']
        wt = tat - r['burst']
        data.append([pid, r['arrival'], r['burst'], r['completion'], tat, wt])
    df = pd.DataFrame(data, columns=['PID', 'Arrival', 'Burst', 'Completion', 'Turnaround', 'Waiting'])
    avg_wt = df['Waiting'].mean()
    avg_tat = df['Turnaround'].mean()
    return df, avg_wt, avg_tat

# -----------------------------------------------------------
# Helper: Plot Gantt Chart
# -----------------------------------------------------------
def plot_gantt(gantt):
    fig, ax = plt.subplots(figsize=(8, 2))
    y, height = 10, 6
    for g in gantt:
        color = 'lightgray' if g['pid'] == 'IDLE' else None
        ax.broken_barh([(g['start'], g['end'] - g['start'])], (y, height), facecolors=color)
        if g['pid'] != 'IDLE':
            ax.text((g['start'] + g['end']) / 2, y + height / 2, g['pid'], ha='center', va='center')
    ax.set_xlabel("Time")
    ax.set_yticks([])
    ax.set_title("Gantt Chart")
    return fig

# -----------------------------------------------------------
# Streamlit Interface
# -----------------------------------------------------------
algo = st.selectbox("Select Algorithm", ["FCFS", "SJF", "Priority", "Round Robin"])
quantum = st.number_input("Time Quantum (RR only)", 1, 10, 2)
n = st.number_input("Number of Processes", 1, 10, 4)

default_data = pd.DataFrame({
    "PID": [f"P{i+1}" for i in range(int(n))],
    "Arrival": [i for i in range(int(n))],
    "Burst": [random.randint(2, 8) for _ in range(int(n))],
    "Priority": [random.randint(1, 3) for _ in range(int(n))]
})

st.write("### Process Table")
df = st.data_editor(default_data, num_rows="dynamic")

if st.button("Run Simulation"):
    processes = [
        {'pid': row.PID, 'arrival': row.Arrival, 'burst': row.Burst, 'priority': row.Priority}
        for _, row in df.iterrows()
    ]

    if algo == "FCFS":
        gantt, results = fcfs(processes)
    elif algo == "SJF":
        gantt, results = sjf(processes)
    elif algo == "Priority":
        gantt, results = priority(processes)
    else:
        gantt, results = round_robin(processes, quantum)

    metrics_df, avg_wt, avg_tat = calculate_metrics(results)
    st.pyplot(plot_gantt(gantt))
    st.dataframe(metrics_df)
    st.write(f"*Average Waiting Time:* {avg_wt:.2f}")
    st.write(f"*Average Turnaround Time:* {avg_tat:.2f}")

st.caption("🧠 Simple CPU Scheduling Simulator — for OS Learning (Ayaz 2025)")
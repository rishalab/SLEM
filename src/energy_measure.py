import os
import time
from functools import wraps
import csv
import pynvml


class EnergyTracker:
    def __init__(self):
        self.rapl_path = "/sys/class/powercap/intel-rapl"
        self.domains = self._get_domains()
        self.gpus = self._get_gpus()
        self.state = "idle"

    def _get_domains(self):
        socket = 0
        domains = {}
        while True:
            socket_path = self.rapl_path + "/intel-rapl:" + str(socket)
            if not os.path.exists(socket_path):
                break
            domains[open(socket_path+"/name").read().strip()
                    ] = socket_path + "/energy_uj"
            domain = 0
            while True:
                domain_path = socket_path + "/intel-rapl:" + \
                    str(socket) + ":" + str(domain)
                if not os.path.exists(domain_path):
                    break
                domains[open(domain_path+"/name").read().strip()
                        + "-" + str(socket)] = domain_path+"/energy_uj"
                domain += 1
            socket += 1
        return domains

    def _get_gpus(self):
        try:
            pynvml.nvmlInit()
            gpus = {}
            for i in range(pynvml.nvmlDeviceGetCount()):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                gpus[f"nvidia-gpu-{i}"] = handle
            return gpus
        except:
            return None

    def _get_energy(self):
        energy = {}
        for domain in self.domains:
            energy[domain] = int(open(self.domains[domain]).read().strip())
        if self.gpus:
            for i in self.gpus:
                energy[i] = pynvml.nvmlDeviceGetTotalEnergyConsumption(
                    self.gpus[i])
        return energy

    def start(self):
        if self.state == "idle":
            self.start_energy = self._get_energy()
            self.start_time = time.time()
            self.state = "running"
        else:
            print("Already running")

    def stop(self):
        if self.state == "running":
            self.stop_energy = self._get_energy()
            self.stop_time = time.time()
            self.state = "idle"
        else:
            print("Not running")

    def compute(self):
        if self.state == "running":
            return
        energy = {}
        for domain in self.domains:
            energy[domain] = self.stop_energy[domain] - \
                self.start_energy[domain]
        if self.gpus:
            for i in self.gpus:
                energy[i] = self.stop_energy[i] - self.start_energy[i]
        return energy

    def save_csv(self, filename):
        energy = self.compute()
        duration = self.stop_time - self.start_time
        with open(filename, "a") as f:
            writer = csv.writer(f)
            if f.tell() == 0:
                writer.writerow(["Domain", "Energy (micro joules)", "Duration (s)"])
            for domain in energy:
                writer.writerow([domain, energy[domain], duration])


def measure_energy(func, fname):
    @wraps(func)
    def wrapper(*args, **kwargs):
        et = EnergyTracker()
        et.start()
        result = func(*args, **kwargs)
        et.stop()
        et.save_csv(f"{fname}")
        return result
    return wrapper


if __name__ == "__main__":
    et = EnergyTracker()
    et.start()
    time.sleep(5)
    et.stop()
    et.save_csv("test.csv")
    print("Wrote measurement to test.csv")

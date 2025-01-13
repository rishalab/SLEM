import os
import sys
import time
import io
import contextlib
import datetime

# Determine the base path
if getattr(sys, 'frozen', False):  # Running as a PyInstaller executable
    base_path = sys._MEIPASS
else:  # Running as a script
    base_path = os.path.dirname(os.path.abspath(__file__))

# Read files using the base path
init_config_path = os.path.join(base_path, "init.config")
energy_measure_path = os.path.join(base_path, "energy_measure.py")

INIT_DATA = open(init_config_path).read()
MEASURE_ENERGY = open(energy_measure_path).read()


class Runner:

    def run(self, mname: str, fname: str, args, frquency: int, interval: int, csv: str, dataset: dict) -> str:
        output = io.StringIO()
        dataframes = """import pandas\n"""
        for data in dataset:
            dataframes += f"""{data} = pandas.read_csv("{dataset[data]}")\n"""
        with contextlib.redirect_stdout(output):
            for _ in range(frquency):
                if not csv:
                    csv = f"""{mname.strip()}-{fname.strip()
                                               }-{datetime.datetime.now()}.csv"""
                try:
                    exec(
                        f"""
{INIT_DATA}
{dataframes}
from {mname.strip()} import {fname}
{MEASURE_ENERGY}

evaluated_args = {{}}
raw_args = {args}
for key, value in raw_args.items():
    try:
        evaluated_args[key] = eval(value, globals(), locals())
    except Exception as e:
        evaluated_args[key] = value
et = EnergyTracker()
et.start()
result = {fname}(**evaluated_args)
et.stop()
et.save_csv(f"{csv}")
# measure_energy({fname},'{csv}')(**evaluated_args)

""", globals())
                    time.sleep(interval)
                except SyntaxError as e:
                    print("Syntax Error:")
                    print(f"Message: {e.msg}")
                    print(f"Line: {e.lineno}, Offset: {e.offset}")
                    print(f"Text: {e.text.strip() if e.text else None}")
                except Exception as e:
                    print(f"Exception occurred:{e}")
        return output.getvalue() + f"Wrote measurement to {csv}"

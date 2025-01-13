# SLEM : Software Library Energy Meter

### An Automated Energy Measurement Tool for Software Libraries
- SLEM is an energy measurement tool designed to measure energy consumption seamlessly across various software frameworks, libraries, and custom scripts.
- At its core, SLEM utilizes the Intel Running Average Power Limit (RAPL) interface, a widely recognized mechanism for monitoring and reporting the energy consumption of vari- ous system-on-chip (SoC) power domains.
- The tool features a user-friendly interface that eliminates the need for manual script writing, allowing users to seamlessly specify input parameters for API-level energy consumption measurements.
- The current version of the tool supports only Linux , with plans to extend support to Windows and MacOS in future updates.
___
## Installation Instructions and Usage
1. Clone the repo
   ```bash
   git clone https://github.com/rishalab/SLEM.git
   ```
2. Navigate to the **`src`** folder:
   ```bash
   cd SLEM/src
   ```
3. Run the **`main.py`** file:
   ```bash

   python3 main.py
   ```
   or
   ```bash
   python main.py
   ```
4. Upon running **`main.py`**, the following screen will appear:

   ![SLEM](https://github.com/user-attachments/assets/2ae78ec7-9d6c-4424-9b92-920f1ed624cf)

6. The interface contains the following sections:
   - Module Selection
   - File Selection
   - Dataset Selection
   - Module Manager
   - Dataset Manager
   - Reporting Module
   - Parameter Configuration Screen

7. To measure the energy consumption of a specific module (e.g., **`numpy`**), follow these steps:
   - Enter the module name in the Module Manager (e.g., **`numpy`**).
   - Click the **Add** button.
   - The module will then be available in the Module Selection dropdown on the left side of the screen.

8. Select the desired module from the dropdown to display all its functions, as shown below:
  ![numpy](https://github.com/user-attachments/assets/e03adec8-7ca1-466d-8180-c989f720ecd1)

9. Select the checkbox of the function you want to measure. The parameters of the selected function will appear in the Parameter Configuration Screen.

10. Adjust the parameters as needed, specify the frequency (number of iterations), and set the interval time (time gap between iterations in seconds).

11. Click the **Run** button to execute the experiment. The results will be displayed in the Reporting Module at the bottom.

12. You can also define your own functions in a Python file (e.g., **`measure_energy.py`**):
    - Click the **Browse** button in the File Selection module to navigate to and select your file.
    - Select your file from the Module Selection dropdown. All defined functions in the file will be displayed below.

13. To upload a dataset:
    - Click the **Browse** button in the Dataset Manager section and select the desired dataset.
    - Each loaded dataset is assigned a dataframe ID (e.g., **`df_0`**), visible in the Dataset Manager section at the bottom right.
  
    ![Dataset_Manager](https://github.com/user-attachments/assets/e52f9232-a507-4fb4-bbaf-6ebd937842a7)

15. The dataframe ID (e.g., **`df_0`**) can be used as an argument in functions requiring dataset input.

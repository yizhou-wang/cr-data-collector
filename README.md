# Camera/Radar Data Collection Tools
This is a repository for Camera/Radar data collection tools, including operating the sensors, image/radar data preprocessing, sensor calibration.

## Installation
1. Install Anaconda.
2. Clone this repository to your local laptop.
3. Setup Python environment in Anaconda Prompt:
```
cd cr-data-collector
conda create --name datacol --file requirements.txt
```
4. Download Spinnaker Python SDK
    1) Download Spinnaker Python SDK: https://www.flir.com/products/spinnaker-sdk/
    2) DOWNLOAD NOW => DOWNLOAD FROM BOX => Windows => Latest Python Spinnaker => 
    x86: `spinnaker_python-1.23.0.27-cp36-cp36m-win32.zip` / x64: `spinnaker_python-1.23.0.27-cp36-cp36m-win_amd64.zip`
5. Activate conda env:
```
activate datacol
```
6. Unzip downloaded Python SDK and follow `README.txt` "1.1 Installation for Windows". 


## Run data collector
1. Activate conda env:
```
activate datacol
```
2. Run script:
```
python run_datacol.py
```
3. Set configurations:

    There are several configurations need to be set as follows. If you input nothing, it will use the default values.
    - Base directory: the place to store collected data. Default to be `D:\RawData`.
    - Sequence number: the number of sequences to be collected. Default to be 1. (if == 1, sequence name is needed; else, use `onrd_xxx`)
    - Sequence name: the name of the current sequence. Does not have default value.
    - Frame rate: the frame rate of the camera. Default to be 30 FPS.
    - Number of images: the number of images need to be collected in this sequence. Default to be 30. 

    Here is an example output of running this script:
    ```
    (datacol) D:\data-collection-tools\cr-data-collector>python run_datacol.py
    Enter base directory (default='D:\RawData'):
    Enter sequence number (default=1): 3
    Enter frame rate (default=30):
    Enter number of images (default=30):
    Input configurations:
            Base Directory:          D:\RawData\2019_06_26
            Sequence Number:         3
            Sequence Name:           ['2019_06_26_onrd012', '2019_06_26_onrd013', '2019_06_26_onrd014']
            Framerate:               30
            Image Number:            30
    
    Are the above configurations correct? (y/n) y    ......
    ```
4. When all the configurations are set, press enter to start recording.
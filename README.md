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
- Sequence name: the name of the current sequence. Does not have default value.
- Frame rate: the frame rate of the camera. Default to be 30 FPS.
- Number of images: the number of images need to be collected in this sequence. Default to be 30. 

Here is an example output of running this script:
```
(datacol) D:\data-collection-tools\cr-data-collector>python run_datacol.py
Enter base directory (default='D:\RawData'):
Enter sequence number: 000
Enter frame rate (default=30):
Enter number of images (default=30):
Input configurations:
        Base Directory:  D:\RawData\2019_06_26
        Series No.:      2019_06_26_000
        Framerate:       30
        Image Number:    30

Are the above configurations correct? (y/n) y
D:\RawData\2019_06_26\2019_06_26_000
......
```
4. When all the configurations are set, press enter to start recording.
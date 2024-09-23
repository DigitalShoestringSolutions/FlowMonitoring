# Flow Monitoring Starter Solution

### Download
- Clone this repo `git clone https://github.com/DigitalShoestringSolutions/FlowMonitoring`
- Open the downloaded folder `cd FlowMonitoring`

### Configure & Assemble
- Edit the config file to set machine name, source and calibration value `nano UserConfig/Sensing/main.py`
- Check the recipe contains the Service Modules you desire `nano recipe.txt`
- Assemble the Service Modules `ServiceModules/Asssembly/get_service_modules.sh`
- Restart to apply the settings to the downloaded Service Modules

### Build & Run
- Build the docker containers `docker compose build`
- Start the docker containers `./start.sh`

### Usage
- View the dashboard: navigate to `localhost:3000` in a web browser
<br>

![image](https://github.com/user-attachments/assets/97a5696b-3463-4fef-a711-a669d68375a8)
_Individual sensor dashboard_

<br>

![image](https://github.com/user-attachments/assets/88d2a9cb-de4e-43ac-8e6e-dfe2267284ec)
_All Sensors dashboard showing two sensors_

# Shoestring Dashboard User Interface Service Module
## Description
This user interface service module uses [grafana](https://grafana.com/), to present timeseries measurements and metrics using graphs, dials, etc. 

## How it works
We use grafana's [provisioning system](https://grafana.com/docs/grafana/latest/administration/provisioning/) to set things up correctly from the beginning. The first step is to set up the datasources we need. The config files for this are found at `config/provisioning/datasources`. This repository is set up with an influxdb datasource. If you need, add further provisioning files here to create additional data sources.
>For more details on influxdb and the use of the `.env` file in docker compose to share environment variables see the [Shoestring timeseries database service module](https://github.com/DigitalShoestringSolutions/sm_timeseries_db).

Next is dashboards - the provisioning file is found at  `config/provisioning/dashboard` but you shouldn't need to change this. The `json` descriptions of the dashboards are stored at `config/dashboards`. The folder structure below this point will be caried into grafana when the dashboards are loaded, so in this case grafana will start with a `Stoppage Monitoring` folder than contains four dashboards.

You can replace or add to these dashboards by:
1. creating your desired dashboard in grafana
1. go to `settings/JSON Model`
1. copy the contents
1. open a new `.json` file at the desired location in `config/dashboards`
1. paste the contents and save

> It is critical that the grafana instance you use to create dashboards has had its inputs provisioned in the same way as the target system ***so that the datasource ids match*** otherwise the loaded dashboards won't query data correctly

## Docker details
Docker needs to be started with the `start.sh` script which primes the compose file with the current user id as an environment variable so that grafana can be started with the same user id to reduce file permission issues

#/bin/bash

#paleidinejam servisus
python3.6 ./run_integration_service.py restart
sleep 1
python3.6 ./run_scheduler_service.py restart
sleep 2
python3.6 ./run_aes_scheduler_service.py restart
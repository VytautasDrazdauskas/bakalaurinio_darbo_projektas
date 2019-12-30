#!/bin/bash

pip freeze | grep -v pkg-resources > app/requirements.txt
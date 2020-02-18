#!/bin/bash

pip freeze | grep -v pkg-resources > service/requirements.txt
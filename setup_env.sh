#!/bin/env bash

DISK_PATH='/media/ramDisk'

sudo mkdir -p $DISK_PATH
sudo mount -t tmpfs -o size=24G tmpfs $DISK_PATH




#!/usr/bin/env bash

USER=ubuntu
NAME=voxceleb

DIR=/opt/$NAME
SERVICE_NAME="${NAME}_bot.service"
SERVICE_FILE_PATH=/etc/systemd/system/$SERVICE_NAME

rm -rf $DIR $SERVICE_FILE_PATH
systemctl disable --now $SERVICE_NAME

cat bot.service > $SERVICE_FILE_PATH
sed -i "s/<name>/$NAME/g" $SERVICE_FILE_PATH
sed -i "s/<user>/$USER/g" $SERVICE_FILE_PATH

mkdir $DIR $DIR/env $DIR/data
apt install -y python3-pip python3-venv
pip3 install virtualenv gdown
python3 -m venv $DIR/env

source $DIR/env/bin/activate
pip3 install --no-cache-dir cython wheel
pip3 install --no-cache-dir -r requirements.txt
deactivate

cp -r . $DIR
gdown --id 1up5kZYuam340giqNp72-Cg2XwYiC2fTG -O $DIR/vox.csv
gdown --id 1eL2OakHyvWL7mCdOu3UAxERIwL1lxJvy -O $DIR/ecapa_vox.npy

chmod 755 $DIR
chown -R $USER:$USER $DIR

systemctl daemon-reload
systemctl enable --now $SERVICE_NAME
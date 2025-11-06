@echo off
echo Copying files to dist folder...

copy config.json dist\
copy Train_Model.py dist\
copy train_controller_sw.py dist\
copy HW_Train_Controller.py dist\
copy Track_Model.py dist\
copy train_data.py dist\
copy clock.py dist\
copy TrainSocketServer.py dist\
copy *.png dist\
copy *.xlsx dist\

mkdir dist\client
copy client\main_control_panel.py dist\client\

echo.
echo ✓ All files copied to dist folder!
echo You can now run: dist\launch_all_modules.exe
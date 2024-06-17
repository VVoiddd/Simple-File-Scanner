@echo off
:: Display a message indicating the start of the installation process
echo Installing required packages...

:: Install the required Python packages from the requirements.txt file
pip install -r requirements.txt

:: Display a completion message
echo Installation complete. You can now run the application with 'python SFS.pyw'.

:: Prevent the command prompt from closing immediately
pause

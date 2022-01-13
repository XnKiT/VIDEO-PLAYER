echo "Cloning Repo..."
git clone -b main https://github.com/LEGEND-ANKIT/TELEGRAM-VC-STREAMER /Ankit
cd /Ankit

echo "Installing Requirements..."
pip3 install -U -r requirements.txt

echo "Starting Bot..."
python3 ankit.py

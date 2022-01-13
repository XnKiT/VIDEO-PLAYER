echo "Cloning Repo..."
git clone -b main https://github.com/LEGEND-ANKIT/VIDEO-PLAYER /VIDEO-PLAYER
cd /VIDEO-PLAYER

echo "Installing Requirements..."
pip3 install -U -r requirements.txt

echo "Starting Bot..."
python3 vidstream.py

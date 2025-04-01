sudo systemctl stop project
kill $(lsof -t -i:8000)
git checkout main
git pull
source activate.sh
pip install -r requirements.txt
sudo cp ./project.service /etc/systemd/system/project.service
sudo systemctl daemon-reload
sudo systemctl restart project
echo | systemctl status project

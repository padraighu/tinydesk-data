sudo yum update -y
sudo yum install git
git clone https://github.com/padraighu/tinydesk-data.git

sudo yum install -y yum-utils
sudo yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo

sudo yum install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo systemctl start docker

docker compose build
docker compose up -d

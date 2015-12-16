#!/bin/bash

# The Postgresql version to install
PGSQL_VERSION=9.3

# ----- Pre-running check

# Make sure only root can run our script
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

# ----- Locales fixing

# Fix locale to UTF-8
cat <<EOT >> /etc/bash.bashrc

export LANGUAGE=fr_FR.UTF-8
export LANG=fr_FR.UTF-8
export LC_ALL=fr_FR.UTF-8
EOT

# Regenerate locales
locale-gen fr_FR.UTF-8
dpkg-reconfigure locales

# Update locales to UTF-8 for the script now
export LANGUAGE=fr_FR.UTF-8
export LANG=fr_FR.UTF-8
export LC_ALL=fr_FR.UTF-8

# Extra APT

# Elastic search engine
wget -qO - https://packages.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb http://packages.elastic.co/elasticsearch/2.x/debian stable main" | sudo tee -a /etc/apt/sources.list.d/elasticsearch-2.x.list

# ----- System update

# Update the apt-get database
apt-get update -y

# Check for update and install
apt-get upgrade -y

# ----- Python installation

# Install python 3.4
apt-get install -y python3.4

# Install python dev packages
apt-get install -y build-essential python3-dev python3-setuptools python3-pip

# Install git client for pip
apt-get install -y git gettext

# Install python env packages
apt-get install -y python-virtualenv

# ----- Python environment creation

# Create the python 3.4 virtual environment 
#sudo -u vagrant mkdir /home/vagrant/.pip_download_cache
sudo -u vagrant virtualenv /home/vagrant/virtualenv --no-site-packages -p /usr/bin/python3.4

# Auto activate the environment on shell login
cat <<EOT >> /home/vagrant/.bashrc

#export PIP_DOWNLOAD_CACHE=/home/vagrant/.pip_download_cache
source /home/vagrant/virtualenv/bin/activate
EOT

# Install dependencies for Pillow (drop-in replacement for PIL)
# supporting: jpeg, tiff, png, freetype, littlecms
apt-get install -y libjpeg-dev libtiff-dev zlib1g-dev libfreetype6-dev liblcms2-dev

# ----- Postgresql installation

# Install the postgresql server and extras
apt-get install -y postgresql-$PGSQL_VERSION postgresql-contrib-$PGSQL_VERSION

# Install dependencies for psycopg2 (postgresql python client)
apt-get install -y libpq-dev

# Configure the server
cat <<EOT > /etc/postgresql/$PGSQL_VERSION/main/pg_hba.conf
# If you change this first entry you will need to make sure that the
# database superuser can access the database using some other method.
# Noninteractive access to all databases is required during automatic
# maintenance (custom daily cronjobs, replication, and similar tasks).
#
# Database administrative login by Unix domain socket
local   all             postgres                                peer

# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             all                                     peer
# IPv4 local connections:
host    all             all             127.0.0.1/32            md5
# IPv6 local connections:
host    all             all             ::1/128                 md5
EOT

# Reload the configuration file
/etc/init.d/postgresql reload

# Create the database for the "vagrant" user
# Will drop an error because postgres cannot cd to /root, ignore it
sudo -u postgres createdb vagrant
sudo -u postgres createdb test_vagrant

# Create the "vagrant" user with "vagrant" password
sudo -u postgres psql -c "CREATE USER vagrant WITH ENCRYPTED PASSWORD 'vagrant';"

# Grant all privileges on the database "vagrant" for the "vagrant" user
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE vagrant TO vagrant;"
sudo -u postgres psql -c "ALTER DATABASE vagrant OWNER TO vagrant"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE test_vagrant TO vagrant;"
sudo -u postgres psql -c "ALTER DATABASE test_vagrant OWNER TO vagrant"
sudo -u postgres psql -c "ALTER USER vagrant CREATEDB;"

# ----- Memcached installation

# Install the memcached service
apt-get install -y memcached

# Install dependencies for pyLibMC (memcached client for python)
apt-get install -y libmemcached-dev zlib1g-dev libssl-dev

# ----- Elastic search engine
sudo apt-get install -y default-jre elasticsearch
sudo update-rc.d elasticsearch defaults 95 10

# ----- Virtualenv provisioning
# TODO

# ----- Cleanup
apt-get clean
apt-get autoclean

# ----- VMDK compression fix
dd if=/dev/zero of=/EMPTY bs=1M
rm -f /EMPTY

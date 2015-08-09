# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

# Vagrant configuration
Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  # Ubuntu box "made by skywodd" (it's just a vanilla Ubuntu 14.04.1 LTS)
  config.vm.box = "skywodd/trusty64"
  config.vm.box_url = "http://192.168.2.1/vagrant-basebox-trusty64.json"

  # Forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine.
  config.vm.network "forwarded_port", guest: 80, host: 8080   # Webserver
  config.vm.network "forwarded_port", guest: 8000, host: 8000 # Django test server

  # VirtualBox customization
  config.vm.provider "virtualbox" do |vb|

    # Boost memory (for database, memcache, etc)
    vb.memory = "2048"
	
	# Boost processor count (for multiple services running)
	vb.cpus = 2
  end

  # Enable provisioning with a shell script.
  config.vm.provision "shell", path: "provisioning.sh"
  
end

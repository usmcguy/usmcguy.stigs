ANSIBLE_LOG_PATH="./rhel8stig_supp-$(date +%Y%m%d-%H%M%S).log" ansible-playbook -v -b -i inventory site.yml

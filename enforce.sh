ansible-playbook -v -b -i inventory site.yml 2>&1 | tee "./rhel8stig_supp-$(date +%Y%m%d-%H%M%S).log"

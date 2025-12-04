# Execute ap_manager without asking password
# echo 'ALL ALL=NOPASSWD: /usr/bin/ap_manager' | sudo EDITOR='tee -a' visudo -f ap_manager
echo 'ALL ALL=NOPASSWD: /home/skye/.local/bin/ap_manager' | sudo EDITOR='tee -a' visudo -f ap_manager
echo 'ALL ALL=NOPASSWD: /home/skye/.local/bin/ap' | sudo EDITOR='tee -a' visudo -f ap

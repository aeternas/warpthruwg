# WARP-thru-WG ready-to-use solution

This repo contains an Ansible deployment of dockerised solution that runs the wg-easy/Amnezia web UI compose stack and prepares a Cloudflare WARP wgcf WireGuard interface as outbound. IPv6 works like a charm for `networking_mode: host` deployment.

## Files

- `deploy.yml`: main playbook
- `inventory.ini.example`: sample inventory
- `group_vars/all.yml.example`: sample variables

## Usage

```bash
cd ansible
cp inventory.ini.example inventory.ini
mkdir -p group_vars
cp group_vars/all.yml.example group_vars/all.yml
ansible-playbook -i inventory.ini deploy.yml
```


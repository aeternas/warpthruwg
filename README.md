# WARP-thru-WG ready-to-use solution

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


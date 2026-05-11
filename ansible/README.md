# Ansible deployment

This playbook deploys the compose stack from this repo and prepares a `wgcf`
WireGuard interface on an Ubuntu VPS.

## Files

- `deploy.yml`: main playbook
- `inventory.ini.example`: sample inventory
- `group_vars/all.yml.example`: sample variables

## What it does

1. Installs `docker.io`, `docker-compose-v2`, `iproute2`, `wireguard-tools`, and `iptables`
2. Copies the selected compose file from this repo to the VPS as
   `/opt/warpthruwg/docker-compose.yml`
3. Starts the compose stack with `docker compose up -d`
4. Downloads `wgcf` for Linux AMD64
5. Registers and generates `/etc/wireguard/wgcf.conf` unless you disable that
6. Enables `wg-quick@wgcf`
7. Enables host IPv4 and IPv6 forwarding
8. Injects `Table = off` plus IPv4 and IPv6 `PostUp` / `PostDown` policy
   routing rules into `wgcf.conf`, so only Amnezia client traffic is marked,
   forwarded, and masqueraded out through WARP

## Usage

```bash
cd /Users/ivangolikov/Development/warpthruwg/ansible
cp inventory.ini.example inventory.ini
mkdir -p group_vars
cp group_vars/all.yml.example group_vars/all.yml
ansible-playbook -i inventory.ini deploy.yml
```

## Compose modes

- `warpthruwg_mode: host` uses `wg-easy/docker-compose.yml`
- `warpthruwg_mode: bridge` uses `wg-easy/docker-compose-bridge.yml`

In bridge mode, the admin panel is bound to `127.0.0.1:8080`.

## Notes

- The playbook assumes Ubuntu with `apt`.
- `wgcf register --accept-tos` is used when `wgcf_register: true`.
- The systemd unit used is the standard `wg-quick@wgcf`.
- `iproute2` is installed explicitly because the WARP steering uses `ip rule`
  and `ip route`.
- `net.ipv4.conf.all.src_valid_mark=1` is enabled to make fwmark-based routing
  behave correctly with reverse-path validation.
- `Table = off` is set on `wgcf`, so WARP does not replace the VPS main
  default route.
- The generated rules mark packets by ingress interface name, not by CIDR.
- In `host` mode the WARP egress rules match WireGuard-style interfaces such as
  `wg0` and `awg0` via the patterns `wg+` and `awg+`.
- In `bridge` mode the WARP egress rules match Docker bridge interfaces via
  `docker0` and `br+`.
- If your setup uses different interfaces, extend
  `amnezia_extra_forward_iface_patterns`.
- If you prefer to manage `/etc/wireguard/wgcf.conf` yourself, set
  `wgcf_register: false` and place the file on the server before running the
  playbook.

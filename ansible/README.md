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
3. Copies the local Dockerfile and patch files used to build the
   `warpthruwg/amneziawg-web-ui:ipv6` image
4. Builds the compose image, then starts the stack with `docker compose up -d`
5. Downloads `wgcf` for Linux AMD64
6. Registers and generates `/etc/wireguard/wgcf.conf` unless you disable that
7. Enables `wg-quick@wgcf`
8. Enables host IPv4 forwarding, IPv6 forwarding, and IPv6 on newly created
   interfaces
9. Injects `Table = off` plus IPv4 and IPv6 `PostUp` / `PostDown` policy
   routing rules into `wgcf.conf`, so only Amnezia client traffic is marked,
   forwarded, and masqueraded out through WARP

## Usage

```bash
cd ansible
cp inventory.ini.example inventory.ini
mkdir -p group_vars
cp group_vars/all.yml.example group_vars/all.yml
ansible-playbook -i inventory.ini deploy.yml
```

## Compose modes

- `warpthruwg_mode: host` uses `wg-easy/docker-compose.yml`
- `warpthruwg_mode: bridge` uses `wg-easy/docker-compose-bridge.yml`

In both modes, the compose stack builds a small local image layer on top of
`alexishw/amneziawg-web-ui:master`. The patch keeps the upstream UI but adds a
default IPv6 ULA pool, `fd42:42:42::/64`, so newly created AWG servers and
clients get both IPv4 and IPv6 tunnel addresses.

In bridge mode, the admin panel is bound to `127.0.0.1:8080`, and the service is
attached to an IPv6-enabled Docker bridge network. This is needed only for
bridge mode; in host mode the container shares the host network namespace, so
Docker's default bridge IPv6 setting is not involved.

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
- New AWG servers and clients created after this deployment are dual-stack.
  Existing IPv4-only servers or clients in the Amnezia Web UI data volume are
  not rewritten automatically; recreate them or migrate their configs manually
  if they need IPv6 addresses.
- In `host` mode the WARP egress rules match WireGuard-style interfaces such as
  `wg-d6c0ef` via the patterns `wg-+` and `awg-+`.
- Avoid broad patterns like `wg+` in host mode, because they also match `wgcf`
  and can create a routing loop.
- In `bridge` mode the WARP egress rules match Docker bridge interfaces via
  `docker0` and `br+`.
- The bridge-mode compose file defines its own IPv6-enabled Docker network
  instead of relying on Docker's IPv4-only default bridge network.
- If your setup uses different interfaces, extend
  `amnezia_extra_forward_iface_patterns`.
- If you prefer to manage `/etc/wireguard/wgcf.conf` yourself, set
  `wgcf_register: false` and place the file on the server before running the
  playbook.

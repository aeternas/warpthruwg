# AGENTS.md

Guidance for AI agents working in this repository.

## Project Overview

This repo contains an Ansible deployment for an Ubuntu VPS that runs the
`wg-easy`/Amnezia web UI compose stack and prepares a Cloudflare WARP `wgcf`
WireGuard interface.

The known-good path is `warpthruwg_mode: host`. Treat host mode as the primary
behavior to preserve unless the user explicitly asks to change it.

## Repository Layout

- `ansible/deploy.yml`: main playbook.
- `ansible/README.md`: operator-facing deployment instructions. Keep this in
  sync with playbook behavior.
- `ansible/group_vars/all.yml.example`: documented variables and safe defaults.
- `ansible/inventory.ini.example`: sample inventory only.
- `ansible/templates/wgcf-firewall-block.j2`: managed `wgcf.conf` block with
  `Table`, `PostUp`, and `PostDown` rules.
- `wg-easy/docker-compose.yml`: host-network compose mode.
- `wg-easy/docker-compose-bridge.yml`: bridge-network compose mode.

## Local Files and Secrets

Do not edit or commit local runtime files unless the user specifically asks:

- `ansible/inventory.ini`
- `ansible/group_vars/all.yml`
- any generated `wgcf-account.toml`, `wgcf-profile.conf`, or private WireGuard
  configuration

Use the `.example` files for documentation and defaults. Assume real inventory
and group vars may contain VPS addresses, SSH users, license keys, or other
private operational settings.

## Behavioral Requirements

- Keep the playbook Ubuntu/`apt` oriented unless a wider OS matrix is requested.
- Preserve installation of `docker.io`, `docker-compose-v2`,
  `wireguard-tools`, `iproute2`, and `iptables`.
- The selected compose file must be copied to
  `/opt/warpthruwg/docker-compose.yml` by default, then started with
  `docker compose up -d`.
- `wgcf` is downloaded as a Linux AMD64 binary and installed at
  `/usr/local/bin/wgcf` by default.
- The systemd service is the standard `wg-quick@wgcf`; do not invent a custom
  unit unless the user asks for one.
- `wgcf.conf` must keep `Table = off` so WARP does not replace the VPS main
  default route.
- IPv4 and IPv6 forwarding rules are both intentional. Keep parity between
  `iptables` and `ip6tables` behavior when changing firewall logic.
- `net.ipv4.conf.all.src_valid_mark=1` is required for fwmark policy routing.

## Compose Mode Notes

- `warpthruwg_mode: host` uses `wg-easy/docker-compose.yml`.
- `warpthruwg_mode: bridge` uses `wg-easy/docker-compose-bridge.yml`.
- In bridge mode the admin panel must remain bound to `127.0.0.1:8080`.
- Host mode intentionally uses narrow forwarding interface patterns such as
  `wg-+` and `awg-+`. Avoid broad patterns like `wg+`, because they can match
  `wgcf` and create a routing loop.
- Bridge mode routes from Docker bridge-style interfaces such as `docker0` and
  `br+`.

## Editing Guidance

- Keep Ansible tasks idempotent where practical.
- Prefer Ansible built-in modules over shell commands. Use
  `ansible.builtin.command` only when a module does not fit, as with `wgcf` and
  `docker compose`.
- If adding variables, define safe defaults in `ansible/deploy.yml`, document
  them in `ansible/group_vars/all.yml.example`, and update
  `ansible/README.md`.
- Be careful editing `ansible/templates/wgcf-firewall-block.j2`: WireGuard
  `PostUp` and `PostDown` are single-line values, and rule order matters.
- If changing firewall rules, preserve cleanup symmetry between `PostUp` and
  `PostDown`.
- Avoid formatting churn in compose files. This repo currently uses simple
  Compose v3.8 YAML with the `amnezia-web-ui` service and the
  `amnezia-data` volume.

## Validation

Run the lightest relevant checks before handing work back:

```bash
cd ansible
ansible-playbook -i inventory.ini.example deploy.yml --syntax-check
```

If Ansible is unavailable locally, say so in the final response. For behavior
that touches a real VPS, do not run the playbook against `inventory.ini` unless
the user explicitly asks.

Useful review commands:

```bash
git diff -- ansible/deploy.yml ansible/README.md ansible/group_vars/all.yml.example wg-easy
rg "warpthruwg_mode|wgcf_|amnezia_" ansible
```

## Documentation Expectations

The README is the operator contract. Whenever playbook behavior changes, update
the README's "What it does", "Compose modes", and "Notes" sections as needed.
Prefer concrete operational notes over broad promises.

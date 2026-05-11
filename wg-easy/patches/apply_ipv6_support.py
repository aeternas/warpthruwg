#!/usr/bin/env python3
from pathlib import Path
import sys


def replace_once(text, old, new):
    if old not in text:
        raise SystemExit(f"patch target not found:\n{old[:240]}")
    return text.replace(old, new, 1)


path = Path(sys.argv[1] if len(sys.argv) > 1 else "/app/web-ui/app.py")
text = path.read_text()

text = replace_once(
    text,
    "DEFAULT_SUBNET = os.getenv('DEFAULT_SUBNET', '10.0.0.0/24')\n",
    "DEFAULT_SUBNET = os.getenv('DEFAULT_SUBNET', '10.0.0.0/24')\n"
    "DEFAULT_IPV6_SUBNET = os.getenv('DEFAULT_IPV6_SUBNET', 'fd42:42:42::/64')\n",
)

text = replace_once(
    text,
    'print(f"DEFAULT_SUBNET: {DEFAULT_SUBNET}")\n',
    'print(f"DEFAULT_SUBNET: {DEFAULT_SUBNET}")\n'
    'print(f"DEFAULT_IPV6_SUBNET: {DEFAULT_IPV6_SUBNET}")\n',
)

text = replace_once(
    text,
    """        # Parse subnet for server IP
        subnet_parts = subnet.split('/')
        network = subnet_parts[0]
        prefix = subnet_parts[1] if len(subnet_parts) > 1 else "24"
        server_ip = self.get_server_ip(network)

        # Create WireGuard server configuration
        server_config_content = f\"\"\"[Interface]
PrivateKey = {server_keys['private_key']}
Address = {server_ip}/{prefix}
ListenPort = {port}
SaveConfig = false
MTU = {mtu}
\"\"\"
""",
    """        # Parse subnets for server IPs
        ipv4_network = ipaddress.ip_network(subnet, strict=False)
        if ipv4_network.version != 4:
            raise ValueError(f"DEFAULT_SUBNET/server subnet must be IPv4, got {subnet}")

        server_ip = str(next(ipv4_network.hosts()))
        prefix = ipv4_network.prefixlen
        ipv6_subnet = server_data.get('ipv6_subnet', DEFAULT_IPV6_SUBNET)
        server_ipv6 = None
        ipv6_prefix = None
        if ipv6_subnet:
            ipv6_network = ipaddress.ip_network(ipv6_subnet, strict=False)
            if ipv6_network.version != 6:
                raise ValueError(f"DEFAULT_IPV6_SUBNET/server IPv6 subnet must be IPv6, got {ipv6_subnet}")
            server_ipv6 = str(next(ipv6_network.hosts()))
            ipv6_prefix = ipv6_network.prefixlen

        server_addresses = f"{server_ip}/{prefix}"
        if server_ipv6:
            server_addresses = f"{server_addresses}, {server_ipv6}/{ipv6_prefix}"

        # Create WireGuard server configuration
        server_config_content = f\"\"\"[Interface]
PrivateKey = {server_keys['private_key']}
Address = {server_addresses}
ListenPort = {port}
SaveConfig = false
MTU = {mtu}
\"\"\"
""",
)

text = replace_once(
    text,
    """            "subnet": subnet,
            "server_ip": server_ip,
""",
    """            "subnet": subnet,
            "server_ip": server_ip,
            "ipv6_subnet": ipv6_subnet,
            "server_ipv6": server_ipv6,
""",
)

text = replace_once(
    text,
    """        print(f"Subnet {subnet_str} is full! No available IPs.")
        return False

    def delete_server(self, server_id):
""",
    """        print(f"Subnet {subnet_str} is full! No available IPs.")
        return False

    def get_new_client_ipv6(self, server_id):
        \"\"\"Get client IPv6 from server IPv6 subnet.\"\"\"
        server = next((s for s in self.config['servers'] if s['id'] == server_id), None)
        if not server or not server.get('ipv6_subnet') or not server.get('server_ipv6'):
            return None

        unbound_ips = server.get("unbound_nat_ipv6s", [])
        if unbound_ips:
            unbound_ip = unbound_ips.pop(0)
            server["unbound_nat_ipv6s"] = unbound_ips
            self.save_config()
            return unbound_ip

        network = ipaddress.ip_network(server['ipv6_subnet'], strict=False)
        used_ips = {server['server_ipv6']}
        for client in server.get('clients', []):
            client_ipv6 = client.get('client_ipv6')
            if client_ipv6:
                used_ips.add(client_ipv6)

        for ip in network.hosts():
            ip_str = str(ip)
            if ip_str not in used_ips:
                return ip_str

        print(f"IPv6 subnet {server['ipv6_subnet']} is full! No available IPs.")
        return None

    def delete_server(self, server_id):
""",
)

text = replace_once(
    text,
    """        # Assign client IP
        client_ip = self.get_new_client_ip(server_id)
        if not client_ip:
            return None

        # Set AllowedIPs only for client config
        server_peer_allowed_ips = f"{client_ip}/32"
""",
    """        # Assign client IPs
        client_ip = self.get_new_client_ip(server_id)
        if not client_ip:
            return None
        client_ipv6 = self.get_new_client_ipv6(server_id)

        # Set AllowedIPs only for server-side peer config
        server_peer_allowed_ips = f"{client_ip}/32"
        if client_ipv6:
            server_peer_allowed_ips = f"{server_peer_allowed_ips}, {client_ipv6}/128"
""",
)

text = replace_once(
    text,
    """            "client_ip": client_ip,
            "obfuscation_enabled": server["obfuscation_enabled"],
""",
    """            "client_ip": client_ip,
            "client_ipv6": client_ipv6,
            "obfuscation_enabled": server["obfuscation_enabled"],
""",
)

text = replace_once(
    text,
    """        server.setdefault("unbound_nat_ips", []).append(client["client_ip"])

        # Rewrite the config file without the deleted client's [Peer] block
""",
    """        server.setdefault("unbound_nat_ips", []).append(client["client_ip"])
        if client.get("client_ipv6"):
            server.setdefault("unbound_nat_ipv6s", []).append(client["client_ipv6"])

        # Rewrite the config file without the deleted client's [Peer] block
""",
)

text = replace_once(
    text,
    """        config += f\"\"\"[Interface]
PrivateKey = {client_config['client_private_key']}
Address = {client_config['client_ip']}/32
DNS = {', '.join(server['dns'])}
MTU = {server['mtu']}
\"\"\"
""",
    """        client_addresses = f"{client_config['client_ip']}/32"
        if client_config.get('client_ipv6'):
            client_addresses = f"{client_addresses}, {client_config['client_ipv6']}/128"

        config += f\"\"\"[Interface]
PrivateKey = {client_config['client_private_key']}
Address = {client_addresses}
DNS = {', '.join(server['dns'])}
MTU = {server['mtu']}
\"\"\"
""",
)

text = replace_once(
    text,
    """            "default_subnet": DEFAULT_SUBNET,
            "default_port": DEFAULT_PORT,
""",
    """            "default_subnet": DEFAULT_SUBNET,
            "default_ipv6_subnet": DEFAULT_IPV6_SUBNET,
            "default_port": DEFAULT_PORT,
""",
)

text = replace_once(
    text,
    """        "server_ip": server['server_ip'],
        "subnet": server['subnet'],
""",
    """        "server_ip": server['server_ip'],
        "server_ipv6": server.get('server_ipv6'),
        "subnet": server['subnet'],
        "ipv6_subnet": server.get('ipv6_subnet'),
""",
)

text = replace_once(
    text,
    '    print(f"  Default Subnet: {DEFAULT_SUBNET}")\n',
    '    print(f"  Default Subnet: {DEFAULT_SUBNET}")\n'
    '    print(f"  Default IPv6 Subnet: {DEFAULT_IPV6_SUBNET}")\n',
)

path.write_text(text)

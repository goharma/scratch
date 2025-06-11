import argparse
import os
import yaml
from jinja2 import Environment, FileSystemLoader

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def load_yaml(path):
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError:
            print(f"Warning: {path} is not standard YAML. Starting with empty inventory.")
            return {}
    return {}

from collections import OrderedDict

def save_yaml(data, path):
    # Sort domain keys (exclude 'integ' and 'global'), then append 'integ' and 'global'
    domain_keys = sorted([k for k in data if k not in ('integ', 'global')])
    keys = domain_keys + [k for k in ('integ', 'global') if k in data]
    ordered = {k: data[k] for k in keys}
    with open(path, "w") as f:
        yaml.dump(ordered, f, default_flow_style=False, sort_keys=False)

def render_template(template_path, context, output_path):
    env = Environment(loader=FileSystemLoader(os.path.dirname(template_path)))
    template = env.get_template(os.path.basename(template_path))
    with open(output_path, "w") as f:
        f.write(template.render(context))

def update_inventory(inventory, domain, hosts, env):
    # Add/Update domain group with hosts
    inventory.setdefault(domain, {})
    inventory[domain].setdefault("hosts", {})
    for host in hosts:
        inventory[domain]["hosts"][host] = None

    # Add/Update 'integ' group with children
    inventory.setdefault("integ", {})
    inventory["integ"].setdefault("children", {})
    inventory["integ"]["children"][domain] = {}

    # Add/Update 'global' group with children
    inventory.setdefault("global", {})
    inventory["global"].setdefault("children", {})
    inventory["global"]["children"][env] = {}

    return inventory

def main():
    parser = argparse.ArgumentParser(description="Create or update Ansible inventory structure.")
    parser.add_argument("--env", required=True, help="Environment name (e.g., integ, sandbox)")
    parser.add_argument("--domain", required=True, help="Domain name (e.g., pesaWeb, portfolioWeb)")
    parser.add_argument("--admin_host", required=True, help="Admin host for group_vars")
    parser.add_argument("--admin_port", required=True, type=int, help="Admin port for group_vars")
    parser.add_argument("--ms_prefix", required=False, default="m", help="Managed server prefix (default: m)")
    parser.add_argument("--host_prefix", required=False, default="nldaweb", help="Optional host prefix to prepend to each host")
    parser.add_argument("--host_suffix", required=False, default="", help="Optional host suffix to append to each host")
    parser.add_argument("--host_numbers", required=True, help="Comma-separated host numbers (e.g., 1,2)")
    parser.add_argument("--host_domain", required=True, help="Host domain string (e.g., domain1)")
    parser.add_argument("--inventory_root", default="inventory", help="Root inventory directory")
    parser.add_argument("--template_dir", default="_templates", help="Directory containing Jinja2 templates")
    parser.add_argument("--force", action="store_true", help="Force overwrite if domain already exists")
    args = parser.parse_args()

    env_dir = os.path.join(args.inventory_root, args.env)
    inventory_yaml_path = os.path.join(env_dir, "inventory.yaml")
    group_vars_dir = os.path.join(env_dir, "group_vars", args.domain)
    host_vars_dir = os.path.join(env_dir, "host_vars")
    domain = args.domain.strip()

    # Ensure directories exist
    ensure_dir(args.inventory_root)
    ensure_dir(env_dir)
    ensure_dir(group_vars_dir)
    ensure_dir(host_vars_dir)

    # Prepare hosts list using all combinations of prefix and number
    prefix = args.ms_prefix.strip()
    host_prefix = args.host_prefix.strip()
    host_suffix = args.host_suffix.strip()
    numbers = [n.strip() for n in args.host_numbers.split(",") if n.strip()]
    host_domain = args.host_domain.strip()
    managed_server_list = [f"{host_prefix}{prefix}{number}{domain}{host_suffix}" for number in numbers]

    # Load or initialize inventory
    inventory = load_yaml(inventory_yaml_path)

    # Check if domain already exists
    if args.domain in inventory and not args.force:
        print(f"Error: Domain '{args.domain}' already exists in the inventory. Use --force to overwrite.")
        return

    # Update inventory structure
    inventory = update_inventory(inventory, args.domain, managed_server_list, args.env)

    # Save updated inventory
    save_yaml(inventory, inventory_yaml_path)

    # Render group_vars
    group_vars_context = {
        "env": args.env,
        "domain": args.domain,
        "admin_port": args.admin_port,
        "admin_host": args.admin_host,
        "ms_prefix": prefix,
        "host_prefix": host_prefix,
        "host_suffix": host_suffix,
        "host_numbers": numbers,
        "host_domain": host_domain,
        "managed_server_list": managed_server_list
    }
    group_vars_template = os.path.join(args.template_dir, "group_vars.j2")
    group_vars_output = os.path.join(group_vars_dir, "vars.yaml")
    render_template(group_vars_template, group_vars_context, group_vars_output)

    # Render host_vars for each host
    host_vars_template = os.path.join(args.template_dir, "host_vars.j2")
    print(managed_server_list)
    for idx, number in enumerate(numbers):
        host = managed_server_list[idx]
        print(f"{host_prefix}-{number}{host_suffix}.{host_domain}") # nldaweb-41f.devjones.com
        fqdn = f"{host_prefix}-{number}{host_suffix}.{host_domain}"
        host_vars_context = {
            "current_host_name": host,
            "fqdn": fqdn,
            "host_suffix": host_suffix
        }
        # Host var filename: ms_prefix + host_number + domain + .yaml
        host_var_filename = f"{prefix}{number}{domain}.yaml"
        host_vars_output = os.path.join(host_vars_dir, host_var_filename)
        render_template(host_vars_template, host_vars_context, host_vars_output)

    print(f"Inventory updated at {inventory_yaml_path}")
    print(f"Group vars written to {group_vars_output}")
    print(f"Host vars written to {host_vars_dir}")

if __name__ == "__main__":
    '''
    Usage: python create_or_update_inventory.py --env=integ --domain=portfolioWeb --admin_port=44433 --admin_host=admin_host_name --ms_prefix='m' --host_numbers='41,42' --host_domain='devjones.com' --force --host_suffix f 
    '''
    main()


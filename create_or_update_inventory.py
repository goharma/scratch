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
    inventory["global"]["children"]["integ"] = {}

    return inventory

def main():
    parser = argparse.ArgumentParser(description="Create or update Ansible inventory structure.")
    parser.add_argument("--env", required=True, help="Environment name (e.g., integ, sandbox)")
    parser.add_argument("--domain", required=True, help="Domain name (e.g., domain1)")
    parser.add_argument("--port", required=True, type=int, help="Port for group_vars")
    parser.add_argument("--admin_host", required=True, help="Admin host for group_vars")
    parser.add_argument("--host_prefizes", required=True, help="Comma-separated host prefixes (e.g., m41,m42)")
    parser.add_argument("--inventory_root", default="inventory", help="Root inventory directory")
    parser.add_argument("--template_dir", default="_templates", help="Directory containing Jinja2 templates")
    args = parser.parse_args()

    env_dir = os.path.join(args.inventory_root, args.env)
    inventory_yaml_path = os.path.join(env_dir, "inventory.yaml")
    group_vars_dir = os.path.join(env_dir, "group_vars", args.domain)
    host_vars_dir = os.path.join(env_dir, "host_vars")

    # Ensure directories exist
    ensure_dir(args.inventory_root)
    ensure_dir(env_dir)
    ensure_dir(group_vars_dir)
    ensure_dir(host_vars_dir)

    # Prepare hosts list
    hosts_list = [f"{prefix.strip()}{args.domain}" for prefix in args.host_prefizes.split(",") if prefix.strip()]

    # Load or initialize inventory
    inventory = load_yaml(inventory_yaml_path)

    # Check if domain already exists
    if args.domain in inventory:
        print(f"Error: Domain '{args.domain}' already exists in the inventory. No changes made.")
        return

    # Update inventory structure
    inventory = update_inventory(inventory, args.domain, hosts_list, args.env)

    # Save updated inventory
    save_yaml(inventory, inventory_yaml_path)

    # Render group_vars
    group_vars_context = {
        "env": args.env,
        "domain": args.domain,
        "port": args.port,
        "admin_host": args.admin_host,
        "host_prefizes": hosts_list
    }
    group_vars_template = os.path.join(args.template_dir, "group_vars.j2")
    group_vars_output = os.path.join(group_vars_dir, "vars.yaml")
    render_template(group_vars_template, group_vars_context, group_vars_output)

    # Render host_vars for each host
    host_vars_template = os.path.join(args.template_dir, "host_vars.j2")
    for host in hosts_list:
        host_vars_context = {"current_host_name": host}
        host_vars_output = os.path.join(host_vars_dir, f"{host}.yaml")
        render_template(host_vars_template, host_vars_context, host_vars_output)

    print(f"Inventory updated at {inventory_yaml_path}")
    print(f"Group vars written to {group_vars_output}")
    print(f"Host vars written to {host_vars_dir}")

if __name__ == "__main__":
    main()

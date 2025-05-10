import xml.etree.ElementTree as ET
import sys 


# Parse the XML file
tree = ET.parse(sys.argv[1])  # Replace with your actual file path
root = tree.getroot()

# Define the namespace mapping
ns = {
    'wl': 'http://xmlns.oracle.com/weblogic/domain'
}

# Find all <jms-system-resource> elements
for jms_resource in root.findall('wl:jms-system-resource', ns):
    name = jms_resource.find('wl:name', ns)
    target = jms_resource.find('wl:target', ns)
    
    if name is not None and target is not None:
        print(f"Name: {name.text}")
        print(f"Target: {target.text}")


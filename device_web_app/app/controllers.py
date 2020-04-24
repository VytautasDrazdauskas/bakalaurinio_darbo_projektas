import subprocess

def save_config(mesh_id, password, mesh_fwding):
    mesh_cmd = "wireless.@wifi-iface[0].mesh_id=" + mesh_id
    key_cmd = "wireless.@wifi-iface[0].key=" + password

    if (mesh_fwding == None):
        mesh_fwding = '0'
    fwding_cmd = "wireless.@wifi-iface[0].mesh_fwding=" + mesh_fwding

    subprocess.call(["uci", "set", mesh_cmd])
    subprocess.call(["uci", "set", key_cmd])
    subprocess.call(["uci", "set", fwding_cmd])
    subprocess.call(["uci", "commit", "wireless"])
    return 1

#konfiguraciju uzkrovimas
def load_mesh_fwding():
    mesh_fwding = subprocess.check_output(["uci", "get", "wireless.@wifi-iface[0].mesh_fwding"])

    return mesh_fwding

def load_mesh_id():
    mesh_id = subprocess.check_output(["uci", "get", "wireless.@wifi-iface[0].mesh_id"])

    return mesh_id

def load_key():
    password = subprocess.check_output(["uci", "get", "wireless.@wifi-iface[0].key"])

    return password

def reboot_wifi():
    subprocess.call(["wifi"])

    return 1
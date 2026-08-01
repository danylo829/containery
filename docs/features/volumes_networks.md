# Volumes & Networks Management

Inspect and manage persistent Docker storage volumes and network configurations across connected hosts.

---

## 1. Volume Management

Docker volumes provide persistent storage outside container filesystems.

### Viewing Volume List

* **Navigation**: **Volumes** (Sidebar: **Volumes**).
* **Attributes**: Lists Volume Name, Storage Mountpoint path on the host system, and Host ID.
* **Search & Pagination**: Filter volumes by name or host mountpoint path.

### Inspecting Volume Details

* **Navigation**: **Volumes** > **Click Volume Name**.
* **Detailed Info**: View Driver (e.g. `local`), Scope (`local` / `global`), Host Mountpoint, Creation date, Driver Options, and Labels.

### Deleting Volumes

* **Navigation**: **Volumes** > **Click Delete icon** next to a volume.
* **Action**: Permanently deletes the volume and all data stored within it from the host filesystem.

---

## 2. Network Management

Docker networks connect containers with each other and isolate external network traffic.

### Viewing Network List

* **Navigation**: **Networks** (Sidebar: **Networks**).
* **Attributes**: Lists Network Name, Network ID, Driver (`bridge`, `host`, `overlay`, `null`), Subnet, Gateway, and Host ID.
* **Search & Pagination**: Filter networks by network name, driver type, subnet CIDR, or gateway IP.

### Inspecting Network Details

* **Navigation**: **Networks** > **Click Network Name**.
* **Detailed Info**:
  * **General Info**: Network ID, Driver, Scope, Creation date.
  * **Configuration Flags**: IPv6 Enabled, Internal Network, Attachable, Ingress.
  * **IPAM Configuration**: Assigned Subnets (e.g. `172.18.0.0/16`) and Default Gateways (e.g. `172.18.0.1`).
  * **Attached Containers**: View all containers connected to this network alongside their assigned IP addresses and MAC addresses.
  * **Labels**: Network metadata labels.

### Deleting Networks

* **Navigation**: **Networks** > **Click Delete icon** next to a network.
* **Action**: Removes the specified Docker network.

!!! note
    Networks with active connected containers cannot be deleted until those containers are disconnected or stopped.

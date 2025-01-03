from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl
import json

def get_esxi_cpu_info(vcenter_host, vcenter_user, vcenter_password, esxi_host):
    # Bỏ qua xác minh chứng chỉ SSL
    context = ssl._create_unverified_context()

    # Kết nối tới vCenter
    si = SmartConnect(host=vcenter_host, user=vcenter_user, pwd=vcenter_password, sslContext=context)
    content = si.RetrieveContent()

    # Duyệt qua các host để tìm ESXi host cụ thể
    result = {}
    for datacenter in content.rootFolder.childEntity:
        for cluster in datacenter.hostFolder.childEntity:
            for host in cluster.host:
                if host.name == esxi_host:
                    summary = host.summary
                    result = {
                        "esxi_host": host.name,
#                        "cpu_model": summary.hardware.cpuModel,
#                        "cpu_total_cores": summary.hardware.numCpuCores,
#                        "cpu_threads": summary.hardware.numCpuThreads,
#                        "cpu_usage_mhz": summary.quickStats.overallCpuUsage,
#                        "cpu_total_mhz": summary.hardware.cpuMhz * summary.hardware.numCpuCores,
                        "cpu_usage": (summary.quickStats.overallCpuUsage / (summary.hardware.cpuMhz * summary.hardware.numCpuCores))*100,
#                        "memory_usage": summary.quickStats.overallMemoryUsage * 1024 * 1024,
#                        "memory_total": host.hardware.memorySize,
                        "memory_usage": ((summary.quickStats.overallMemoryUsage * 1024 * 1024) / host.hardware.memorySize)*100
                    }
    Disconnect(si)
    return result

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--vcenter_host", required=True, help="vCenter server hostname or IP")
    parser.add_argument("--vcenter_user", required=True, help="vCenter username")
    parser.add_argument("--vcenter_password", required=True, help="vCenter password")
    parser.add_argument("--esxi_host", required=True, help="ESXi hostname")

    args = parser.parse_args()

    data = get_esxi_cpu_info(args.vcenter_host, args.vcenter_user, args.vcenter_password, args.esxi_host)
    print(json.dumps(data, indent=4))

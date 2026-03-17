import pyopencl as cl


def print_device_info():
    # Iterate through all available OpenCL platforms
    for platform in cl.get_platforms():
        print(f"Platform Name: {platform.name}")
        print(f"Platform Vendor: {platform.vendor}")
        print(f"Platform Version: {platform.version}")

        # Iterate through all devices on this platform
        for device in platform.get_devices():
            print("\t-------------------------")
            print(f"\tDevice Name: {device.name}")
            print(f"\tDevice Type: {cl.device_type.to_string(device.type)}")
            print(f"\tDevice Vendor: {device.vendor}")
            print(f"\tDevice Version: {device.opencl_c_version}")
            print(f"\tDriver Version: {device.driver_version}")
            print(f"\tCompute Units: {device.max_compute_units}")
            print(f"\tLocal Memory: {device.local_mem_size / 1024:.0f} KB")
            print(f"\tGlobal Memory: {device.global_mem_size / (1024**3):.2f} GB")
            print(f"\tMax Work Item Dimensions:   {device.max_work_item_dimensions}")
            print(f"\tMax Work Item Sizes (dims): {device.max_work_item_sizes}")
            print(f"\tMax Work Group Total Size:  {device.max_work_group_size}")
        print("\n")


if __name__ == "__main__":
    print_device_info()

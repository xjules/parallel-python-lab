import numpy as np
import pyopencl as cl

kernel_code = """
__kernel void test_mem(
    __global float *g_data,   // From d_global
    __constant float *c_val,  // From d_constant
    __local float *l_temp     // From cl.LocalMemory(16)
) {
    int gid = get_global_id(0);

    l_temp[gid] = g_data[gid] + c_val[0];
    
    // Ensure all threads in the group finished writing to local memory
    barrier(CLK_LOCAL_MEM_FENCE);

    // Write back to global to see the result in Python
    g_data[gid] = l_temp[gid];
}
"""
# Setup
ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx)
mf = cl.mem_flags

# Data to send
h_data = np.array([1, 2, 3, 4], dtype=np.float32)
h_const = np.array([10], dtype=np.float32)

# 1. Global: Standard Read/Write buffer
d_global = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=h_data)

# 2. Constant: Optimized Read-Only buffer
d_constant = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=h_const)

# 3. shared mem: No data sent, only the size (4 floats * 4 bytes = 16 bytes)
d_local = cl.LocalMemory(16)

# Execute Kernel
prg = cl.Program(ctx, kernel_code).build()
prg.test_mem(queue, h_data.shape, None, d_global, d_constant, d_local)

# Read back results
cl.enqueue_copy(queue, h_data, d_global)
print("Result after kernel execution:", h_data)

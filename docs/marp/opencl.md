---
marp: true
theme: dracula
class: invert
paginate: true
size: 16:9
---
# Why Learn OpenCL?

GPU programming enables **massive parallelism**.

- Data‑parallel computation
- Thousands of concurrent threads
- SIMT execution model

Examples of GPU frameworks:

- CUDA
- OpenCL
- GLSL / HLSL shaders

OpenCL allows a **host application** to control multiple compute devices.

---

# OpenCL Devices

OpenCL can execute on:

- GPU
- CPU
- FPGA
- DSP

Device structure:

Device  
→ Compute Units
→ Processing Elements

Processing elements execute instructions using:

- SIMD
- SPMD

---

# Historical Context

Important milestones:

- 1992 — OpenGL standard
- 2007 — CUDA introduced
- 2008 — OpenCL 1.0 released
- 2013 — OpenCL 2.0 (Shared Virtual Memory)
- 2017 — OpenCL 2.2 (workgroup functions)
- 2020 — OpenCL 3.0

---

# Why OpenCL?

Advantages:

- Portable parallel code
- Works across hardware vendors
- Access to GPU acceleration
- Massive performance gains for heavy computation

Typical domains:

- Scientific computing
- Simulation
- Signal processing
- Rendering

---

# Example Application Domains

OpenCL is commonly used for:

- Particle simulations
- Molecular dynamics
- Matrix multiplication
- FFT
- Database search
- Volume rendering

---

# OpenCL Programming Model

OpenCL programs consist of:

### Setup

- Devices
- Contexts
- Command Queues

### Memory

- Buffers
- Images

### Execution

- Programs
- Kernels

### Synchronization

- Events
- Pipes

---

# Kernels

A **kernel** is a C‑like function executed on the device.

Thousands of threads execute the same kernel.

Example:

```c
kernel void dp_mul(global const float *a,
                   global const float *b,
                   global float *result)
{
    int id = get_global_id(0);
    result[id] = a[id] * b[id];
}
```

Each work‑item processes **one element**.

---

# CPU vs GPU Thinking

CPU version:

```c
for(int i=0;i<n;i++)
    result[i] = a[i] * b[i];
```

GPU version:

Each thread computes one element simultaneously.

---

# Work‑Items

Kernel execution creates many **work‑items**.

Each work‑item has identifiers:

```
get_global_id()
get_local_id()
get_group_id()
```

Example:

```
globalID = groupSize * groupID + localID
```

---

# Work‑Groups

Work‑items are grouped into **work‑groups**.

Structure:

NDRange  
→ Work‑groups  
→ Work‑items

Work‑items inside a group:

- can synchronize
- share local memory

Work‑groups are **independent**.

---

# Global vs Local Dimensions

Two dimensions define execution:

Global size
- total number of threads

Local size
- threads per work‑group

Example:

Global: 1024 × 1024  
Local: 128 × 128

---

# Memory Model

OpenCL memory hierarchy:

Private memory
- per work‑item

Local memory
- shared within work‑group

Global memory
- accessible by all work‑items

Constant memory
- read‑only global data

---

# Memory Transfer

Important constraint:

Data must move between:

Host (CPU)
↔
Device (GPU)

Transfers are expensive.

Performance depends heavily on **memory layout and transfers**.

---

# Address Space Qualifiers

OpenCL uses explicit memory qualifiers.

```
__global
__local
__constant
__private
```

Example kernel:

```c
__kernel void vadd(__global const float *a,
                   __global const float *b,
                   __global float *result)
{
    int id = get_global_id(0);
    result[id] = a[id] + b[id];
}
```

---

# Synchronization

Within a work‑group:

```
barrier(CLK_LOCAL_MEM_FENCE);
```

This synchronizes threads in the same group.

Important limitation:

No synchronization between **different work‑groups**.

---

# Atomic Operations

Atomic operations prevent race conditions.

Examples:

```
atomic_add
atomic_sub
atomic_inc
atomic_dec
atomic_min
atomic_max
```

Example:

```c
uint old_val = atomic_inc(counter);
```

---

# Reduction Pattern

Many GPU algorithms use **reductions**.

Example:

Sum of array values.

Strategy:

1. Load values into local memory
2. Perform partial reductions
3. Write result per work‑group

---

# Example Reduction Kernel

```c
__kernel void Sum(global int *X,
                  local int *sdata,
                  global int *Y)
{
    int tid = get_local_id(0);
    int i = get_global_id(0);

    sdata[tid] = X[i];
    barrier(CLK_LOCAL_MEM_FENCE);

    for(int s = get_local_size(0)/2; s > 0; s >>= 1)
    {
        if(tid < s)
            sdata[tid] += sdata[tid+s];

        barrier(CLK_LOCAL_MEM_FENCE);
    }

    if(tid == 0)
        Y[get_group_id(0)] = sdata[0];
}
```

---

# Monte Carlo Methods

Monte Carlo integration uses random sampling.

Typical GPU workflow:

1. Generate random samples
2. Evaluate function in parallel
3. Aggregate results

Note:

OpenCL does **not provide built‑in RNG**.

Options:

- Precompute random numbers
- Implement custom RNG

---

# Fractal Example

Example GPU workload:

Mandelbrot set.

Equation:

```
z(n+1) = z(n)^2 + c
```

Each pixel can be computed **independently**, making it ideal for GPUs.

---

# Particle Simulation

Particle systems are another good GPU target.

Each particle has:

- position
- velocity
- weight

Update rule:

```
v(i+1) = v(i) + f(...)
p(i+1) = p(i) + v(i+1)
```

Thousands of particles can update in parallel.

---

# PyOpenCL

PyOpenCL provides a Python interface for OpenCL.

Advantages:

- Python host code
- GPU kernels in OpenCL C
- Easy memory management

Important features:

- asynchronous execution
- event objects
- non‑blocking kernel launches

---

# Async Execution

Commands are queued on the device.

Queue operations return **events**.

Events allow:

```
event.wait()
pyopencl.wait_for_events(events)
```

This enables asynchronous GPU pipelines.

---

# Key Takeaways

OpenCL provides:

- portable GPU programming
- massive parallelism
- device‑agnostic compute acceleration

PyOpenCL allows Python applications to:

- launch kernels
- manage GPU memory
- run asynchronous compute pipelines

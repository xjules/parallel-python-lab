import time

import matplotlib.pyplot as plt
import numpy as np
import pyopencl as cl

KERNEL = r"""
__kernel void game_of_life(
    __global const uchar *src,
    __global uchar *dst,
    const int width,
    const int height)
{
    int x = get_global_id(0);
    int y = get_global_id(1);

    if (x >= width || y >= height) return;

    int idx = y * width + x;
    int alive = 0;

    for (int dy = -1; dy <= 1; dy++) {
        for (int dx = -1; dx <= 1; dx++) {
            if (dx == 0 && dy == 0) continue;

            int nx = (x + dx + width) % width;
            int ny = (y + dy + height) % height;
            alive += src[ny * width + nx];
        }
    }

    uchar cell = src[idx];

    if (cell) {
        dst[idx] = (alive == 2 || alive == 3) ? 1 : 0;
    } else {
        dst[idx] = (alive == 3) ? 1 : 0;
    }
}
"""


def main():
    width, height = 256, 256
    steps = 500

    # random initial grid
    grid = (np.random.rand(height, width) > 0.8).astype(np.uint8)

    # OpenCL setup
    ctx = cl.create_some_context()
    queue = cl.CommandQueue(ctx)
    program = cl.Program(ctx, KERNEL).build()

    mf = cl.mem_flags
    src_buf = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=grid)
    dst_buf = cl.Buffer(ctx, mf.READ_WRITE, grid.nbytes)

    # matplotlib setup
    plt.ion()
    fig, ax = plt.subplots()
    im = ax.imshow(grid, cmap="binary", interpolation="nearest")
    ax.set_title("Game of Life (PyOpenCL)")
    ax.set_axis_off()

    for _ in range(steps):
        program.game_of_life(
            queue,
            (width, height),
            None,
            src_buf,
            dst_buf,
            np.int32(width),
            np.int32(height),
        )

        cl.enqueue_copy(queue, grid, dst_buf).wait()
        src_buf, dst_buf = dst_buf, src_buf

        im.set_data(grid)
        plt.pause(0.01)

    plt.ioff()
    plt.show()


if __name__ == "__main__":
    main()

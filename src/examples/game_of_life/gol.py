# gol_pyopencl_pygame.py
# Game of Life on GPU (PyOpenCL) + pygame visualization — all in one file.
#
# Install:
#   pip install numpy pyopencl pygame
#
# Run:
#   python gol_pyopencl_pygame.py
#
# Controls:
#   SPACE  pause/resume
#   R      randomize
#   C      clear
#   N      single-step (when paused)
#   UP/DOWN  speed up / slow down
#   ESC / close window  quit

from __future__ import annotations

import sys
import time

import numpy as np
import pygame
import pyopencl as cl

KERNEL_SRC = r"""
__kernel void gol_step(
    __global const uchar* src,
    __global uchar* dst,
    const int W,
    const int H
){
    int x = (int)get_global_id(0);
    int y = (int)get_global_id(1);
    if (x >= W || y >= H) return;

    int idx = y * W + x;

    // wrap-around (toroidal) boundaries
    int xm1 = (x + W - 1) % W;
    int xp1 = (x + 1) % W;
    int ym1 = (y + H - 1) % H;
    int yp1 = (y + 1) % H;

    int n =
        src[ym1 * W + xm1] + src[ym1 * W + x] + src[ym1 * W + xp1] +
        src[y   * W + xm1]                     + src[y   * W + xp1] +
        src[yp1 * W + xm1] + src[yp1 * W + x] + src[yp1 * W + xp1];

    uchar alive = src[idx];
    // Conway rules:
    // alive stays alive if 2 or 3 neighbors; dead becomes alive if exactly 3.
    uchar out = (alive && (n == 2 || n == 3)) || (!alive && (n == 3));
    dst[idx] = out;
}
"""


def make_surface_from_grid(grid_2d_u8: np.ndarray, cell: int) -> pygame.Surface:
    """
    Convert (H,W) uint8 grid of {0,1} to a pygame Surface, scaled by `cell`.
    Fast-ish path: build an RGB array where alive cells are white.
    """
    # grid -> 0 or 255
    img = (grid_2d_u8 * 255).astype(np.uint8)

    # Make 3-channel (H,W,3)
    rgb = np.stack([img, img, img], axis=-1)  # alive=white, dead=black

    # pygame expects (W,H,3) when using surfarray.make_surface
    surf = pygame.surfarray.make_surface(np.transpose(rgb, (1, 0, 2)))

    if cell != 1:
        surf = pygame.transform.scale(
            surf, (grid_2d_u8.shape[1] * cell, grid_2d_u8.shape[0] * cell)
        )
    return surf


def main() -> int:
    # ---- Config (keep it simple) ----
    W, H = 256, 256  # try 512x512 if you have a decent GPU
    CELL = 3  # pixel size per cell in window
    TARGET_FPS = 60
    STEPS_PER_FRAME = (
        1  # increase for faster evolution without increasing transfer rate
    )

    # Host grid
    host = (np.random.rand(H, W) > 0.85).astype(np.uint8)
    host_flat = host.ravel()

    # ---- OpenCL setup ----
    try:
        dev = cl.device_type.GPU
        ctx = cl.Context(devices=[dev])
        queue = cl.CommandQueue(ctx)
    except Exception as e:
        print(f"[OpenCL] {e}", file=sys.stderr)
        return 1

    prg = cl.Program(ctx, KERNEL_SRC).build()

    mf = cl.mem_flags
    # Double buffer on device
    buf_a = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=host_flat)
    buf_b = cl.Buffer(ctx, mf.READ_WRITE, size=host_flat.nbytes)

    # ---- Pygame setup ----
    pygame.init()
    screen = pygame.display.set_mode((W * CELL, H * CELL))
    pygame.display.set_caption("Game of Life (PyOpenCL + pygame)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 20)

    paused = False
    step_once = False
    speed = STEPS_PER_FRAME

    last_info = ""
    last_info_t = 0.0

    def show_info(msg: str) -> None:
        nonlocal last_info, last_info_t
        last_info = msg
        last_info_t = time.time()

    show_info("SPACE pause/resume | R randomize | C clear | N step | UP/DOWN speed")

    # Pre-allocate a host buffer for device->host copies
    out_flat = np.empty(W * H, dtype=np.uint8)

    running = True
    while running:
        # ---- Handle events ----
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                elif ev.key == pygame.K_SPACE:
                    paused = not paused
                    show_info("Paused" if paused else "Running")
                elif ev.key == pygame.K_r:
                    host = (np.random.rand(H, W) > 0.85).astype(np.uint8)
                    host_flat = host.ravel()
                    cl.enqueue_copy(queue, buf_a, host_flat)  # reset src buffer
                    show_info("Randomized")
                elif ev.key == pygame.K_c:
                    host.fill(0)
                    host_flat = host.ravel()
                    cl.enqueue_copy(queue, buf_a, host_flat)
                    show_info("Cleared")
                elif ev.key == pygame.K_n:
                    # single step when paused
                    if paused:
                        step_once = True
                        show_info("Step")
                elif ev.key == pygame.K_UP:
                    speed = min(50, speed + 1)
                    show_info(f"Steps/frame: {speed}")
                elif ev.key == pygame.K_DOWN:
                    speed = max(1, speed - 1)
                    show_info(f"Steps/frame: {speed}")

        # ---- Compute next state on GPU ----
        if (not paused) or step_once:
            # do `speed` steps per frame (on GPU, no host transfer between them)
            for _ in range(speed):
                prg.gol_step(
                    queue, (W, H), None, buf_a, buf_b, np.int32(W), np.int32(H)
                )
                buf_a, buf_b = buf_b, buf_a
            step_once = False

        # ---- Copy to host for display (this is the expensive part) ----
        cl.enqueue_copy(queue, out_flat, buf_a)
        queue.finish()

        # reshape to 2D and render
        grid2d = out_flat.reshape(H, W)
        surf = make_surface_from_grid(grid2d, CELL)

        screen.blit(surf, (0, 0))

        # overlay FPS + status
        fps = clock.get_fps()
        overlay = (
            f"{'PAUSED' if paused else 'RUN'} | FPS {fps:5.1f} | steps/frame {speed}"
        )
        txt = font.render(overlay, True, (0, 255, 0))
        screen.blit(txt, (8, 8))

        # transient help/info line
        if last_info and (time.time() - last_info_t) < 2.0:
            txt2 = font.render(last_info, True, (0, 255, 0))
            screen.blit(txt2, (8, 28))

        pygame.display.flip()
        clock.tick(TARGET_FPS)

    pygame.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

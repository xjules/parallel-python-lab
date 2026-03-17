import matplotlib.pyplot as plt
import numpy as np
import pyopencl as cl
from PIL import Image

KERNEL_CODE = """
const sampler_t sampler = CLK_NORMALIZED_COORDS_FALSE |
                          CLK_ADDRESS_CLAMP_TO_EDGE |
                          CLK_FILTER_NEAREST;

__kernel void invert_grayscale(__read_only image2d_t src,
                               __write_only image2d_t dest) {
    int2 coord = (int2)(get_global_id(0), get_global_id(1));
    float4 pixel = read_imagef(src, sampler, coord);

    float gray = 0.299f * pixel.x + 0.587f * pixel.y + 0.114f * pixel.z;
    float inverted = 1.0f - gray;

    write_imagef(dest, coord, (float4)(inverted, 0.0f, 0.0f, 1.0f));
}
"""


def run_image_kernel():
    img = Image.open("lena_color.png")
    img_np = np.array(img).astype(np.float32) / 255.0

    h, w = img_np.shape[:2]
    img_rgba = np.ones((h, w, 4), dtype=np.float32)
    img_rgba[:, :, :3] = img_np

    ctx = cl.create_some_context()
    queue = cl.CommandQueue(ctx)

    rgba_fmt = cl.ImageFormat(cl.channel_order.RGBA, cl.channel_type.FLOAT)
    r_fmt = cl.ImageFormat(cl.channel_order.R, cl.channel_type.FLOAT)

    src_img = cl.Image(
        ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR,
        rgba_fmt, shape=(w, h), hostbuf=img_rgba,
    )
    dest_img = cl.Image(ctx, cl.mem_flags.WRITE_ONLY, r_fmt, shape=(w, h))

    prg = cl.Program(ctx, KERNEL_CODE).build()
    prg.invert_grayscale(queue, (w, h), None, src_img, dest_img)

    result = np.empty((h, w, 1), dtype=np.float32)
    cl.enqueue_copy(queue, result, dest_img, origin=(0, 0), region=(w, h))

    fig, (ax1, ax2) = plt.subplots(1, 2)
    ax1.imshow(img_np)
    ax1.set_title("Original")
    ax1.axis("off")
    ax2.imshow(result[:, :, 0], cmap="gray")
    ax2.set_title("Inverted Grayscale")
    ax2.axis("off")
    plt.show()


if __name__ == "__main__":
    run_image_kernel()

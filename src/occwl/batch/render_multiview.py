import argparse
import math
import pathlib
import signal
from itertools import repeat
from multiprocessing import Pool
from occwl.compound import Compound
from occwl.viewer import OffscreenRenderer
from OCC.Core.gp import gp_Dir, gp_Vec
from OCC.Core.V3d import V3d_DirectionalLight
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB, Quantity_NOC_WHITE
from tqdm import tqdm


def render(shape, filename, width=1024, height=768, euler_angles_radians=(0, 0, 0)):
    viewer = OffscreenRenderer(background_top_color=[255, 255, 255], background_bottom_color=[255, 255, 255],
                               axes=False, size=(width, height))
    # Add a directional light so that the shading isn't too flat. The default light seems to be pointing backwards
    viewer.add_directional_light((0, 0.5, -1), color=(255, 255, 255))
    if euler_angles_radians != (0, 0, 0):
        shape.rotate_euler_angles(euler_angles_radians)
    viewer.display(shape)
    viewer.fit()
    viewer.save_image(filename)


def process_one_file_multi_view(fn_args):
    fn, args = fn_args
    output_path = pathlib.Path(args.output_dir)
    exists = True
    if not args.overwrite:
        for i in range(args.num_images):
            exists &= output_path.joinpath(fn.stem + f"_{i}.png").exists()
        if exists:
            return
    try:
        shape = Compound.load_from_step(str(fn))
        delta_angle = (2 * math.pi) / args.num_images
        for i in range(args.num_images):
            render(shape, output_path.joinpath(fn.stem + f"_{i}.png"), args.width, args.height,
                   euler_angles_radians=(0, 0, delta_angle))
    except Exception as e:
        print(e)


def process_one_file_single_view(fn_args):
    fn, args = fn_args
    output_path = pathlib.Path(args.output_dir)
    if not args.overwrite:
        if output_path.joinpath(fn.stem + ".png").exists():
            return
    try:
        shape = Compound.load_from_step(str(fn))
        render(shape, output_path.joinpath(fn.stem + ".png"), args.width, args.height, euler_angles_radians=(0, 0, 0))
    except Exception as e:
        print(e)


def initializer():
    """Ignore CTRL+C in the worker process."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def main():
    p = argparse.ArgumentParser("Render a folder of STEP files from a single view or multi-view by rotating the shape")
    p.add_argument("--input_dir", "-i", type=str, required=True, help="Input folder of STP/STEP files")
    p.add_argument("--output_dir", "-o", type=str, required=True, help="Output folder of PNG files")
    p.add_argument("--width", "-wi", type=int, default=1024, help="Width of image")
    p.add_argument("--height", "-he", type=int, default=768, help="Height of image")
    p.add_argument("--num_images", "-n", type=int, default=1, help="Number of images from different viewpoints")
    p.add_argument("--num_procs", "-p", type=int, default=8, help="Number of processes for concurrent rendering")
    p.add_argument("--overwrite", "-ov", action="store_true", help="Whether to overwrite existing images")

    args = p.parse_args()

    assert args.num_images >= 1

    input_path = pathlib.Path(args.input_dir)
    output_path = pathlib.Path(args.output_dir)
    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)

    files = list(input_path.rglob("*.st*p"))

    fn_args = zip(files, repeat(args))
    pool = Pool(args.num_procs, initializer=initializer)
    try:
        fn = process_one_file_multi_view if args.num_images > 1 else process_one_file_single_view
        results = list(tqdm(pool.imap(fn, fn_args), total=len(files)))
        print(f"Finished processing {len(results)} files.")
    except KeyboardInterrupt:
        pool.terminate()
        pool.join()


if __name__ == "__main__":
    main()

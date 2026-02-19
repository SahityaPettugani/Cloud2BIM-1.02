import argparse
import os
import subprocess
import sys

import numpy as np

try:
    import laspy
except ImportError as exc:
    raise SystemExit(
        "Missing dependency: laspy. Install it with: python -m pip install laspy"
    ) from exc


def _scale_color_to_255(values):
    if values is None:
        return None
    values = np.asarray(values)
    if values.size == 0:
        return None
    max_val = values.max()
    if max_val == 0:
        return np.zeros_like(values, dtype=np.int32)
    if max_val <= 255:
        return values.astype(np.int32)
    return np.clip(np.rint(values / 65535.0 * 255.0), 0, 255).astype(np.int32)


def convert_las_to_xyz(las_path, xyz_path, chunk_size, step):
    header = "X\tY\tZ\tR\tG\tB\tIntensity"
    output_dir = os.path.dirname(xyz_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with laspy.open(las_path) as reader:
        with open(xyz_path, "w", encoding="utf-8") as handle:
            handle.write(header + "\n")

            for chunk in reader.chunk_iterator(chunk_size):
                if step > 1:
                    chunk = chunk[::step]

                points = np.vstack([chunk.x, chunk.y, chunk.z]).T

                if hasattr(chunk, "red") and hasattr(chunk, "green") and hasattr(chunk, "blue"):
                    r = _scale_color_to_255(chunk.red)
                    g = _scale_color_to_255(chunk.green)
                    b = _scale_color_to_255(chunk.blue)
                    if r is None or g is None or b is None:
                        rgb = np.zeros((points.shape[0], 3), dtype=np.int32)
                    else:
                        rgb = np.column_stack([r, g, b])
                else:
                    rgb = np.zeros((points.shape[0], 3), dtype=np.int32)

                if hasattr(chunk, "intensity"):
                    intensity = np.asarray(chunk.intensity).reshape(-1, 1)
                else:
                    intensity = np.zeros((points.shape[0], 1), dtype=np.int32)

                data = np.hstack([points, rgb, intensity])
                np.savetxt(
                    handle,
                    data,
                    delimiter="\t",
                    comments="",
                    fmt="%.6f\t%.6f\t%.6f\t%d\t%d\t%d\t%d",
                )


def run_cloud2entities(xyz_path, ifc_path):
    script_path = os.path.join(os.path.dirname(__file__), "cloud2entities.py")
    cmd = [sys.executable, script_path, "--xyz_files", xyz_path, "--output_ifc", ifc_path]
    subprocess.run(cmd, check=True)


def run_view_ifc(ifc_path, renderer):
    script_path = os.path.join(os.path.dirname(__file__), "view_ifc.py")
    cmd = [sys.executable, script_path, ifc_path, "--renderer", renderer]
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser(
        description="Convert LAS to XYZ, generate IFC, and open the viewer."
    )
    parser.add_argument("las_path", help="Path to input .las file")
    parser.add_argument("--xyz_path", help="Output .xyz path (optional)")
    parser.add_argument("--ifc_path", default="output_IFC/las_output.ifc", help="Output IFC path")
    parser.add_argument("--chunk_size", type=int, default=1_000_000,
                        help="LAS points per chunk for conversion")
    parser.add_argument("--step", type=int, default=1,
                        help="Keep every Nth point during conversion")
    parser.add_argument("--renderer", choices=["open3d", "pyvista"], default="pyvista",
                        help="Renderer for viewing the IFC")
    args = parser.parse_args()

    las_path = args.las_path
    if args.xyz_path:
        xyz_path = args.xyz_path
    else:
        base, _ = os.path.splitext(las_path)
        xyz_path = base + ".xyz"

    os.makedirs("output_xyz", exist_ok=True)
    os.makedirs(os.path.dirname(args.ifc_path), exist_ok=True)

    convert_las_to_xyz(las_path, xyz_path, args.chunk_size, args.step)
    print(f"XYZ saved: {xyz_path}")

    run_cloud2entities(xyz_path, args.ifc_path)
    run_view_ifc(args.ifc_path, args.renderer)


if __name__ == "__main__":
    main()

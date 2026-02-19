import argparse
import os

import numpy as np
import open3d as o3d


def convert_ply_to_xyz(ply_path, xyz_path):
    pcd = o3d.io.read_point_cloud(ply_path)
    points = np.asarray(pcd.points)
    if points.size == 0:
        raise ValueError(f"No points found in {ply_path}")

    colors = np.asarray(pcd.colors)
    if colors.size == 0:
        rgb = np.zeros((points.shape[0], 3), dtype=np.int32)
    else:
        rgb = np.clip(np.rint(colors * 255.0), 0, 255).astype(np.int32)

    intensity = np.zeros((points.shape[0], 1), dtype=np.int32)

    data = np.hstack([points, rgb, intensity])
    header = "X\tY\tZ\tR\tG\tB\tIntensity"

    os.makedirs(os.path.dirname(xyz_path), exist_ok=True)
    np.savetxt(xyz_path, data, delimiter="\t", header=header, comments="", fmt="%.6f\t%.6f\t%.6f\t%d\t%d\t%d\t%d")


def main():
    parser = argparse.ArgumentParser(description="Convert a PLY point cloud to Cloud2BIM XYZ format.")
    parser.add_argument("ply_path", help="Path to input .ply file")
    parser.add_argument("--output_xyz", help="Path to output .xyz file")
    args = parser.parse_args()

    ply_path = args.ply_path
    if args.output_xyz:
        xyz_path = args.output_xyz
    else:
        base, _ = os.path.splitext(ply_path)
        xyz_path = base + ".xyz"

    convert_ply_to_xyz(ply_path, xyz_path)
    print(f"Saved: {xyz_path}")


if __name__ == "__main__":
    main()

import argparse
import os
import subprocess
import sys

from convert_ply_to_xyz import convert_ply_to_xyz


def build_default_xyz_path(ply_path):
    base = os.path.splitext(os.path.basename(ply_path))[0]
    return os.path.join("output_xyz", f"{base}.xyz")


def main():
    parser = argparse.ArgumentParser(
        description="Convert a PLY point cloud to XYZ and run Cloud2BIM to generate IFC."
    )
    parser.add_argument("ply_path", help="Path to input .ply file")
    parser.add_argument(
        "--output_ifc",
        default=os.path.join("output_IFC", "output.ifc"),
        help="Path to output .ifc file",
    )
    parser.add_argument(
        "--output_xyz",
        help="Optional path to output .xyz file (default: output_xyz/<ply_name>.xyz)",
    )
    parser.add_argument(
        "cloud2entities_args",
        nargs=argparse.REMAINDER,
        help="Additional arguments passed to cloud2entities.py (prefix with --)",
    )
    args = parser.parse_args()

    ply_path = args.ply_path
    output_ifc = args.output_ifc
    output_xyz = args.output_xyz or build_default_xyz_path(ply_path)

    os.makedirs(os.path.dirname(output_ifc), exist_ok=True)
    os.makedirs(os.path.dirname(output_xyz), exist_ok=True)

    convert_ply_to_xyz(ply_path, output_xyz)

    cmd = [
        sys.executable,
        os.path.join(os.path.dirname(__file__), "cloud2entities.py"),
        "--xyz_files",
        output_xyz,
        "--output_ifc",
        output_ifc,
    ]

    if args.cloud2entities_args:
        cmd.extend(args.cloud2entities_args)

    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()

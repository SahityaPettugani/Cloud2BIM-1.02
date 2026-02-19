import argparse
import os

import numpy as np
import ifcopenshell
import ifcopenshell.geom
import open3d as o3d


def export_ifc_to_obj(ifc_path, obj_path):
    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)

    model = ifcopenshell.open(ifc_path)
    vertices = []
    faces = []
    vertex_offset = 0

    for product in model.by_type("IfcProduct"):
        if not getattr(product, "Representation", None):
            continue
        try:
            shape = ifcopenshell.geom.create_shape(settings, product)
        except Exception:
            continue

        verts = np.array(shape.geometry.verts, dtype=float).reshape(-1, 3)
        face_indices = np.array(shape.geometry.faces, dtype=int).reshape(-1, 3)

        vertices.append(verts)
        faces.append(face_indices + vertex_offset)
        vertex_offset += verts.shape[0]

    if not vertices:
        raise RuntimeError("No geometry found in IFC. Ensure ifcopenshell has geometry support.")

    all_vertices = np.vstack(vertices)
    all_faces = np.vstack(faces)

    os.makedirs(os.path.dirname(obj_path), exist_ok=True)
    with open(obj_path, "w", encoding="utf-8") as f:
        for v in all_vertices:
            f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
        for tri in all_faces:
            f.write(f"f {tri[0] + 1} {tri[1] + 1} {tri[2] + 1}\n")

    return obj_path


def export_ifc_mesh(ifc_path):
    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)

    model = ifcopenshell.open(ifc_path)
    vertices = []
    faces = []
    vertex_offset = 0

    for product in model.by_type("IfcProduct"):
        if not getattr(product, "Representation", None):
            continue
        try:
            shape = ifcopenshell.geom.create_shape(settings, product)
        except Exception:
            continue

        verts = np.array(shape.geometry.verts, dtype=float).reshape(-1, 3)
        face_indices = np.array(shape.geometry.faces, dtype=int).reshape(-1, 3)

        vertices.append(verts)
        faces.append(face_indices + vertex_offset)
        vertex_offset += verts.shape[0]

    if not vertices:
        raise RuntimeError("No geometry found in IFC. Ensure ifcopenshell has geometry support.")

    all_vertices = np.vstack(vertices)
    all_faces = np.vstack(faces)
    return all_vertices, all_faces


def show_obj(obj_path):
    mesh = o3d.io.read_triangle_mesh(obj_path)
    if not mesh.has_triangles():
        raise RuntimeError("Failed to load triangles from OBJ.")
    mesh.compute_vertex_normals()
    o3d.visualization.draw_geometries([mesh])


def show_pyvista(vertices, faces):
    try:
        import pyvista as pv
    except ImportError as exc:
        raise RuntimeError(
            "pyvista is not installed. Install it with: python -m pip install pyvista"
        ) from exc

    face_cells = np.hstack([
        np.full((faces.shape[0], 1), 3, dtype=np.int64),
        faces.astype(np.int64)
    ]).ravel()

    mesh = pv.PolyData(vertices, face_cells)
    plotter = pv.Plotter()
    plotter.add_mesh(mesh, color="lightgray", show_edges=False)
    plotter.add_axes()
    plotter.show()


def main():
    parser = argparse.ArgumentParser(description="Export IFC to OBJ and preview it using Open3D or PyVista.")
    parser.add_argument("ifc_path", nargs="?", default="output_IFC/scaniverse.ifc", help="Path to IFC file")
    parser.add_argument("--obj_path", default="output_IFC/scaniverse.obj", help="Path to output OBJ file")
    parser.add_argument("--renderer", choices=["open3d", "pyvista"], default="open3d",
                        help="Renderer to use for preview")
    parser.add_argument("--no_show", action="store_true", help="Only export OBJ, do not open a viewer")
    args = parser.parse_args()

    if args.renderer == "open3d":
        obj_path = export_ifc_to_obj(args.ifc_path, args.obj_path)
        print(f"OBJ saved: {obj_path}")
        if not args.no_show:
            show_obj(obj_path)
    else:
        vertices, faces = export_ifc_mesh(args.ifc_path)
        if args.no_show:
            obj_path = export_ifc_to_obj(args.ifc_path, args.obj_path)
            print(f"OBJ saved: {obj_path}")
        else:
            show_pyvista(vertices, faces)


if __name__ == "__main__":
    main()

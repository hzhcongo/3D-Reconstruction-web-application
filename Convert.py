import trimesh
mesh = trimesh.load_mesh('trimmed_mesh.ply')
# mesh.export('trimmed_mesh.obj')
# mesh.export('trimmed_mesh.stl')
mesh.export('trimmed_mesh.json')

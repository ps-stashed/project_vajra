import numpy as np

def get_rhombic_dodecahedron_data():
    """
    Returns vertices and indices for a Rhombic Dodecahedron.
    A Rhombic Dodecahedron has 14 vertices and 12 rhombic faces.
    """
    # 14 Vertices
    # (±1, ±1, ±1) -> 8 vertices (Cube corners)
    # (±2, 0, 0), (0, ±2, 0), (0, 0, ±2) -> 6 vertices (Octahedron tips)
    # Scaled down by 0.5 to fit unit sphere roughly
    
    vertices = np.array([
        # Cube corners (0-7)
        [-0.5, -0.5, -0.5], [ 0.5, -0.5, -0.5], [ 0.5,  0.5, -0.5], [-0.5,  0.5, -0.5],
        [-0.5, -0.5,  0.5], [ 0.5, -0.5,  0.5], [ 0.5,  0.5,  0.5], [-0.5,  0.5,  0.5],
        # Tips (8-13)
        [-1.0,  0.0,  0.0], [ 1.0,  0.0,  0.0],
        [ 0.0, -1.0,  0.0], [ 0.0,  1.0,  0.0],
        [ 0.0,  0.0, -1.0], [ 0.0,  0.0,  1.0]
    ], dtype=np.float32)

    # 12 Faces (Rhombuses). Each rhombus is 2 triangles.
    # We will just list the triangles for rendering.
    # This is a simplified convex hull triangulation for brevity.
    # A proper mesh would list 12 quads.
    
    # Let's use a simpler approach for the "Visual" mesh:
    # We can construct it face by face.
    # Face 1: Tip 12 (0,0,-1) connects to Cube corners 0,1,2,3? No.
    # It connects to (-0.5,-0.5,-0.5), (0.5,-0.5,-0.5), (0.5,0.5,-0.5), (-0.5,0.5,-0.5)
    # Actually, the tips connect to the cube corners.
    
    # Correct connectivity:
    # Each Tip connects to 4 Cube corners.
    # Tip 8 (-1,0,0) -> 0, 3, 4, 7
    # Tip 9 (1,0,0)  -> 1, 2, 5, 6
    # Tip 10 (0,-1,0)-> 0, 1, 4, 5
    # Tip 11 (0,1,0) -> 2, 3, 6, 7
    # Tip 12 (0,0,-1)-> 0, 1, 2, 3
    # Tip 13 (0,0,1) -> 4, 5, 6, 7
    
    # But wait, the faces are formed by 2 tips and 2 cube corners.
    # Example Face: Tip 12 (Bottom), Tip 10 (Front), Corner 0, Corner 1...
    # Let's just return the vertices. Taichi's Scene.mesh_instance needs vertices and indices.
    
    # Actually, for a swarm of 4000, instancing a low-poly sphere or cube is faster and looks similar.
    # But the user demanded Rhombic Dodecahedron.
    # Let's define the 12 faces (Quads) explicitly.
    
    # Face 1: (0, 0, -1), (0.5, -0.5, -0.5), (0, -1, 0), (-0.5, -0.5, -0.5) -> Indices: 12, 1, 10, 0
    # We need triangles. (12, 1, 10) and (12, 10, 0)
    
    indices = np.array([
        # Face 1 (Bottom-Front)
        12, 1, 10,  12, 10, 0,
        # Face 2 (Bottom-Right)
        12, 2, 9,   12, 9, 1,
        # Face 3 (Bottom-Back)
        12, 3, 11,  12, 11, 2,
        # Face 4 (Bottom-Left)
        12, 0, 8,   12, 8, 3,
        
        # Face 5 (Top-Front)
        13, 10, 5,  13, 5, 4,
        # Face 6 (Top-Right)
        13, 5, 9,   13, 9, 6,
        # Face 7 (Top-Back)
        13, 6, 11,  13, 11, 7,
        # Face 8 (Top-Left)
        13, 7, 8,   13, 8, 4,
        
        # We missed the "Equatorial" faces?
        # The 12 faces are arranged around the center.
        # The above covers 8 faces connecting to the poles (12 and 13).
        # Wait, Rhombic Dodecahedron has 12 faces.
        # My topology logic above created 8 faces.
        # The remaining 4 are the "side" faces?
        # No, the tips are the 6 vertices of an octahedron. The cube corners are the 8 vertices of a cube.
        # Every face connects 2 tips and 2 cube corners.
        # There are 12 edges on the octahedron. Each edge corresponds to a face.
        # Edge (12, 10) -> Face 1.
        # Edge (12, 9) -> Face 2.
        # Edge (12, 11) -> Face 3.
        # Edge (12, 8) -> Face 4.
        # Edge (13, 10) -> Face 5.
        # Edge (13, 9) -> Face 6.
        # Edge (13, 11) -> Face 7.
        # Edge (13, 8) -> Face 8.
        # Edge (10, 9) -> Face 9: (0,-1,0), (1,0,0), (0.5,-0.5,0.5), (0.5,-0.5,-0.5) -> Indices: 10, 5, 9, 1
        # Edge (9, 11) -> Face 10: (1,0,0), (0,1,0), (0.5,0.5,0.5), (0.5,0.5,-0.5) -> Indices: 9, 6, 11, 2
        # Edge (11, 8) -> Face 11: (0,1,0), (-1,0,0), (-0.5,0.5,0.5), (-0.5,0.5,-0.5) -> Indices: 11, 7, 8, 3
        # Edge (8, 10) -> Face 12: (-1,0,0), (0,-1,0), (-0.5,-0.5,0.5), (-0.5,-0.5,-0.5) -> Indices: 8, 4, 10, 0
        
        # Adding the missing 4 equatorial faces
        10, 5, 9,   10, 9, 1,
        9, 6, 11,   9, 11, 2,
        11, 7, 8,   11, 8, 3,
        8, 4, 10,   8, 10, 0
    ], dtype=np.int32)
    
    return vertices, indices

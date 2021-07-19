def write_obj(pathname, verts, tris):

    # Write the mesh to OBJ
    with open(pathname, "w") as fh:
        fh.write("# WaveFront *.obj file\n")
        fh.write(f"# Vertices: {len(verts)}\n")
        fh.write(f"# Triangles : {len(tris)}\n\n")

        for v in verts:
            fh.write(f"v {v[0]} {v[1]} {v[2]} \n")

        for tri in tris:
            fh.write(f"f {tri[0]+1} {tri[1]+1} {tri[2]+1} \n")

        fh.write(f"\n# End of file")

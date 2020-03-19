import os

def stl_to_gltf(path_to_stl, out_path, is_binary):
    import struct

    gltf2 = '''
{
  "scenes" : [
    {
      "nodes" : [ 0 ]
    }
  ],

  "nodes" : [
    {
      "mesh" : 0
    }
  ],

  "meshes" : [
    {
      "primitives" : [ {
        "attributes" : {
          "POSITION" : 1
        },
        "indices" : 0
      } ]
    }
  ],

  "buffers" : [
    {
      %s
      "byteLength" : %d
    }
  ],
  "bufferViews" : [
    {
      "buffer" : 0,
      "byteOffset" : 0,
      "byteLength" : %d,
      "target" : 34963
    },
    {
      "buffer" : 0,
      "byteOffset" : %d,
      "byteLength" : %d,
      "target" : 34962
    }
  ],
  "accessors" : [
    {
      "bufferView" : 0,
      "byteOffset" : 0,
      "componentType" : 5125,
      "count" : %d,
      "type" : "SCALAR",
      "max" : [ %d ],
      "min" : [ 0 ]
    },
    {
      "bufferView" : 1,
      "byteOffset" : 0,
      "componentType" : 5126,
      "count" : %d,
      "type" : "VEC3",
      "min" : [%f, %f, %f],
      "max" : [%f, %f, %f]
    }
  ],

  "asset" : {
    "version" : "2.0"
  }
}
'''

    header_bytes = 80
    unsigned_long_int_bytes = 4
    float_bytes = 4
    vec3_bytes = 4 * 3
    spacer_bytes = 2
    num_vertices_in_face = 3

    vertices = {}
    indices = []

    if not is_binary:
        out_bin = os.path.join(out_path, "out.bin")
        out_gltf = os.path.join(out_path, "out.gltf")
    else:
        out_bin = out_path

    unpack_face = struct.Struct("<12fH").unpack
    face_bytes = float_bytes*12 + 2

    with open(path_to_stl, "rb") as f:
        f.seek(header_bytes) # skip 80 bytes headers

        num_faces_bytes = f.read(unsigned_long_int_bytes)
        number_faces = struct.unpack("<I", num_faces_bytes)[0]

        # the vec3_bytes is for normal
        stl_assume_bytes = header_bytes + unsigned_long_int_bytes + number_faces * (vec3_bytes*3 + spacer_bytes + vec3_bytes)
        assert stl_assume_bytes == os.path.getsize(path_to_stl), "stl is not binary or ill formatted"

        minx, maxx = [9999999, -9999999]
        miny, maxy = [9999999, -9999999]
        minz, maxz = [9999999, -9999999]

        vertices_length_counter = 0

        data = struct.unpack("<" + "12fH"*number_faces, f.read())
        len_data = len(data)

        for i in range(0, len_data, 13):
            for j in range(3, 12, 3):
                x, y, z = data[i+j:i+j+3]

                x = int(x*100000)/100000
                y = int(y*100000)/100000
                z = int(z*100000)/100000

                tuple_xyz = (x, y, z);

                try:
                    indices.append(vertices[tuple_xyz])
                except KeyError:
                    vertices[tuple_xyz] = vertices_length_counter
                    vertices_length_counter += 1
                    indices.append(vertices[tuple_xyz])



                if x < minx: minx = x
                if x > maxx: maxx = x
                if y < miny: miny = y
                if y > maxy: maxy = y
                if z < minz: minz = z
                if z > maxz: maxz = z

            # f.seek(spacer_bytes, 1) # skip the spacer

    number_vertices = len(vertices)
    vertices_bytelength = number_vertices * vec3_bytes # each vec3 has 3 floats, each float is 4 bytes
    unpadded_indices_bytelength = number_vertices * unsigned_long_int_bytes

    out_number_vertices = len(vertices)
    out_number_indices = len(indices)

    unpadded_indices_bytelength = out_number_indices * unsigned_long_int_bytes
    indices_bytelength = (unpadded_indices_bytelength + 3) & ~3

    out_bin_bytelength = vertices_bytelength + indices_bytelength

    if is_binary:
        out_bin_uir = ""
    else:
        out_bin_uir = '"uri": "out.bin",'

    gltf2 = gltf2 % ( out_bin_uir,
                #buffer
                out_bin_bytelength,

                # bufferViews[0]
                indices_bytelength,

                # bufferViews[1]
                indices_bytelength,
                vertices_bytelength,

                # accessors[0]
                out_number_indices,
                out_number_vertices - 1,

                # accessors[1]
                out_number_vertices,
                minx, miny, minz,
                maxx, maxy, maxz
    )

    glb_out = bytearray()
    if is_binary:
        gltf2 = gltf2.replace(" ", "")
        gltf2 = gltf2.replace("\n", "")

        scene = bytearray(gltf2.encode())

        scene_len = len(scene)
        padded_scene_len = (scene_len + 3) & ~3
        body_offset = padded_scene_len + 12 + 8

        file_len = body_offset + out_bin_bytelength + 8

        # 12-byte header
        glb_out.extend(struct.pack('<I', 0x46546C67)) # magic number for glTF
        glb_out.extend(struct.pack('<I', 2))
        glb_out.extend(struct.pack('<I', file_len))

        # chunk 0
        glb_out.extend(struct.pack('<I', padded_scene_len))
        glb_out.extend(struct.pack('<I', 0x4E4F534A)) # magic number for JSON
        glb_out.extend(scene)

        while len(glb_out) < body_offset:
            glb_out.extend(b' ')

        # chunk 1
        glb_out.extend(struct.pack('<I', out_bin_bytelength))
        glb_out.extend(struct.pack('<I', 0x004E4942)) # magin number for BIN

    # print('<%dI' % len(indices))
    # print(struct.pack('<%dI' % len(indices), *indices))
    glb_out.extend(struct.pack('<%dI' % len(indices), *indices))

    for i in range(indices_bytelength - unpadded_indices_bytelength):
        glb_out.extend(b' ')

    vertices = dict((v, k) for k,v in vertices.items())

    # glb_out.extend(struct.pack('f',
    # print([each_v for vertices[v_counter] for v_counter in range(number_vertices)]) # magin number for BIN
    vertices = [vertices[i] for i in range(number_vertices)]
    flatten = lambda l: [item for sublist in l for item in sublist]

    # for v_counter in :
        # v_3f = vertices[v_counter]
        # all_floats_in_vertices.append(v_3f[0])
        # all_floats_in_vertices.append(v_3f[1])
        # all_floats_in_vertices.append(v_3f[2])

    # for v_counter in range(number_vertices):
    glb_out.extend(struct.pack('%df' % number_vertices*3, *flatten(vertices))) # magin number for BIN

    # for v_counter in range(number_vertices):
        # glb_out.extend(struct.pack('3f', *vertices[v_counter])) # magin number for BIN

    # for (v_x, v_y, v_z), _ in sorted(vertices.items(), key=lambda x: x[1]):
        # glb_out.extend(struct.pack('3f', v_x, v_y, v_z)) # magin number for BIN
        # # glb_out.extend(struct.pack('f', v_y)) # magin number for BIN
        # # glb_out.extend(struct.pack('f', v_z)) # magin number for BIN

    with open(out_bin, "wb") as out:
        out.write(glb_out)

    if not is_binary:
        with open(out_gltf, "w") as out:
            out.write(gltf2)

    print("Done! Exported to %s" %out_path)

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 3:
        print("use it like python3 stl_to_gltf.py /path/to/stl /path/to/gltf/folder")
        print("or          python3 stl_to_gltf.py /path/to/stl /path/to/glb/file -b")
        sys.exit(1)

    path_to_stl = sys.argv[1]
    out_path = sys.argv[2]
    if len(sys.argv) > 3:
        is_binary = True
    else:
        is_binary = False

    if out_path.lower().endswith(".glb"):
        print("Use binary mode since output file has glb extension")
        is_binary = True
    else:
        if is_binary:
            print("output file should have glb extension but not %s", out_path)

    if not os.path.exists(path_to_stl):
        print("stl file does not exists %s" % path_to_stl)

    if not is_binary:
        if not os.path.isdir(out_path):
            os.mkdir(out_path)

    stl_to_gltf(path_to_stl, out_path, is_binary)


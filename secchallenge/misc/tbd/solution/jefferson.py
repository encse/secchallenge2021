# https://github.com/sviehb/jefferson/

import lzma
import struct
import stat
import os
import zlib
import binascii
import cstruct

LZMA_BEST_LC = 0
LZMA_BEST_LP = 0
LZMA_BEST_PB = 0

pb = LZMA_BEST_PB
lp = LZMA_BEST_LP
lc = LZMA_BEST_LC
PROPERTIES = (pb * 5 + lp) * 9 + lc

DICT_SIZE = 0x2000


def decompress(data, outlen):
    lzma_header = struct.pack("<BIQ", PROPERTIES, DICT_SIZE, outlen)
    lzma_data = lzma_header + data
    decompressed = lzma.decompress(lzma_data)
    return decompressed


def decompress(data_in, destlen):
    positions = [0] * 256
    cpage_out = bytearray([0] * destlen)
    outpos = 0
    pos = 0
    while outpos < destlen:
        value = data_in[pos]
        pos += 1
        cpage_out[outpos] = value
        outpos += 1
        repeat = data_in[pos]
        pos += 1

        backoffs = positions[value]
        positions[value] = outpos
        if repeat:
            if backoffs + repeat >= outpos:
                while repeat:
                    cpage_out[outpos] = cpage_out[backoffs]
                    outpos += 1
                    backoffs += 1
                    repeat -= 1
            else:
                cpage_out[outpos: outpos + repeat] = cpage_out[
                                                     backoffs: backoffs + repeat
                                                     ]
                outpos += repeat
    return cpage_out


def PAD(x):
    return ((x) + 3) & ~3


JFFS2_MAGIC_BITMASK = 0x1985
JFFS2_COMPR_NONE = 0x00
JFFS2_COMPR_ZERO = 0x01
JFFS2_COMPR_RTIME = 0x02
JFFS2_COMPR_RUBINMIPS = 0x03
JFFS2_COMPR_COPY = 0x04
JFFS2_COMPR_DYNRUBIN = 0x05
JFFS2_COMPR_ZLIB = 0x06
JFFS2_COMPR_LZO = 0x07
JFFS2_COMPR_LZMA = 0x08

# /* Compatibility flags. */
JFFS2_COMPAT_MASK = 0xC000  # /* What do to if an unknown nodetype is found */
JFFS2_NODE_ACCURATE = 0x2000
# /* INCOMPAT: Fail to mount the filesystem */
JFFS2_FEATURE_INCOMPAT = 0xC000
# /* ROCOMPAT: Mount read-only */
JFFS2_FEATURE_ROCOMPAT = 0x8000
# /* RWCOMPAT_COPY: Mount read/write, and copy the node when it's GC'd */
JFFS2_FEATURE_RWCOMPAT_COPY = 0x4000
# /* RWCOMPAT_DELETE: Mount read/write, and delete the node when it's GC'd */
JFFS2_FEATURE_RWCOMPAT_DELETE = 0x0000

JFFS2_NODETYPE_DIRENT = JFFS2_FEATURE_INCOMPAT | JFFS2_NODE_ACCURATE | 1
JFFS2_NODETYPE_INODE = JFFS2_FEATURE_INCOMPAT | JFFS2_NODE_ACCURATE | 2
JFFS2_NODETYPE_CLEANMARKER = JFFS2_FEATURE_RWCOMPAT_DELETE | JFFS2_NODE_ACCURATE | 3
JFFS2_NODETYPE_PADDING = JFFS2_FEATURE_RWCOMPAT_DELETE | JFFS2_NODE_ACCURATE | 4
JFFS2_NODETYPE_SUMMARY = JFFS2_FEATURE_RWCOMPAT_DELETE | JFFS2_NODE_ACCURATE | 6
JFFS2_NODETYPE_XATTR = JFFS2_FEATURE_INCOMPAT | JFFS2_NODE_ACCURATE | 8
JFFS2_NODETYPE_XREF = JFFS2_FEATURE_INCOMPAT | JFFS2_NODE_ACCURATE | 9


def mtd_crc(data):
    return (binascii.crc32(data, -1) ^ -1) & 0xFFFFFFFF


cstruct.typedef("uint8", "uint8_t")
cstruct.typedef("uint16", "jint16_t")
cstruct.typedef("uint32", "jint32_t")
cstruct.typedef("uint32", "jmode_t")


class Jffs2_unknown_node(cstruct.CStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __struct__ = """
        /* All start like this */
        jint16_t magic;
        jint16_t nodetype;
        jint32_t totlen; /* So we can skip over nodes we don't grok */
        jint32_t hdr_crc;
    """

    def unpack(self, data):
        cstruct.CStruct.unpack(self, data[: self.size])
        comp_hrd_crc = mtd_crc(data[: self.size - 4])

        if comp_hrd_crc == self.hdr_crc:
            self.hdr_crc_match = True
        else:
            # print("hdr_crc does not match!")
            self.hdr_crc_match = False


class Jffs2_raw_xattr(cstruct.CStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __struct__ = """
        jint16_t magic;
        jint16_t nodetype;      /* = JFFS2_NODETYPE_XATTR */
        jint32_t totlen;
        jint32_t hdr_crc;
        jint32_t xid;           /* XATTR identifier number */
        jint32_t version;
        uint8_t xprefix;
        uint8_t name_len;
        jint16_t value_len;
        jint32_t data_crc;
        jint32_t node_crc;
        uint8_t data[0];
    """


class Jffs2_raw_summary(cstruct.CStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __struct__ = """
        jint16_t magic;
        jint16_t nodetype;      /* = JFFS2_NODETYPE_SUMMARY */
        jint32_t totlen;
        jint32_t hdr_crc;
        jint32_t sum_num;       /* number of sum entries*/
        jint32_t cln_mkr;       /* clean marker size, 0 = no cleanmarker */
        jint32_t padded;        /* sum of the size of padding nodes */
        jint32_t sum_crc;       /* summary information crc */
        jint32_t node_crc;      /* node crc */
        jint32_t sum[0];        /* inode summary info */
    """


class Jffs2_raw_xref(cstruct.CStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __struct__ = """
        jint16_t magic;
        jint16_t nodetype;      /* = JFFS2_NODETYPE_XREF */
        jint32_t totlen;
        jint32_t hdr_crc;
        jint32_t ino;           /* inode number */
        jint32_t xid;           /* XATTR identifier number */
        jint32_t xseqno;        /* xref sequencial number */
        jint32_t node_crc;
    """


class Jffs2_raw_dirent(cstruct.CStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __struct__ = """
        jint16_t magic;
        jint16_t nodetype;      /* == JFFS2_NODETYPE_DIRENT */
        jint32_t totlen;
        jint32_t hdr_crc;
        jint32_t pino;
        jint32_t version;
        jint32_t ino; /* == zero for unlink */
        jint32_t mctime;
        uint8_t nsize;
        uint8_t type;
        uint8_t unused[2];
        jint32_t node_crc;
        jint32_t name_crc;
    /* uint8_t data[0]; -> name */
    """

    def unpack(self, data, node_offset):
        cstruct.CStruct.unpack(self, data[: self.size])
        self.name = data[self.size: self.size + self.nsize]
        self.node_offset = node_offset

        if mtd_crc(data[: self.size - 8]) == self.node_crc:
            self.node_crc_match = True
        else:
            print("node_crc does not match!")
            self.node_crc_match = False

        if mtd_crc(self.name) == self.name_crc:
            self.name_crc_match = True
        else:
            print("data_crc does not match!")
            self.name_crc_match = False

    def __str__(self):
        result = []
        for field in self.__fields__ + ["name", "node_offset"]:
            result.append(field + "=" + str(getattr(self, field, None)))
        return type(self).__name__ + "(" + ", ".join(result) + ")"


class Jffs2_raw_inode(cstruct.CStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __struct__ = """
        jint16_t magic;      /* A constant magic number.  */
        jint16_t nodetype;   /* == JFFS2_NODETYPE_INODE */
        jint32_t totlen;     /* Total length of this node (inc data, etc.) */
        jint32_t hdr_crc;
        jint32_t ino;        /* Inode number.  */
        jint32_t version;    /* Version number.  */
        jmode_t mode;       /* The file's type or mode.  */
        jint16_t uid;        /* The file's owner.  */
        jint16_t gid;        /* The file's group.  */
        jint32_t isize;      /* Total resultant size of this inode (used for truncations)  */
        jint32_t atime;      /* Last access time.  */
        jint32_t mtime;      /* Last modification time.  */
        jint32_t ctime;      /* Change time.  */
        jint32_t offset;     /* Where to begin to write.  */
        jint32_t csize;      /* (Compressed) data size */
        jint32_t dsize;      /* Size of the node's data. (after decompression) */
        uint8_t compr;       /* Compression algorithm used */
        uint8_t usercompr;   /* Compression algorithm requested by the user */
        jint16_t flags;      /* See JFFS2_INO_FLAG_* */
        jint32_t data_crc;   /* CRC for the (compressed) data.  */
        jint32_t node_crc;   /* CRC for the raw inode (excluding data)  */
        /* uint8_t data[0]; */
    """

    def unpack(self, data):
        cstruct.CStruct.unpack(self, data[: self.size])

        node_data = data[self.size: self.size + self.csize]
        if self.compr == JFFS2_COMPR_NONE:
            self.data = node_data
        elif self.compr == JFFS2_COMPR_ZERO:
            self.data = b'\x00' * self.dsize
        elif self.compr == JFFS2_COMPR_ZLIB:
            self.data = zlib.decompress(node_data)
        elif self.compr == JFFS2_COMPR_RTIME:
            self.data = rtime.decompress(node_data, self.dsize)
        elif self.compr == JFFS2_COMPR_LZMA:
            self.data = jffs2_lzma.decompress(node_data, self.dsize)
        else:
            print("compression not implemented", self)
            print(node_data.hex()[:20])
            self.data = node_data

        if len(self.data) != self.dsize:
            print("data length mismatch!")

        if mtd_crc(data[: self.size - 8]) == self.node_crc:
            self.node_crc_match = True
        else:
            print("hdr_crc does not match!")
            self.node_crc_match = False

        if mtd_crc(node_data) == self.data_crc:
            self.data_crc_match = True
        else:
            print("data_crc does not match!")
            self.data_crc_match = False


class Jffs2_device_node_old(cstruct.CStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __struct__ = """
        jint16_t old_id;
    """


class Jffs2_device_node_new(cstruct.CStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __struct__ = """
        jint32_t new_id;
    """


NODETYPES = {
    JFFS2_FEATURE_INCOMPAT: Jffs2_unknown_node,
    JFFS2_NODETYPE_DIRENT: Jffs2_raw_dirent,
    JFFS2_NODETYPE_INODE: Jffs2_raw_inode,
    JFFS2_NODETYPE_CLEANMARKER: "JFFS2_NODETYPE_CLEANMARKER",
    JFFS2_NODETYPE_SUMMARY: Jffs2_raw_summary,
    JFFS2_NODETYPE_XATTR: Jffs2_raw_xattr,
    JFFS2_NODETYPE_XREF: Jffs2_raw_xref,
    JFFS2_NODETYPE_PADDING: "JFFS2_NODETYPE_PADDING",
}


def set_endianness(endianness):
    Jffs2_device_node_new.__fmt__ = endianness + Jffs2_device_node_new.__fmt__[1:]
    Jffs2_device_node_old.__fmt__ = endianness + Jffs2_device_node_old.__fmt__[1:]

    for node in NODETYPES.values():
        if isinstance(node, cstruct.CStructMeta):
            node.__fmt__ = endianness + node.__fmt__[1:]


def scan_fs(content, endianness, verbose=False):
    set_endianness(endianness)
    summaries = []
    pos = 0
    jffs2_magic_bitmask_str = struct.pack(endianness + "H", JFFS2_MAGIC_BITMASK)
    fs_index = 0

    fs = {}
    fs[fs_index] = {}
    fs[fs_index]["endianness"] = endianness
    fs[fs_index][JFFS2_NODETYPE_INODE] = []
    fs[fs_index][JFFS2_NODETYPE_DIRENT] = []
    fs[fs_index][JFFS2_NODETYPE_XATTR] = []
    fs[fs_index][JFFS2_NODETYPE_XREF] = []
    fs[fs_index][JFFS2_NODETYPE_SUMMARY] = []

    dirent_dict = {}
    while True:
        find_result = content.find(
            jffs2_magic_bitmask_str, pos, len(content) - Jffs2_unknown_node.size
        )
        if find_result == -1:
            break
        else:
            pos = find_result

        unknown_node = Jffs2_unknown_node()
        unknown_node.unpack(content[pos: pos + unknown_node.size])
        if not unknown_node.hdr_crc_match:
            pos += 1
            continue
        offset = pos
        pos += PAD(unknown_node.totlen)

        if unknown_node.magic == JFFS2_MAGIC_BITMASK:
            if unknown_node.nodetype in NODETYPES:
                if unknown_node.nodetype == JFFS2_NODETYPE_DIRENT:
                    dirent = Jffs2_raw_dirent()
                    dirent.unpack(content[0 + offset:], offset)
                    if dirent.ino in dirent_dict:
                        print("duplicate inode use detected!!!")
                        fs_index += 1
                        fs[fs_index] = {}
                        fs[fs_index]["endianness"] = endianness
                        fs[fs_index][JFFS2_NODETYPE_INODE] = []
                        fs[fs_index][JFFS2_NODETYPE_DIRENT] = []
                        fs[fs_index][JFFS2_NODETYPE_XATTR] = []
                        fs[fs_index][JFFS2_NODETYPE_XREF] = []
                        fs[fs_index][JFFS2_NODETYPE_SUMMARY] = []
                        dirent_dict = {}

                    dirent_dict[dirent.ino] = dirent

                    fs[fs_index][JFFS2_NODETYPE_DIRENT].append(dirent)
                    if verbose:
                        print("0x%08X:" % (offset), dirent)
                elif unknown_node.nodetype == JFFS2_NODETYPE_INODE:
                    inode = Jffs2_raw_inode()
                    inode.unpack(content[0 + offset:])
                    fs[fs_index][JFFS2_NODETYPE_INODE].append(inode)
                    if verbose:
                        print("0x%08X:" % (offset), inode)
                elif unknown_node.nodetype == JFFS2_NODETYPE_XREF:
                    xref = Jffs2_raw_xref()
                    xref.unpack(content[offset: offset + xref.size])
                    fs[fs_index][JFFS2_NODETYPE_XREF].append(xref)
                    if verbose:
                        print("0x%08X:" % (offset), xref)
                elif unknown_node.nodetype == JFFS2_NODETYPE_XATTR:
                    xattr = Jffs2_raw_xattr()
                    xattr.unpack(content[offset: offset + xattr.size])
                    fs[fs_index][JFFS2_NODETYPE_XREF].append(xattr)
                    if verbose:
                        print("0x%08X:" % (offset), xattr)
                elif unknown_node.nodetype == JFFS2_NODETYPE_SUMMARY:
                    summary = Jffs2_raw_summary()
                    summary.unpack(content[offset: offset + summary.size])
                    summaries.append(summary)
                    fs[fs_index][JFFS2_NODETYPE_SUMMARY].append(summary)
                    if verbose:
                        print("0x%08X:" % (offset), summary)
                elif unknown_node.nodetype == JFFS2_NODETYPE_CLEANMARKER:
                    pass
                elif unknown_node.nodetype == JFFS2_NODETYPE_PADDING:
                    pass
                else:
                    print("Unhandled node type", unknown_node.nodetype, unknown_node)
    return fs.values()


def get_device(inode):
    if not stat.S_ISBLK(inode.mode) and not stat.S_ISCHR(inode.mode):
        return None

    if inode.dsize == len(Jffs2_device_node_new):
        node = Jffs2_device_node_new()
        node.unpack(inode.data)
        return os.makedev(
            (node.new_id & 0xFFF00) >> 8,
            (node.new_id & 0xFF) | ((node.new_id >> 12) & 0xFFF00),
        )

    if inode.dsize == len(Jffs2_device_node_old):
        node = Jffs2_device_node_old()
        node.unpack(inode.data)
        return os.makedev((node.old_id >> 8) & 0xFF, node.old_id & 0xFF)
    return None


def dump_fs(fs, target):
    node_dict = {}

    set_endianness(fs["endianness"])

    for dirent in fs[JFFS2_NODETYPE_DIRENT]:
        dirent.inodes = []
        for inode in fs[JFFS2_NODETYPE_INODE]:
            if inode.ino == dirent.ino:
                dirent.inodes.append(inode)
        if dirent.ino in node_dict:
            print("duplicate dirent.ino use detected!!!", dirent)
        node_dict[dirent.ino] = dirent

    for dirent in fs[JFFS2_NODETYPE_DIRENT]:
        pnode_pino = dirent.pino
        pnodes = []
        for _ in range(100):
            if pnode_pino not in node_dict:
                break
            pnode = node_dict[pnode_pino]
            pnode_pino = pnode.pino
            pnodes.append(pnode)
        pnodes.reverse()

        node_names = []

        for pnode in pnodes:
            node_names.append(pnode.name.decode())
        node_names.append(dirent.name.decode())
        path = "/".join(node_names)

        target_path = os.path.join(os.getcwd(), target, path)
        for inode in dirent.inodes:
            try:
                if stat.S_ISDIR(inode.mode):
                    if not os.path.isdir(target_path):
                        os.makedirs(target_path)
                elif stat.S_ISLNK(inode.mode):
                    if not os.path.islink(target_path):
                        if os.path.exists(target_path):
                            continue
                        os.symlink(inode.data, target_path)
                elif stat.S_ISREG(inode.mode):
                    if not os.path.isfile(target_path):
                        if not os.path.isdir(os.path.dirname(target_path)):
                            os.makedirs(os.path.dirname(target_path))
                        with open(target_path, "wb") as fd:
                            for inode in dirent.inodes:
                                fd.seek(inode.offset)
                                fd.write(inode.data)
                    os.chmod(target_path, stat.S_IMODE(inode.mode))
                    break
                elif stat.S_ISCHR(inode.mode):
                    os.mknod(target_path, inode.mode, get_device(inode))
                elif stat.S_ISBLK(inode.mode):
                    os.mknod(target_path, inode.mode, get_device(inode))
                elif stat.S_ISFIFO(inode.mode):
                    pass
                elif stat.S_ISSOCK(inode.mode):
                    pass
                else:
                    raise Exception("unhandled inode.mode: %o" % inode.mode, inode, dirent)

            except OSError as error:
                raise Exception("OS error(%i): %s" % (error.errno, error.strerror), inode, dirent)


def extract(filesystem, dest_path):
    if os.path.exists(dest_path):
        raise Exception("Destination path already exists!")
    else:
        os.mkdir(dest_path)

    with open(filesystem, "rb") as filesystem:
        content = filesystem.read()

    fs_list = list(scan_fs(content, cstruct.BIG_ENDIAN))
    fs_list += list(scan_fs(content, cstruct.LITTLE_ENDIAN))

    fs_index = 1
    for fs in fs_list:
        if not fs[JFFS2_NODETYPE_DIRENT]:
            continue

        dest_path_fs = os.path.join(dest_path, "fs_%i" % fs_index)
        for key, value in fs.items():
            if key == "endianness":
                continue

        if not os.path.exists(dest_path_fs):
            os.mkdir(dest_path_fs)

        dump_fs(fs, dest_path_fs)
        fs_index += 1

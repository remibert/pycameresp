import os
import machine, rp2

# REMI BERTHOLET START
import uos
def setup():
    print("Performing initial setup")
%s
# REMI BERTHOLET END
# Try to mount the filesystem, and format the flash if it doesn't exist.
# Note: the flash requires the programming size to be aligned to 256 bytes.
bdev = rp2.Flash()
try:
    vfs = os.VfsLfs2(bdev, progsize=256)
except:
    os.VfsLfs2.mkfs(bdev, progsize=256)
    vfs = os.VfsLfs2(bdev, progsize=256)
# REMI BERTHOLET START
    setup()
# REMI BERTHOLET END
os.mount(vfs, "/")

del os, bdev, vfs

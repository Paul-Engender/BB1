#! /bin/bash
# Install Docker
apt-get update
apt-get install -y docker.io

# Format & Mount Persistence Disk
MNT_DIR="/mnt/fuseki-data"
mkdir -p $MNT_DIR
# Check if device is formatted; if not, format it
if ! blkid /dev/disk/by-id/google-fuseki-data; then
    mkfs.ext4 -m 0 -E lazy_itable_init=0,lazy_journal_init=0,discard /dev/disk/by-id/google-fuseki-data
fi
mount -o discard,defaults /dev/disk/by-id/google-fuseki-data $MNT_DIR
chmod 777 $MNT_DIR

# Run Fuseki
docker run -d \
    --name fuseki \
    --restart unless-stopped \
    -p 3030:3030 \
    -v $MNT_DIR:/fuseki/databases \
    -e ADMIN_PASSWORD=admin \
    stain/jena-fuseki:4.6.1 \
    /jena-fuseki/fuseki-server --update --loc=/fuseki/databases/ds /ds

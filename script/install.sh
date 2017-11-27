umount /data1 /data2 /data3 /data4
pvcreate -y /dev/sdb /dev/sdc /dev/sdd /dev/sde
vgcreate sdb_volume /dev/sdb
vgcreate sdc_volume /dev/sdc
vgcreate sdd_volume /dev/sdd
vgcreate sde_volume /dev/sde
lvcreate -L100000 -n data1 sdb_volume
lvcreate -L100000 -n data2 sdb_volume
lvcreate -L100000 -n data1 sdc_volume
lvcreate -L100000 -n data2 sdc_volume
lvcreate -L100000 -n data1 sdd_volume
lvcreate -L100000 -n data2 sdd_volume
mkfs.ext4 /dev/sdb_volume/data1
mkfs.ext4 /dev/sdb_volume/data2
mkfs.ext4 /dev/sdc_volume/data2
mkfs.ext4 /dev/sdc_volume/data1
mkfs.ext4 /dev/sdd_volume/data1
mkfs.ext4 /dev/sdd_volume/data2
mkdir /mnt/disk{1..6}
mount /dev/sdb_volume/data1 /mnt/disk1
mount /dev/sdb_volume/data2 /mnt/disk2
mount /dev/sdc_volume/data1 /mnt/disk3
mount /dev/sdc_volume/data2 /mnt/disk4
mount /dev/sdd_volume/data1 /mnt/disk5
mount /dev/sdd_volume/data2 /mnt/disk6
ln -s /mnt/disk1 /tidb/tikv-dir-1
ln -s /mnt/disk2 /tidb/tikv-dir-2
ln -s /mnt/disk3 /tidb/tikv-dir-3
ln -s /mnt/disk4 /tidb/tikv-dir-4
ln -s /mnt/disk5 /tidb/tikv-dir-5
ln -s /mnt/disk6 /tidb/tikv-dir-6
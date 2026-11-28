# Storage and data safety

Use this reference for persistent volumes, StatefulSets, snapshots, backup, restore, expansion, or data migration.

## Establish the data contract

Identify durability, consistency, recovery-point and recovery-time expectations, access pattern, topology, encryption, backup owner, and restore procedure before changing storage. A successful PVC bind is not proof that an application can recover its data.

## Storage objects

Confirm StorageClass provisioner and parameters, binding mode, reclaim policy, expansion support, topology, access mode, volume mode, mount behavior, and CSI capabilities. Treat provider defaults as target-specific.

Do not assume:

- every CSI driver supports snapshots, cloning, online expansion, or every access mode;
- `ReadWriteOnce` means one pod rather than one node;
- a default StorageClass has a particular reclaim policy;
- a retained PV is a usable backup;
- deleting and recreating a PVC is an acceptable resize path.

## Snapshots and backups

A volume snapshot may be crash-consistent rather than application-consistent. Coordinate quiescing, database-native backup, log or WAL handling, cross-volume consistency, retention, encryption, and restore testing according to the application.

Before destructive work, verify that the recovery artifact exists, is recent enough, is independently retained, and has a tested restore path. Do not mutate PVCs, PVs, reclaim policy, or StatefulSet claim retention without exact authorization.

## Stateful changes

Analyze schema compatibility, replication, quorum, failover, ordered identity, claim ownership, and rollback direction. Scaling a StatefulSet or changing its update strategy can be a data operation even when the manifest change looks small.

## Ephemeral storage

Bound writable temporary storage using application cleanup, volume sizing, and ephemeral-storage requests or limits as appropriate. Memory-backed `emptyDir` consumes memory accounting; disk-backed growth can trigger node pressure.

## Sources

- Persistent volumes: https://kubernetes.io/docs/concepts/storage/persistent-volumes/
- Storage classes: https://kubernetes.io/docs/concepts/storage/storage-classes/
- Volume snapshots: https://kubernetes.io/docs/concepts/storage/volume-snapshots/
- Local ephemeral storage: https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/#local-ephemeral-storage

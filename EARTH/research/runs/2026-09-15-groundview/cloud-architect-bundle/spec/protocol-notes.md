# GroundView protocol notes

v1 ingest is rtl_433 NDJSON plus the GroundView source-event envelope. Canonical identity is `rtl433_protocol:model:sensor_id` under `groundview_canonical_v1`.

Unknown protocols stay OBSERVED. Do not design the domain around one TPMS manufacturer.

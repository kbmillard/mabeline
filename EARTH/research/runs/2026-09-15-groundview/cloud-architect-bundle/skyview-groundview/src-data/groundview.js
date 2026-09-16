import * as Cesium from 'cesium';
import {
  registerEntityContext,
  selectEntityContext,
  clearSelectedEntityContextForLayer,
} from './contextStore.js';
import {
  isOwnedByOtherLayer,
  registerPickOwner,
  resolvePickId,
  unregisterPickOwner,
} from './pickRegistry.js';
import { describeMatch, normalizePresentation, passAnchor } from './groundview/presentation.mjs';

const LAYER_ID = 'groundview';
const API_URL = '/api/groundview/snapshot';
const PASS_RADIUS_M = 420;

const COLORS = {
  receiver: Cesium.Color.fromCssColorString('#7fd4b8'),
  pass: Cesium.Color.fromCssColorString('#f0b429'),
  match: Cesium.Color.fromCssColorString('#f5d76e'),
  track: Cesium.Color.fromCssColorString('#c792ea'),
};

function createGroundViewLayer() {
  let dataSource = null;
  let enabled = false;
  let count = 0;
  let lastUpdate = null;
  let lastError = null;
  let snapshot = { receivers: [], passes: [], matches: [], tracks: [] };
  let presentation = normalizePresentation();
  let rowListener = null;
  let clickHandler = null;
  let selectedId = null;

  function attachCard(entity, position, title, details, accent) {
    const cached = position;
    entity.gevTrackedId = String(entity.id);
    entity.gevDisplayPosition = () => cached;
    entity.gevLabelModel = {
      title,
      details: details.filter(Boolean),
      accent,
    };
  }

  function pickGroundViewEntity(viewer, screenPosition) {
    const drilled = viewer.scene.drillPick(screenPosition, 12) || [];
    const found = [];
    for (const picked of drilled) {
      const entity = picked?.id;
      if (entity && String(entity.id || '').startsWith('groundview:')) found.push(entity);
    }
    const rank = (id) => {
      if (String(id).includes(':receiver:')) return 0;
      if (String(id).includes(':pass:')) return 1;
      if (String(id).includes(':match:')) return 2;
      return 3;
    };
    found.sort((a, b) => rank(a.id) - rank(b.id));
    return found[0] || null;
  }

  function restoreSelection() {
    if (!selectedId || !dataSource) return;
    const entity = dataSource.entities.getById(selectedId);
    if (entity) selectEntityContext(entity);
    else {
      selectedId = null;
      clearSelectedEntityContextForLayer(LAYER_ID);
    }
  }

  function applyShow() {
    if (!dataSource) return;
    for (const entity of dataSource.entities.values) {
      const kind = entity.properties?.kind?.getValue();
      if (kind === 'receiver') entity.show = presentation.showReceivers;
      else if (kind === 'pass') entity.show = presentation.showPasses;
      else if (kind === 'match') entity.show = presentation.showMatches;
      else if (kind === 'track') entity.show = presentation.showTracks;
    }
  }

  function contextFor(kind, record, extra = {}) {
    return {
      id: extra.id,
      layerId: LAYER_ID,
      layerName: 'GROUNDVIEW',
      source: 'GroundView RF (synthetic/replay until field validation)',
      label: extra.label,
      latitude: extra.latitude ?? null,
      longitude: extra.longitude ?? null,
      properties: {
        kind,
        provenance: record.provenance,
        ...extra.properties,
      },
    };
  }

  function paint(viewer) {
    if (!dataSource) return;
    dataSource.entities.removeAll();
    const receivers = new Map((snapshot.receivers || []).map((row) => [row.receiver_id, row]));
    const passes = new Map((snapshot.passes || []).map((row) => [row.pass_id, row]));

    for (const receiver of snapshot.receivers || []) {
      const anchor = passAnchor(receiver);
      if (!anchor) continue;
      const position = Cesium.Cartesian3.fromDegrees(anchor.longitude, anchor.latitude);
      const entity = dataSource.entities.add({
        id: `groundview:receiver:${receiver.receiver_id}`,
        position,
        point: {
          pixelSize: 14,
          color: COLORS.receiver,
          outlineColor: Cesium.Color.BLACK,
          outlineWidth: 1,
          disableDepthTestDistance: Number.POSITIVE_INFINITY,
        },
        label: {
          text: receiver.name || receiver.receiver_id,
          font: '12px sans-serif',
          pixelOffset: new Cesium.Cartesian2(0, -18),
          fillColor: Cesium.Color.WHITE,
        },
        properties: { kind: 'receiver', provenance: 'OBSERVED', receiver_id: receiver.receiver_id },
      });
      registerEntityContext(entity, contextFor('receiver', { provenance: 'OBSERVED' }, {
        id: receiver.receiver_id,
        label: receiver.name || receiver.receiver_id,
        latitude: anchor.latitude,
        longitude: anchor.longitude,
        properties: { coverage: 'receiver site; not a vehicle GPS fix' },
      }));
      attachCard(entity, position, receiver.name || receiver.receiver_id, [
        'OBSERVED receiver site',
        'Coverage pin, not a vehicle GPS fix',
        `${anchor.latitude.toFixed(5)}, ${anchor.longitude.toFixed(5)}`,
      ], '#7fd4b8');
    }

    for (const pass of snapshot.passes || []) {
      const receiver = receivers.get(pass.receiver_id);
      const anchor = passAnchor(receiver);
      if (!anchor) continue;
      const position = Cesium.Cartesian3.fromDegrees(anchor.longitude, anchor.latitude);
      const entity = dataSource.entities.add({
        id: `groundview:pass:${pass.pass_id}`,
        position,
        ellipse: {
          semiMajorAxis: PASS_RADIUS_M,
          semiMinorAxis: PASS_RADIUS_M,
          material: COLORS.pass.withAlpha(0.18),
          outline: true,
          outlineColor: COLORS.pass.withAlpha(0.8),
          heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
        },
        properties: {
          kind: 'pass',
          provenance: pass.provenance,
          pass_id: pass.pass_id,
          receiver_id: pass.receiver_id,
        },
      });
      registerEntityContext(entity, contextFor('pass', pass, {
        id: pass.pass_id,
        label: `Pass at ${pass.receiver_id}`,
        latitude: anchor.latitude,
        longitude: anchor.longitude,
        properties: {
          sensor_count: pass.sensor_count,
          start_time: pass.start_time,
          clustering_version: pass.clustering_version,
          note: 'Drawn at receiver coverage, not a vehicle coordinate',
        },
      }));
      attachCard(entity, position, `Pass at ${pass.receiver_id}`, [
        `${pass.provenance || 'DERIVED'} truck pass`,
        `${pass.sensor_count ?? '—'} sensors in cluster`,
        'Drawn at receiver coverage, not a vehicle coordinate',
      ], '#f0b429');
    }

    for (const match of snapshot.matches || []) {
      const a = receivers.get(match.receiver_a_id);
      const b = receivers.get(match.receiver_b_id);
      if (!passAnchor(a) || !passAnchor(b)) continue;
      const described = describeMatch(match);
      const position = Cesium.Cartesian3.fromDegrees(a.longitude, a.latitude, 40);
      const entity = dataSource.entities.add({
        id: `groundview:match:${match.match_id}`,
        position,
        polyline: {
          positions: Cesium.Cartesian3.fromDegreesArrayHeights([
            a.longitude, a.latitude, 40,
            b.longitude, b.latitude, 40,
          ]),
          width: Number(match.confidence_score) > 0 ? 3 : 1,
          material: COLORS.match.withAlpha(Number(match.confidence_score) > 0 ? 0.9 : 0.2),
        },
        properties: { kind: 'match', ...described },
      });
      registerEntityContext(entity, contextFor('match', match, {
        id: match.match_id,
        label: `Match ${described.confidence_label} ${Number(described.confidence_score).toFixed(2)}`,
        latitude: a.latitude,
        longitude: a.longitude,
        properties: described,
      }));
      attachCard(entity, position, `Match ${described.confidence_label} ${Number(described.confidence_score).toFixed(2)}`, [
        'INFERRED · not confirmed',
        `shared ${described.shared_count ?? '—'}`,
        described.matcher_version || 'groundview_match_v1',
      ], '#f5d76e');
    }

    for (const track of snapshot.tracks || []) {
      const coords = [];
      for (const passId of track.pass_ids || []) {
        const pass = passes.get(passId);
        const receiver = pass ? receivers.get(pass.receiver_id) : null;
        const anchor = passAnchor(receiver);
        if (!anchor) continue;
        coords.push(anchor.longitude, anchor.latitude, 80);
      }
      if (coords.length < 6) continue;
      const position = Cesium.Cartesian3.fromDegrees(coords[0], coords[1], coords[2]);
      const entity = dataSource.entities.add({
        id: `groundview:track:${track.track_id}`,
        position,
        polyline: {
          positions: Cesium.Cartesian3.fromDegreesArrayHeights(coords),
          width: 2,
          material: COLORS.track,
        },
        properties: {
          kind: 'track',
          provenance: track.provenance,
          fork: track.fork,
          weak_edge: track.weak_edge,
          note: 'Inferred relation, not a driven path',
        },
      });
      registerEntityContext(entity, contextFor('track', track, {
        id: track.track_id,
        label: `Track ${track.pass_ids.length} passes`,
        properties: {
          pass_ids: track.pass_ids,
          fork: track.fork,
          weak_edge: track.weak_edge,
          note: 'Inferred relation, not a driven path',
        },
      }));
      attachCard(entity, position, `Track ${track.pass_ids.length} passes`, [
        'INFERRED relation, not a driven path',
        track.fork ? 'fork' : null,
        track.weak_edge ? 'weak edge' : null,
      ], '#c792ea');
    }

    count = dataSource.entities.values.length;
    lastUpdate = Date.now();
    applyShow();
    if (enabled) dataSource.show = true;
    restoreSelection();
    viewer?.scene?.requestRender?.();
  }

  const layer = {
    id: LAYER_ID,
    name: 'GROUNDVIEW',
    icon: '▣',
    source: 'GroundView RF',
    panelGroup: 'mabeline',
    updateInterval: 5000,

    init(viewer) {
      dataSource = new Cesium.CustomDataSource('groundview');
      dataSource.show = false;
      viewer.dataSources.add(dataSource);
      registerPickOwner(LAYER_ID, (pickedId) => String(pickedId || '').startsWith('groundview:'));
      clickHandler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);
      clickHandler.setInputAction((click) => {
        if (!enabled) return;
        const topId = resolvePickId(viewer.scene.pick(click.position));
        if (isOwnedByOtherLayer(LAYER_ID, topId)) return;
        const entity = pickGroundViewEntity(viewer, click.position);
        if (entity && entity.id === selectedId) {
          selectedId = null;
          clearSelectedEntityContextForLayer(LAYER_ID);
          return;
        }
        if (entity) {
          selectedId = entity.id;
          selectEntityContext(entity);
          return;
        }
        if (selectedId) {
          selectedId = null;
          clearSelectedEntityContextForLayer(LAYER_ID);
        }
      }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
      enabled = false;
      selectedId = null;
      count = 0;
      lastUpdate = null;
      lastError = null;
    },

    enable() {
      enabled = true;
      if (dataSource) dataSource.show = true;
    },

    disable() {
      enabled = false;
      selectedId = null;
      if (dataSource) dataSource.show = false;
      clearSelectedEntityContextForLayer(LAYER_ID);
    },

    async update(viewer) {
      try {
        let response = await fetch(API_URL);
        if (!response.ok) {
          lastError = `GroundView HTTP ${response.status}`;
          return false;
        }
        snapshot = await response.json();
        if (!(snapshot.observations || []).length && !(snapshot.receivers || []).length) {
          await fetch('/api/groundview/replay', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ fixture: 'synthetic' }),
          });
          response = await fetch(API_URL);
          if (response.ok) snapshot = await response.json();
        }
        lastError = null;
        paint(viewer);
        return true;
      } catch (error) {
        lastError = error.message || 'GroundView network error';
        return false;
      }
    },

    destroy(viewer) {
      enabled = false;
      selectedId = null;
      unregisterPickOwner(LAYER_ID);
      clearSelectedEntityContextForLayer(LAYER_ID);
      clickHandler?.destroy?.();
      clickHandler = null;
      if (dataSource) {
        viewer.dataSources.remove(dataSource, true);
        dataSource = null;
      }
      count = 0;
    },

    getParams() {
      return { ...presentation };
    },

    setParams(next = {}) {
      presentation = normalizePresentation({ ...presentation, ...next });
      applyShow();
      rowListener?.();
      return true;
    },

    getRowControls() {
      return {
        chips: [
          {
            id: 'receivers',
            label: 'RECEIVERS',
            active: presentation.showReceivers,
            params: { showReceivers: !presentation.showReceivers },
          },
          {
            id: 'passes',
            label: 'TRUCK PASSES',
            active: presentation.showPasses,
            params: { showPasses: !presentation.showPasses },
          },
          {
            id: 'matches',
            label: 'MATCHES',
            active: presentation.showMatches,
            params: { showMatches: !presentation.showMatches },
          },
          {
            id: 'tracks',
            label: 'TRACKS',
            active: presentation.showTracks,
            params: { showTracks: !presentation.showTracks },
          },
        ],
      };
    },

    setRowControlsListener(listener) {
      rowListener = listener;
    },

    getStats() {
      return {
        count,
        lastUpdate,
        error: lastError,
        loading: false,
      };
    },
  };

  return layer;
}

const groundviewLayer = createGroundViewLayer();
export default groundviewLayer;
export { createGroundViewLayer };

import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';

function emptyState() {
  return {
    observed: { events: [], observations: [] },
    derived: {},
    inferred: {},
    config: { snapshots: [], receivers: [], links: [], cameras: [] },
    camera_observations: [],
    visual_identities: [],
    bindings: [],
    experiments: [],
    heartbeats: [],
    quarantine: [],
    health: {},
  };
}

export function createGroundViewStore({
  rootDir,
  persist = process.env.VERCEL ? false : true,
} = {}) {
  let state = emptyState();
  const file = rootDir ? path.join(rootDir, 'state.json') : null;

  async function load() {
    if (!persist || !file) return state;
    try {
      state = JSON.parse(await readFile(file, 'utf8'));
    } catch {
      state = emptyState();
    }
    return state;
  }

  async function save() {
    if (!persist || !file) return;
    await mkdir(path.dirname(file), { recursive: true });
    await writeFile(file, `${JSON.stringify(state)}\n`);
  }

  return {
    async read() {
      await load();
      return state;
    },
    async write(mutator) {
      await load();
      mutator(state);
      await save();
      return state;
    },
    async replaceDerived(key, records) {
      await load();
      state.derived[key] = records;
      await save();
      return state;
    },
    async replaceInferred(key, records) {
      await load();
      state.inferred[key] = records;
      await save();
      return state;
    },
    async deleteDerivedAndInferred() {
      await load();
      state.derived = {};
      state.inferred = {};
      state.bindings = state.bindings || [];
      await save();
      return state;
    },
    emptyState,
  };
}

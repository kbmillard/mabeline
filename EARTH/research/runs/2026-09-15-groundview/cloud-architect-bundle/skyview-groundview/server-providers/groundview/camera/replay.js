export async function replayCameraFixture(engine, observations = []) {
  for (const observation of observations) await engine.ingestCamera(observation);
  return engine.snapshot();
}

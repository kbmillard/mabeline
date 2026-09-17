import { normalizeEvent } from '../rf/normalizeEvent.js';
import { adaptReceiverNodeEnvelope } from '../normalize.js';

/** Federation never owns a second normalizer. */
export function ingestFederatedEnvelope(body, defaults = {}) {
  return normalizeEvent(adaptReceiverNodeEnvelope(body, defaults));
}

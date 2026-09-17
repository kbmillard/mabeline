import { createGroundViewEngine } from './groundview/engine.js';
import { createGroundViewHttp } from './groundview/http.js';

export function groundviewProxy() {
  const engine = createGroundViewEngine();
  const middleware = createGroundViewHttp(engine);
  const install = (server) => {
    server.middlewares.use('/api/groundview', middleware);
  };
  return {
    name: 'groundview-proxy',
    configureServer: install,
    configurePreviewServer: install,
  };
}

export { createGroundViewEngine, createGroundViewHttp };

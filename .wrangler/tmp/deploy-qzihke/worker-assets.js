// worker-assets.js
var worker_assets_default = {
  async fetch(request, env) {
    return env.ASSETS.fetch(request);
  }
};
export {
  worker_assets_default as default
};
//# sourceMappingURL=worker-assets.js.map

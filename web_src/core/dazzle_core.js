/**
 * DazzleNodes Core Library
 *
 * Provides utilities for ComfyUI custom nodes with automatic depth detection
 * for compatibility between standalone nodes and DazzleNodes collection.
 *
 * Version: 0.2.0
 */

/**
 * Calculate import path depth based on current URL
 * Works for any nesting level: standalone, DazzleNodes, or other contexts
 *
 * @returns {string} Path prefix like "../../../" based on current depth
 */
function calculateImportDepth() {
    const currentPath = import.meta.url;
    const urlParts = new URL(currentPath).pathname.split('/').filter(p => p);
    // Each part requires one ../ to traverse up (including filename)
    const depth = urlParts.length;
    return '../'.repeat(depth);
}

/**
 * Import ComfyUI core modules with automatic path detection
 *
 * Usage:
 *   const { app, ComfyWidgets } = await DazzleNodesCore.importComfyModules('app', 'widgets');
 *
 * @param {...string} modules - Module names ('app', 'widgets', 'api', etc.)
 * @returns {Promise<Object>} Object with imported modules
 */
async function importComfyModules(...modules) {
    const prefix = calculateImportDepth();
    const imports = {};

    for (const moduleName of modules) {
        const module = await import(`${prefix}scripts/${moduleName}.js`);
        // Extract named exports (e.g., { app } from app.js)
        Object.assign(imports, module);
    }

    return imports;
}

/**
 * Import a single ComfyUI module
 *
 * Usage:
 *   const app = await DazzleNodesCore.importComfyModule('app');
 *
 * @param {string} moduleName - Module name ('app', 'widgets', 'api', etc.)
 * @returns {Promise<Object>} The module's default or named exports
 */
async function importComfyModule(moduleName) {
    const prefix = calculateImportDepth();
    return await import(`${prefix}scripts/${moduleName}.js`);
}

// Initialize and register extension
(async function() {
    console.log("[DazzleNodes] Core library loading...");
    console.log("[DazzleNodes] Version: 0.2.0");

    try {
        // Import ComfyUI app module using our helper
        const { app } = await importComfyModules('app');

        // Register extension
        app.registerExtension({
            name: "DazzleNodes.CoreLibrary",

            async init() {
                console.log("[DazzleNodes] Core library initialized");
                console.log("[DazzleNodes] Ready for custom nodes");
            },

            async setup() {
                console.log("[DazzleNodes] Core library setup complete");
            }
        });

        console.log("[DazzleNodes] Core library loaded successfully!");
    } catch (error) {
        console.error("[DazzleNodes] Failed to load core library:", error);
    }
})();

// Export utilities to window for use by other nodes
window.DazzleNodesCore = {
    version: "0.2.0",
    loaded: true,
    timestamp: new Date().toISOString(),

    // Export helper functions
    calculateImportDepth,
    importComfyModules,
    importComfyModule,

    /**
     * Quick helper for common case: importing app and ComfyWidgets
     *
     * Usage:
     *   const { app, ComfyWidgets } = await window.DazzleNodesCore.importComfyCore();
     */
    importComfyCore: async function() {
        return await importComfyModules('app', 'widgets');
    }
};

console.log("[DazzleNodes] Core utilities available at window.DazzleNodesCore");

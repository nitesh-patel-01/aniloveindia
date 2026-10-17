# Optional AniLove 3D logo

Three.js 0.180.0 (MIT); bundled from scripts/logo-scene.js using esbuild 0.25.11, --bundle --format=esm --minify --legal-comments=inline. Install the pinned tools in a temporary build directory, copy scripts/logo-scene.js there, and emit assets/vendor/anilove-scene.js. THREE-LICENSE.txt retains the upstream license. No package installation or runtime CDN is needed during deployment.

Only the homepage loads assets/logo-3d.js (783 bytes). It imports the self-hosted bundle after explicit activation. No preload or automatic engine fetch. Canvas area is fixed; pixel ratio is 1, shadows and antialiasing are disabled. Animation is capped at 20fps for eight seconds, paused offscreen and when hidden, and disabled for reduced motion. Close releases geometry, textures and WebGL context. Unsupported WebGL retains the static logo. Lighthouse and real-user Core Web Vitals are not guaranteed by these safeguards.

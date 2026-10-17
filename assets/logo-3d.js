// Opt-in only: no renderer, engine import or animation before a visitor activates it.
const button = document.querySelector('[data-logo-3d]');
if (button) {
  let stop;
  button.addEventListener('click', async () => {
    if (stop) { button.closest('.logo-experience').classList.remove('is-active'); stop(); stop = null; button.textContent = 'View logo in 3D'; button.setAttribute('aria-pressed', 'false'); return; }
    button.disabled = true;
    button.textContent = 'Loading 3D…';
    try {
      const { start } = await import('./vendor/anilove-scene.js');
      stop = start(document.querySelector('[data-logo-stage]'));
      button.closest('.logo-experience').classList.add('is-active');
      button.textContent = 'Close 3D logo';
      button.setAttribute('aria-pressed', 'true');
    } catch {
      button.textContent = '3D unavailable — try again';
    } finally { button.disabled = false; }
  });
}

/* Only this visual preference is stored in the browser; never vault data. */
(() => {
  let theme = 'dark';
  try { const saved = localStorage.getItem('kagnode-theme'); if (['light', 'dark'].includes(saved)) theme = saved; } catch {}
  function apply(value) {
    document.documentElement.dataset.theme = value;
    document.querySelector('meta[name="theme-color"]').content = value === 'light' ? '#fcfcfd' : '#101010';
    document.querySelectorAll('.theme-toggle').forEach(button => {
      button.setAttribute('aria-label', `Switch to ${value === 'dark' ? 'light' : 'dark'} theme`);
      button.setAttribute('aria-pressed', String(value === 'light'));
    });
  }
  apply(theme);
  document.addEventListener('DOMContentLoaded', () => {
    apply(theme);
    document.querySelectorAll('.theme-toggle').forEach(button => button.addEventListener('click', () => {
      theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
      apply(theme); try { localStorage.setItem('kagnode-theme', theme); } catch {}
    }));
  });
})();

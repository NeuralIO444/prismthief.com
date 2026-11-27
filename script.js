// Prism Thief — gallery lightbox (arrows + Esc) and service worker
(function () {
  var box = document.getElementById('lightbox');
  var img = document.getElementById('lightbox-img');
  var cap = document.getElementById('lightbox-cap');
  var closeBtn = box ? box.querySelector('.lightbox-close') : null;
  var figs = box ? Array.prototype.slice.call(document.querySelectorAll('.grid figure')) : [];
  var current = -1;
  var lastFocused = null;

  function show(i) {
    if (!figs.length) return;
    if (i < 0) i = figs.length - 1;
    if (i >= figs.length) i = 0;
    current = i;
    var pic = figs[i].querySelector('img');
    var caption = figs[i].querySelector('figcaption');
    img.src = pic.currentSrc || pic.src;
    img.alt = pic.alt;
    cap.textContent = caption ? caption.textContent : pic.alt;
  }

  function open(i) {
    lastFocused = document.activeElement;
    show(i);
    box.hidden = false;
    document.body.style.overflow = 'hidden';
    if (closeBtn) closeBtn.focus();
  }

  function close() {
    box.hidden = true;
    img.src = '';
    document.body.style.overflow = '';
    if (lastFocused && lastFocused.focus) lastFocused.focus();
  }

  if (box && img) {
    figs.forEach(function (fig, i) {
      fig.addEventListener('click', function () { open(i); });
    });

    // Close on backdrop click or the close button — not on the photo itself.
    box.addEventListener('click', function (e) {
      if (e.target === box) close();
    });
    if (closeBtn) closeBtn.addEventListener('click', close);
    document.addEventListener('keydown', function (e) {
      if (box.hidden) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowRight') show(current + 1);
      if (e.key === 'ArrowLeft') show(current - 1);
    });
  }

  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('sw.js').catch(function () { /* offline is a bonus, never an error */ });
    });
  }
})();

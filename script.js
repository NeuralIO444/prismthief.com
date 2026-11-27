// Prism Thief — gallery lightbox
(function () {
  var box = document.getElementById('lightbox');
  var img = document.getElementById('lightbox-img');
  var cap = document.getElementById('lightbox-cap');
  var closeBtn = box ? box.querySelector('.lightbox-close') : null;
  if (!box || !img) return;

  var lastFocused = null;

  document.querySelectorAll('.grid figure').forEach(function (fig) {
    fig.addEventListener('click', function () {
      var pic = fig.querySelector('img');
      var caption = fig.querySelector('figcaption');
      lastFocused = document.activeElement;
      img.src = pic.currentSrc || pic.src;
      img.alt = pic.alt;
      cap.textContent = caption ? caption.textContent : pic.alt;
      box.hidden = false;
      document.body.style.overflow = 'hidden';
      if (closeBtn) closeBtn.focus();
    });
  });

  function close() {
    box.hidden = true;
    img.src = '';
    document.body.style.overflow = '';
    if (lastFocused && lastFocused.focus) lastFocused.focus();
  }

  // Close on backdrop click or the close button — not on the photo itself.
  box.addEventListener('click', function (e) {
    if (e.target === box) close();
  });
  if (closeBtn) closeBtn.addEventListener('click', close);
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !box.hidden) close();
  });
})();

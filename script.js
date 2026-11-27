// Prism Thief — gallery lightbox
(function () {
  var box = document.getElementById('lightbox');
  var img = document.getElementById('lightbox-img');
  var cap = document.getElementById('lightbox-cap');
  if (!box || !img) return;

  document.querySelectorAll('.grid figure').forEach(function (fig) {
    fig.addEventListener('click', function () {
      var pic = fig.querySelector('img');
      var caption = fig.querySelector('figcaption');
      img.src = pic.src;
      img.alt = pic.alt;
      cap.textContent = caption ? caption.textContent : pic.alt;
      box.hidden = false;
      document.body.style.overflow = 'hidden';
    });
  });

  function close() {
    box.hidden = true;
    img.src = '';
    document.body.style.overflow = '';
  }

  box.addEventListener('click', close);
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !box.hidden) close();
  });
})();

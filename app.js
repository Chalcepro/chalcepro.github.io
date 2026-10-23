  // fancy animation — snappy easing, no scale
  AOS.init({
    duration: 700,
    once: true,
    easing: 'ease-out-quart'
  });


  // ── NAV: sticky + single center toggle ──
  const nav = document.getElementById('mainNav');
  const navExpandBtn = document.getElementById('navExpand');

  if (navExpandBtn) {
    navExpandBtn.addEventListener('click', () => {
      nav.classList.toggle('minimized');
    });
  }

  // Sticky nav on scroll WITHOUT auto-minimizing
  window.addEventListener('scroll', () => {
    const heroHeight = document.querySelector('.hero')?.offsetHeight || 100;
    if (window.scrollY > heroHeight - 100) {
      nav.classList.add('sticky');
    } else {
      nav.classList.remove('sticky');
    }
  });


//music player

/**
 * RoTEM Academy — English Landing Page Scripts
 */

(function () {
  'use strict';

  // --- Navbar scroll effect ---
  const navbar = document.getElementById('navbar');
  if (navbar) {
    window.addEventListener('scroll', function () {
      navbar.classList.toggle('scrolled', window.scrollY > 20);
    });
  }

  // --- Mobile nav toggle ---
  const toggle = document.querySelector('.nav-toggle');
  const navLinks = document.querySelector('.nav-links');
  if (toggle && navLinks) {
    toggle.addEventListener('click', function () {
      navLinks.classList.toggle('open');
    });
    navLinks.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        navLinks.classList.remove('open');
      });
    });
  }

  // --- Smooth scroll for anchor links ---
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      var target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // --- Simple particle background ---
  var canvas = document.getElementById('particles');
  if (canvas) {
    var parent = canvas.parentElement;
    var el = document.createElement('canvas');
    el.width = parent.offsetWidth;
    el.height = parent.offsetHeight;
    el.style.cssText = 'position:absolute;inset:0;width:100%;height:100%';
    canvas.appendChild(el);

    var ctx = el.getContext('2d');
    var dots = [];
    var count = Math.min(60, Math.floor(el.width / 20));

    for (var i = 0; i < count; i++) {
      dots.push({
        x: Math.random() * el.width,
        y: Math.random() * el.height,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        r: Math.random() * 2 + 1
      });
    }

    function animate() {
      ctx.clearRect(0, 0, el.width, el.height);
      dots.forEach(function (d) {
        d.x += d.vx;
        d.y += d.vy;
        if (d.x < 0 || d.x > el.width) d.vx *= -1;
        if (d.y < 0 || d.y > el.height) d.vy *= -1;
        ctx.beginPath();
        ctx.arc(d.x, d.y, d.r, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(255,255,255,0.5)';
        ctx.fill();
      });
      // Draw connections
      for (var i = 0; i < dots.length; i++) {
        for (var j = i + 1; j < dots.length; j++) {
          var dx = dots[i].x - dots[j].x;
          var dy = dots[i].y - dots[j].y;
          var dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 120) {
            ctx.beginPath();
            ctx.moveTo(dots[i].x, dots[i].y);
            ctx.lineTo(dots[j].x, dots[j].y);
            ctx.strokeStyle = 'rgba(255,255,255,' + (1 - dist / 120) * 0.2 + ')';
            ctx.stroke();
          }
        }
      }
      requestAnimationFrame(animate);
    }
    animate();

    window.addEventListener('resize', function () {
      el.width = parent.offsetWidth;
      el.height = parent.offsetHeight;
    });
  }

  // --- Contact form handler ---
  var form = document.getElementById('contactForm');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var btn = form.querySelector('button[type="submit"]');
      var originalText = btn.innerHTML;

      btn.disabled = true;
      btn.innerHTML = 'Sending...';

      var data = new FormData(form);
      fetch(form.action, {
        method: 'POST',
        body: data
      })
        .then(function (res) {
          if (res.ok) {
            btn.innerHTML = 'Sent! We\'ll be in touch.';
            btn.style.background = '#10b981';
            btn.style.borderColor = '#10b981';
            form.reset();
          } else {
            throw new Error('Server error');
          }
        })
        .catch(function () {
          btn.innerHTML = 'Error — please email us directly';
          btn.style.background = '#ef4444';
          btn.style.borderColor = '#ef4444';
        })
        .finally(function () {
          setTimeout(function () {
            btn.disabled = false;
            btn.innerHTML = originalText;
            btn.style.background = '';
            btn.style.borderColor = '';
          }, 4000);
        });
    });
  }

  // --- Intersection Observer for fade-in animations ---
  var sections = document.querySelectorAll('.section');
  if ('IntersectionObserver' in window) {
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
          }
        });
      },
      { threshold: 0.1 }
    );
    sections.forEach(function (s) {
      s.classList.add('fade-in');
      observer.observe(s);
    });

    // Add fade-in CSS dynamically
    var style = document.createElement('style');
    style.textContent =
      '.fade-in{opacity:0;transform:translateY(20px);transition:opacity 0.6s ease,transform 0.6s ease}' +
      '.fade-in.visible{opacity:1;transform:translateY(0)}';
    document.head.appendChild(style);
  }
})();

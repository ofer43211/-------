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

  // --- Pulse Check Widget ---
  (function initPulse() {
    var canvas = document.getElementById('pulseCanvas');
    var startBtn = document.getElementById('pulseStartBtn');
    var insightText = document.getElementById('pulseInsightText');
    var widget = document.getElementById('pulseWidget');
    var leadGate = document.getElementById('pulseLeadGate');
    var leadForm = document.getElementById('pulseLeadForm');
    if (!canvas || !startBtn) return;

    var ctx = canvas.getContext('2d');
    var W = canvas.width;
    var H = canvas.height;
    var running = false;
    var startTime = 0;
    var elapsed = 0;
    var SCAN_DURATION = 12000; // 12 seconds
    var mouseActivity = 0; // 0-1 intensity from mouse/key input
    var decayTimer = null;
    var animFrame = null;

    // Nitzutz insight messages at different time offsets
    var insights = [
      { at: 3000, text: 'Detecting initial neural baseline\u2026 cognitive pattern forming.' },
      { at: 6000, text: 'I see a <strong>focused attention pattern</strong> with rhythmic micro-adjustments \u2014 characteristic of an analytical mind.' },
      { at: 9000, text: 'Cognitive alignment at <strong>~' + (68 + Math.floor(Math.random() * 14)) + '%</strong>. This is the zone where clinical learning peaks.' },
      { at: 12000, text: 'Scan complete. Your Neural Signature is ready. Enter your email below to receive the full analysis.' }
    ];
    var insightIdx = 0;

    // Track mouse movement intensity
    function onMouseMove() {
      if (!running) return;
      mouseActivity = Math.min(1, mouseActivity + 0.08);
    }
    function onKeyDown() {
      if (!running) return;
      mouseActivity = Math.min(1, mouseActivity + 0.12);
    }

    // Decay mouse activity over time
    function decay() {
      mouseActivity *= 0.95;
      if (mouseActivity < 0.01) mouseActivity = 0;
    }

    // Draw a single frame
    function drawWaveform(t) {
      ctx.clearRect(0, 0, W, H);

      // Base frequency modulated by time and activity
      var baseFreq = 0.02 + mouseActivity * 0.015;
      var amp = 30 + mouseActivity * 40;
      var midY = H / 2;
      var speed = t * 0.002;

      // Draw 3 layered waves
      var layers = [
        { color: 'rgba(96,165,250,0.6)', freqMul: 1, ampMul: 1, phase: 0 },
        { color: 'rgba(52,211,153,0.5)', freqMul: 1.5, ampMul: 0.6, phase: 2 },
        { color: 'rgba(167,139,250,0.35)', freqMul: 0.7, ampMul: 0.8, phase: 4 }
      ];

      layers.forEach(function (layer) {
        ctx.beginPath();
        for (var x = 0; x <= W; x++) {
          var y =
            midY +
            Math.sin((x * baseFreq * layer.freqMul) + speed + layer.phase) * amp * layer.ampMul +
            Math.sin((x * baseFreq * 2.3) + speed * 1.4) * amp * 0.2 * mouseActivity;
          if (x === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        ctx.strokeStyle = layer.color;
        ctx.lineWidth = 2;
        ctx.stroke();
      });

      // Progress bar at bottom
      var progress = Math.min(1, elapsed / SCAN_DURATION);
      ctx.fillStyle = 'rgba(16,185,129,0.3)';
      ctx.fillRect(0, H - 4, W * progress, 4);
    }

    function tick() {
      elapsed = Date.now() - startTime;
      decay();
      drawWaveform(elapsed);

      // Show insights at timed intervals
      if (insightIdx < insights.length && elapsed >= insights[insightIdx].at) {
        insightText.innerHTML = insights[insightIdx].text;
        insightIdx++;
      }

      if (elapsed < SCAN_DURATION) {
        animFrame = requestAnimationFrame(tick);
      } else {
        // Scan complete — show lead gate
        running = false;
        widget.classList.remove('active');
        startBtn.style.display = 'none';
        if (leadGate) leadGate.style.display = 'block';
      }
    }

    startBtn.addEventListener('click', function () {
      if (running) return;
      running = true;
      startTime = Date.now();
      elapsed = 0;
      insightIdx = 0;
      mouseActivity = 0;
      widget.classList.add('active');
      startBtn.disabled = true;
      startBtn.innerHTML = 'Scanning\u2026';
      insightText.innerHTML = 'Initialising neural scan\u2026';

      document.addEventListener('mousemove', onMouseMove);
      document.addEventListener('keydown', onKeyDown);

      tick();
    });

    // Lead capture form
    if (leadForm) {
      leadForm.addEventListener('submit', function (e) {
        e.preventDefault();
        var email = document.getElementById('pulseEmail').value;
        var btn = leadForm.querySelector('button');
        btn.disabled = true;
        btn.innerHTML = 'Sending\u2026';

        fetch('/api/contact', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: 'email=' + encodeURIComponent(email) + '&interest=pulse-check&name=Pulse+Lead'
        })
          .then(function (res) {
            if (res.ok) {
              leadGate.innerHTML =
                '<p style="color:#34d399;font-weight:600;">Your Neural Signature report will arrive shortly.</p>';
            } else {
              throw new Error('fail');
            }
          })
          .catch(function () {
            btn.disabled = false;
            btn.innerHTML = 'Get My Report';
            insightText.innerHTML = 'Something went wrong \u2014 please try again or email us directly.';
          });
      });
    }
  })();

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

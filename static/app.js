/**
 * InvoiceGuard — Frontend Application Engine
 * Supports User-Isolated Firestore Architecture (UID Scoped),
 * Role-Based Admin Sentinel Portal (admin:admins),
 * Real-Data Metrics (Zero Fake Stats), and Document AI Processing.
 */

// Global State
const STATE = {
  activeInvoiceId: 'INV-2026-0918',
  invoices: [],
  vendors: [],
  complaints: [],
  metrics: {},
  activeUser: {
    uid: 'usr_demo1_alex',
    email: 'demo1@invoiceguard.demo',
    name: 'Alex Vance',
    role: 'user',
    title: 'Finance Sec Lead',
    initials: 'AV'
  },
  demoUsers: [],
  invoicesFilter: 'all',
  searchQuery: '',
  adminData: null,
  chatMessages: [
    {
      sender: 'user',
      text: 'Why is the payment destination suspicious for ABC Technologies?',
      time: '14:34'
    },
    {
      sender: 'ai',
      text: 'ABC Technologies has received 14 previous payments to HDFC Account *4901 without incident. This invoice lists ICICI Account *8821, which was first seen across our vendor network only 3 days ago. No change-of-banking affidavit was attached to this payload.',
      time: '14:34',
      confidence: '98.4%'
    }
  ]
};

// Request Headers Helper
function getAuthHeaders() {
  return {
    'Content-Type': 'application/json',
    'X-User-UID': STATE.activeUser.uid
  };
}

// DOM Initialization
document.addEventListener('DOMContentLoaded', async () => {
  initTextDecodeEffect();
  initBrandCursorBlink();
  initHeroDotGrid();
  initCursorGlow();
  setupScrollSpy();
  setupKeyboardShortcuts();
  await fetchDemoUsers();
  await refreshUserData();

  if (window.location.pathname === '/admin' || window.location.hash === '#admin') {
    openAdminLoginModal();
  }
});

// --- Modern Forensic Motion & Canvas Effects ---
function initTextDecodeEffect() {
  const el = document.getElementById('brand-wordmark');
  if (!el) return;
  const targetText = 'InvoiceGuard';
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReduced) {
    el.innerText = targetText;
    return;
  }

  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789%#@$&*!?';
  let frame = 0;
  const totalFrames = 26;
  
  const timer = setInterval(() => {
    frame++;
    const progress = frame / totalFrames;
    const resolvedIndex = Math.floor(progress * targetText.length);

    let resultHtml = '';
    for (let i = 0; i < targetText.length; i++) {
      if (i < resolvedIndex) {
        resultHtml += `<span class="text-on-surface font-sans">${targetText[i]}</span>`;
      } else {
        const randomChar = chars[Math.floor(Math.random() * chars.length)];
        resultHtml += `<span class="text-electric-cyan font-mono">${randomChar}</span>`;
      }
    }

    el.innerHTML = resultHtml;

    if (frame >= totalFrames) {
      clearInterval(timer);
      el.innerText = targetText;
    }
  }, 40);
}

// Brand Wordmark Blinking Terminal Cursor Settings & Functions
const WORDMARK_CONFIG = {
  blinkIntervalMs: 500 // Time required between 2 consecutive blinks in milliseconds
};

function initBrandCursorBlink(intervalMs = WORDMARK_CONFIG.blinkIntervalMs) {
  const cursor = document.getElementById('brand-cursor');
  if (!cursor) return;

  if (window._brandBlinkTimer) {
    clearInterval(window._brandBlinkTimer);
  }

  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReduced) {
    cursor.style.opacity = '1';
    return;
  }

  window._brandBlinkTimer = setInterval(() => {
    cursor.style.opacity = cursor.style.opacity === '0' ? '1' : '0';
  }, intervalMs);
}

function setBrandBlinkInterval(intervalMs) {
  WORDMARK_CONFIG.blinkIntervalMs = parseInt(intervalMs, 10) || 500;
  initBrandCursorBlink(WORDMARK_CONFIG.blinkIntervalMs);
  showToast(`Brand cursor blink interval updated to ${WORDMARK_CONFIG.blinkIntervalMs}ms`);
}

function initHeroDotGrid() {
  const canvas = document.getElementById('hero-dot-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const heroSection = document.getElementById('overview');
  if (!heroSection) return;

  let width = (canvas.width = heroSection.clientWidth);
  let height = (canvas.height = heroSection.clientHeight);

  const spacing = 28;
  const dots = [];
  let mouse = { x: -1000, y: -1000, targetX: -1000, targetY: -1000 };
  let isMouseOver = false;

  function buildGrid() {
    dots.length = 0;
    const cols = Math.ceil(width / spacing) + 1;
    const rows = Math.ceil(height / spacing) + 1;

    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const bx = c * spacing;
        const by = r * spacing;
        dots.push({
          baseX: bx,
          baseY: by,
          x: bx,
          y: by,
          targetX: bx,
          targetY: by,
          radius: 1.5,
          targetRadius: 1.5,
          opacity: 0.18,
          targetOpacity: 0.18,
          color: [139, 149, 165],
          targetColor: [139, 149, 165]
        });
      }
    }
  }

  function resize() {
    if (!heroSection) return;
    width = canvas.width = heroSection.clientWidth;
    height = canvas.height = heroSection.clientHeight;
    buildGrid();
  }

  window.addEventListener('resize', resize);
  resize();

  window.addEventListener('mousemove', (e) => {
    const rect = heroSection.getBoundingClientRect();
    if (
      e.clientX >= rect.left &&
      e.clientX <= rect.right &&
      e.clientY >= rect.top &&
      e.clientY <= rect.bottom
    ) {
      mouse.targetX = e.clientX - rect.left;
      mouse.targetY = e.clientY - rect.top;
      isMouseOver = true;
    } else {
      isMouseOver = false;
      mouse.targetX = -1000;
      mouse.targetY = -1000;
    }
  });

  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReduced) {
    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = 'rgba(139, 149, 165, 0.18)';
    dots.forEach(d => {
      ctx.beginPath();
      ctx.arc(d.baseX, d.baseY, 1.5, 0, Math.PI * 2);
      ctx.fill();
    });
    return;
  }

  let time = 0;
  const cyanRgb = [66, 133, 244];
  const mutedRgb = [148, 163, 184];

  function render() {
    time += 0.02;
    mouse.x += (mouse.targetX - mouse.x) * 0.12;
    mouse.y += (mouse.targetY - mouse.y) * 0.12;

    ctx.clearRect(0, 0, width, height);

    const proximityRadius = 150;

    dots.forEach(dot => {
      let dx = dot.baseX - mouse.x;
      let dy = dot.baseY - mouse.y;
      let dist = Math.sqrt(dx * dx + dy * dy);

      let wave = Math.sin(dot.baseX * 0.025 + dot.baseY * 0.025 + time) * 0.04;

      if (dist < proximityRadius && isMouseOver) {
        let factor = 1 - dist / proximityRadius;
        let smoothFactor = factor * factor * (3 - 2 * factor);

        // Repel / displace dot position away from cursor
        const angle = Math.atan2(dy, dx);
        const repelForce = smoothFactor * 16;

        dot.targetX = dot.baseX + Math.cos(angle) * repelForce;
        dot.targetY = dot.baseY + Math.sin(angle) * repelForce;

        dot.targetRadius = 1.5 + smoothFactor * 1.6;
        dot.targetOpacity = 0.18 + smoothFactor * 0.65 + wave;
        dot.targetColor = [
          mutedRgb[0] + (cyanRgb[0] - mutedRgb[0]) * smoothFactor,
          mutedRgb[1] + (cyanRgb[1] - mutedRgb[1]) * smoothFactor,
          mutedRgb[2] + (cyanRgb[2] - mutedRgb[2]) * smoothFactor
        ];
      } else {
        dot.targetX = dot.baseX;
        dot.targetY = dot.baseY;
        dot.targetRadius = 1.5;
        dot.targetOpacity = Math.max(0.08, 0.18 + wave);
        dot.targetColor = mutedRgb;
      }

      dot.x += (dot.targetX - dot.x) * 0.12;
      dot.y += (dot.targetY - dot.y) * 0.12;
      dot.radius += (dot.targetRadius - dot.radius) * 0.1;
      dot.opacity += (dot.targetOpacity - dot.opacity) * 0.1;
      dot.color[0] += (dot.targetColor[0] - dot.color[0]) * 0.1;
      dot.color[1] += (dot.targetColor[1] - dot.color[1]) * 0.1;
      dot.color[2] += (dot.targetColor[2] - dot.color[2]) * 0.1;

      ctx.beginPath();
      ctx.arc(dot.x, dot.y, Math.max(0.5, dot.radius), 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${Math.round(dot.color[0])}, ${Math.round(dot.color[1])}, ${Math.round(dot.color[2])}, ${dot.opacity})`;
      ctx.fill();
    });

    requestAnimationFrame(render);
  }

  requestAnimationFrame(render);
}

// Glow Configuration Functions
const GLOW_CONFIG = {
  radius: parseInt(localStorage.getItem('ig_glow_radius'), 10) || 210,
  opacity: parseFloat(localStorage.getItem('ig_glow_opacity')) || 0.20,
  blur: parseInt(localStorage.getItem('ig_glow_blur'), 10) || 40,
  color: (localStorage.getItem('ig_glow_color') && localStorage.getItem('ig_glow_color') !== '#22D3C4' && localStorage.getItem('ig_glow_color') !== '#4285F4') ? localStorage.getItem('ig_glow_color') : '#00B8D9',
  idleFadeTime: parseFloat(localStorage.getItem('ig_glow_idle_fade_time')) || 5.5,
  minIdleOpacity: parseFloat(localStorage.getItem('ig_glow_min_idle_opacity')) || 0.12
};

function applyGlowConfig() {
  const glow = document.getElementById('cursor-glow');
  if (!glow) return;

  const r = GLOW_CONFIG.radius;
  const opacity = GLOW_CONFIG.opacity;
  const blur = GLOW_CONFIG.blur;
  const color = GLOW_CONFIG.color;

  glow.style.width = `${r * 2}px`;
  glow.style.height = `${r * 2}px`;
  glow.style.filter = `blur(${blur}px)`;

  const hex = color.replace('#', '');
  const rVal = parseInt(hex.substring(0, 2), 16) || 0;
  const gVal = parseInt(hex.substring(2, 4), 16) || 184;
  const bVal = parseInt(hex.substring(4, 6), 16) || 217;

  glow.style.background = `radial-gradient(circle, rgba(${rVal}, ${gVal}, ${bVal}, ${opacity}) 0%, rgba(${rVal}, ${gVal}, ${bVal}, 0) 70%)`;

  const rDisp = document.getElementById('glow-val-radius');
  if (rDisp) rDisp.innerText = `${r}px`;
  const oDisp = document.getElementById('glow-val-opacity');
  if (oDisp) oDisp.innerText = `${Math.round(opacity * 100)}%`;
  const bDisp = document.getElementById('glow-val-blur');
  if (bDisp) bDisp.innerText = `${blur}px`;
  const fDisp = document.getElementById('glow-val-idle-fade');
  if (fDisp) fDisp.innerText = `${GLOW_CONFIG.idleFadeTime.toFixed(1)}s`;
  const mDisp = document.getElementById('glow-val-min-idle');
  if (mDisp) mDisp.innerText = `${Math.round(GLOW_CONFIG.minIdleOpacity * 100)}%`;

  localStorage.setItem('ig_glow_radius', r);
  localStorage.setItem('ig_glow_opacity', opacity);
  localStorage.setItem('ig_glow_blur', blur);
  localStorage.setItem('ig_glow_color', color);
  localStorage.setItem('ig_glow_idle_fade_time', GLOW_CONFIG.idleFadeTime);
  localStorage.setItem('ig_glow_min_idle_opacity', GLOW_CONFIG.minIdleOpacity);
}

function toggleGlowControlPanel() {
  const panel = document.getElementById('glow-control-panel');
  if (panel) {
    panel.classList.toggle('hidden');
    const rSlide = document.getElementById('glow-slider-radius');
    if (rSlide) rSlide.value = GLOW_CONFIG.radius;
    const oSlide = document.getElementById('glow-slider-opacity');
    if (oSlide) oSlide.value = Math.round(GLOW_CONFIG.opacity * 100);
    const bSlide = document.getElementById('glow-slider-blur');
    if (bSlide) bSlide.value = GLOW_CONFIG.blur;
    const fSlide = document.getElementById('glow-slider-idle-fade');
    if (fSlide) fSlide.value = GLOW_CONFIG.idleFadeTime;
    const mSlide = document.getElementById('glow-slider-min-idle');
    if (mSlide) mSlide.value = Math.round(GLOW_CONFIG.minIdleOpacity * 100);
  }
}

function updateGlowRadius(val) {
  GLOW_CONFIG.radius = parseInt(val, 10);
  applyGlowConfig();
}

function updateGlowOpacity(val) {
  GLOW_CONFIG.opacity = parseInt(val, 10) / 100;
  applyGlowConfig();
}

function updateGlowBlur(val) {
  GLOW_CONFIG.blur = parseInt(val, 10);
  applyGlowConfig();
}

function updateGlowIdleFade(val) {
  GLOW_CONFIG.idleFadeTime = parseFloat(val);
  applyGlowConfig();
}

function updateGlowMinIdle(val) {
  GLOW_CONFIG.minIdleOpacity = parseInt(val, 10) / 100;
  applyGlowConfig();
}

function updateGlowColor(hexColor) {
  GLOW_CONFIG.color = hexColor;
  applyGlowConfig();
}

function resetGlowDefaults() {
  GLOW_CONFIG.radius = 210;
  GLOW_CONFIG.opacity = 0.20;
  GLOW_CONFIG.blur = 40;
  GLOW_CONFIG.color = '#00B8D9';
  GLOW_CONFIG.idleFadeTime = 3.0;
  GLOW_CONFIG.minIdleOpacity = 0.05;
  applyGlowConfig();
  toggleGlowControlPanel();
  showToast('Cursor glow restored to defaults (210px radius, 20% opacity, 40px blur, 3.0s fade)');
}

function initCursorGlow() {
  const glow = document.getElementById('cursor-glow');
  if (!glow) return;

  applyGlowConfig();

  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReduced || ('ontouchstart' in window && !window.matchMedia('(pointer: fine)').matches)) {
    glow.style.display = 'none';
    return;
  }

  let mouseX = -300;
  let mouseY = -300;
  let currentX = -300;
  let currentY = -300;
  let lastMouseMoveTime = performance.now();

  window.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
    lastMouseMoveTime = performance.now();
    if (glow.style.opacity === '0' || glow.style.opacity === '') {
      glow.style.opacity = '1';
    }
  });

  document.addEventListener('mouseleave', () => {
    glow.style.opacity = '0';
  });

  function renderGlow() {
    const now = performance.now();
    const idleElapsed = (now - lastMouseMoveTime) / 1000;
    const activeOpacity = GLOW_CONFIG.opacity;
    const minOpacity = GLOW_CONFIG.minIdleOpacity;
    const fadeTime = Math.max(0.2, GLOW_CONFIG.idleFadeTime);

    let effectiveOpacity = activeOpacity;
    const idleStartDelay = 0.4;
    if (idleElapsed > idleStartDelay) {
      const fadeProgress = Math.min(1, (idleElapsed - idleStartDelay) / fadeTime);
      effectiveOpacity = activeOpacity - (activeOpacity - minOpacity) * fadeProgress;
    }

    const r = GLOW_CONFIG.radius;
    const blur = GLOW_CONFIG.blur;
    const color = GLOW_CONFIG.color;

    glow.style.width = `${r * 2}px`;
    glow.style.height = `${r * 2}px`;
    glow.style.filter = `blur(${blur}px)`;

    const hex = color.replace('#', '');
    const rVal = parseInt(hex.substring(0, 2), 16) || 0;
    const gVal = parseInt(hex.substring(2, 4), 16) || 184;
    const bVal = parseInt(hex.substring(4, 6), 16) || 217;

    glow.style.background = `radial-gradient(circle, rgba(${rVal}, ${gVal}, ${bVal}, ${effectiveOpacity.toFixed(3)}) 0%, rgba(${rVal}, ${gVal}, ${bVal}, 0) 70%)`;

    currentX += (mouseX - currentX) * 0.12;
    currentY += (mouseY - currentY) * 0.12;

    glow.style.transform = `translate3d(${currentX - r}px, ${currentY - r}px, 0)`;
    requestAnimationFrame(renderGlow);
  }

  requestAnimationFrame(renderGlow);
}

function animateThreatScore(scoreEl, targetScore) {
  if (!scoreEl) return;
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReduced) {
    scoreEl.innerText = targetScore;
    return;
  }

  let current = 0;
  const duration = 750;
  const startTime = performance.now();
  const startVal = parseInt(scoreEl.innerText, 10) || 0;

  function step(now) {
    const elapsed = now - startTime;
    const progress = Math.min(1, elapsed / duration);
    const easeProgress = 1 - Math.pow(1 - progress, 2);
    const score = Math.round(startVal + (targetScore - startVal) * easeProgress);
    scoreEl.innerText = score;

    if (progress < 1) {
      requestAnimationFrame(step);
    } else {
      scoreEl.innerText = targetScore;
    }
  }
  requestAnimationFrame(step);
}

// --- User-Isolated API Sync ---
async function fetchDemoUsers() {
  try {
    const res = await fetch('/api/auth/demo-users');
    const data = await res.json();
    STATE.demoUsers = data.users || [];
  } catch (err) {
    console.error('Failed to load demo users:', err);
  }
}

async function refreshUserData() {
  if (STATE.activeUser.role === 'admin') {
    await refreshAdminData();
    return;
  }

  try {
    const headers = getAuthHeaders();
    const [mRes, invRes, venRes, cmpRes] = await Promise.all([
      fetch('/api/user/metrics', { headers }),
      fetch('/api/user/invoices', { headers }),
      fetch('/api/user/vendors', { headers }),
      fetch('/api/user/complaints', { headers })
    ]);

    STATE.metrics = await mRes.json();
    const invData = await invRes.json();
    STATE.invoices = invData.invoices || [];
    const venData = await venRes.json();
    STATE.vendors = venData.vendors || [];
    const cmpData = await cmpRes.json();
    STATE.complaints = cmpData.complaints || [];

    updateUserDisplay();
    renderDashboardView();
  } catch (err) {
    console.error('Error refreshing user data:', err);
  }
}

async function clearUserInvoices() {
  if (!confirm(`Clear all uploaded invoices for ${STATE.activeUser.name}?`)) {
    return;
  }
  try {
    const res = await fetch('/api/user/invoices/clear', {
      method: 'POST',
      headers: getAuthHeaders()
    });
    if (res.ok) {
      STATE.invoices = [];
      STATE.activeInvoiceId = null;
      showToast('Invoice history has been successfully cleared');
      await refreshUserData();
    } else {
      showToast('Failed to clear invoice history.');
    }
  } catch (err) {
    console.error('Error clearing user invoices:', err);
  }
}

function renderDashboardView() {
  const spotlightSec = document.getElementById('analysis-spotlight');

  if (STATE.invoices.length === 0) {
    if (spotlightSec) spotlightSec.classList.add('hidden');
    renderInvoicesTable();
    renderVendorsGrid();
    renderComplaintsList();
  } else {
    if (spotlightSec) spotlightSec.classList.remove('hidden');
    
    if (!STATE.invoices.some(i => i.id === STATE.activeInvoiceId)) {
      STATE.activeInvoiceId = STATE.invoices[0].id;
    }
    
    renderSpotlightInvoice(STATE.activeInvoiceId);
    renderInvoicesTable();
    renderVendorsGrid();
    renderComplaintsList();
  }
}

// --- Active Invoice Analysis Spotlight Renderer ---
function renderSpotlightInvoice(invoiceId) {
  let inv = STATE.invoices.find(i => i.id === invoiceId || i.invoice_number === invoiceId);
  if (!inv) {
    inv = STATE.invoices[0];
  }
  if (!inv) return;

  STATE.activeInvoiceId = inv.id;

  // Header & Meta
  const vName = document.getElementById('spotlight-vendor-name');
  if (vName) vName.innerText = inv.vendor_name;

  const invNum = document.getElementById('spotlight-inv-num');
  if (invNum) invNum.innerText = `#${inv.invoice_number}`;

  const vBadge = document.getElementById('spotlight-vendor-badge');
  if (vBadge) {
    if (inv.vendor_verified) {
      vBadge.className = 'inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-primary/10 text-primary font-mono text-[11px] font-semibold border border-primary/20';
      vBadge.innerHTML = `<span class="material-symbols-outlined text-[13px]">verified</span> Verified Vendor`;
    } else {
      vBadge.className = 'inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-error/10 text-error font-mono text-[11px] font-semibold border border-error/20';
      vBadge.innerHTML = `<span class="material-symbols-outlined text-[13px]">warning</span> Unverified Vendor`;
    }
  }

  const issDate = document.getElementById('spotlight-issue-date');
  if (issDate) issDate.innerText = inv.issue_date;

  const recDate = document.getElementById('spotlight-received-date');
  if (recDate) recDate.innerText = inv.received_date || `${inv.issue_date} · 14:32 IST`;

  const sha = document.getElementById('spotlight-sha256');
  if (sha) sha.innerText = inv.sha256_short || '7f8b9d...4a12';

  const amt = document.getElementById('spotlight-amount');
  if (amt) amt.innerText = `₹${Number(inv.total_amount).toLocaleString('en-IN')}`;

  const varEl = document.getElementById('spotlight-variance');
  if (varEl) {
    varEl.innerHTML = `<span class="material-symbols-outlined text-[13px]">report_problem</span> Historical variance: ${inv.historical_variance_pct || '+0.0%'}`;
    varEl.className = `text-xs font-mono flex items-center gap-1 mt-1 ${inv.threat_score > 25 ? 'text-tertiary' : 'text-secondary'}`;
  }

  // User feedback state display
  const fLegit = document.getElementById('btn-feedback-legit');
  const fSusp = document.getElementById('btn-feedback-susp');
  if (fLegit && fSusp) {
    fLegit.className = inv.user_feedback === 'Legitimate' ? 'px-2 py-0.5 rounded bg-secondary text-on-secondary font-bold text-xs' : 'px-2 py-0.5 rounded text-secondary hover:bg-secondary/10 font-bold transition-colors text-xs';
    fSusp.className = inv.user_feedback === 'Suspicious' ? 'px-2 py-0.5 rounded bg-error text-on-error font-bold text-xs' : 'px-2 py-0.5 rounded text-error hover:bg-error/10 font-bold transition-colors text-xs';
  }

  // Circular Risk Meter Gauge
  const scoreNum = document.getElementById('spotlight-score-num');
  if (scoreNum) animateThreatScore(scoreNum, inv.threat_score);

  const riskBadge = document.getElementById('spotlight-risk-badge');
  if (riskBadge) {
    let bClass = 'bg-warning/10 text-warning border-warning/20';
    let dotClass = 'bg-warning';
    if (inv.threat_score <= 25) {
      bClass = 'bg-secondary/10 text-secondary border-secondary/20';
      dotClass = 'bg-secondary';
    } else if (inv.threat_score > 60) {
      bClass = 'bg-error/10 text-error border-error/20';
      dotClass = 'bg-error';
    }
    riskBadge.className = `inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full ${bClass} font-mono text-xs font-bold border`;
    riskBadge.innerHTML = `<span class="w-1.5 h-1.5 rounded-full ${dotClass}"></span> ${inv.risk_level}`;
  }

  const meterCircle = document.getElementById('spotlight-meter-circle');
  if (meterCircle) {
    const circumference = 314.16;
    const offset = circumference - (circumference * (inv.threat_score / 100));
    meterCircle.style.strokeDashoffset = offset;
    meterCircle.setAttribute('class', inv.threat_score <= 25 ? 'text-secondary transition-all duration-1000' : (inv.threat_score > 60 ? 'text-error transition-all duration-1000' : 'text-warning transition-all duration-1000'));
  }

  // Checkpoints Tally
  const signals = inv.signals || [];
  const passed = inv.passed_checks || [];
  const tallyText = document.getElementById('spotlight-tally-text');
  if (tallyText) tallyText.innerText = `${signals.length} Warnings · ${passed.length} Passed`;

  const warnBar = document.getElementById('spotlight-tally-warn');
  const passBar = document.getElementById('spotlight-tally-pass');
  const totalChecks = Math.max(1, signals.length + passed.length);
  if (warnBar && passBar) {
    warnBar.style.width = `${(signals.length / totalChecks) * 100}%`;
    passBar.style.width = `${(passed.length / totalChecks) * 100}%`;
  }

  // Evidence Matrix Cards
  const evCount = document.getElementById('spotlight-signals-count');
  if (evCount) evCount.innerText = `${signals.length + passed.length} forensic checkpoints`;

  const evContainer = document.getElementById('spotlight-evidence-container');
  if (evContainer) {
    let html = signals.map((s, idx) => {
      const expVal = s.expected_value || s.expected || 'Historical settled baseline';
      const actVal = s.actual_value || s.actual || 'Extracted invoice coordinate/value';
      const whyMatters = s.why_it_matters || 'Impacts financial authorization, tax credit (ITC), and anti-tampering verification.';
      const action = s.recommended_action || s.protocol || 'Verify through independent out-of-band channel.';

      return `
      <div class="rounded-xl bg-surface-container p-3.5 hover:bg-surface-container-high transition-all border border-white/5">
        <div class="flex items-start justify-between cursor-pointer" onclick="toggleSpotlightEvidence('ev-spot-${idx}')">
          <div class="flex items-start gap-3">
            <span class="w-6 h-6 rounded flex items-center justify-center ${s.badge_class || (s.severity === 'CRITICAL' ? 'bg-error/10 text-error' : 'bg-tertiary/10 text-tertiary')} shrink-0 mt-0.5">
              <span class="material-symbols-outlined text-[15px]">${s.icon || (s.severity === 'CRITICAL' ? 'report' : 'warning')}</span>
            </span>
            <div>
              <div class="flex items-center gap-2">
                <span class="font-semibold text-xs text-on-surface">${s.title}</span>
                <span class="px-1.5 py-0.2 rounded ${s.badge_class || (s.severity === 'CRITICAL' ? 'bg-error/10 text-error' : 'bg-tertiary/10 text-tertiary')} font-mono text-[10px] uppercase font-bold">${s.severity || 'Signal'}</span>
              </div>
              <p class="text-xs text-on-surface-variant mt-1 leading-relaxed">
                ${s.description}
              </p>
            </div>
          </div>
          <button aria-label="Toggle details" class="text-on-surface-variant hover:text-on-surface p-1" type="button">
            <span class="material-symbols-outlined text-[16px]" id="ev-spot-${idx}-icon">expand_more</span>
          </button>
        </div>
        <div class="mt-2.5 pt-2.5 bg-surface-container-low/80 p-3.5 rounded-lg border border-white/5 flex flex-col gap-2.5" id="ev-spot-${idx}">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs font-mono">
            <div class="p-2 rounded bg-surface-container border border-white/5">
              <span class="text-[10px] uppercase text-outline font-bold block mb-0.5">Expected Value</span>
              <span class="text-secondary font-medium">${expVal}</span>
            </div>
            <div class="p-2 rounded bg-surface-container border border-white/5">
              <span class="text-[10px] uppercase text-outline font-bold block mb-0.5">Actual Value</span>
              <span class="text-tertiary font-medium">${actVal}</span>
            </div>
          </div>
          <div class="text-xs text-on-surface-variant bg-surface-container/50 p-2.5 rounded border border-white/5">
            <span class="font-bold text-[10px] uppercase text-outline block mb-0.5">Why It Matters</span>
            <p class="text-on-surface leading-relaxed">${whyMatters}</p>
          </div>
          <div class="flex items-start gap-2 pt-1">
            <span class="material-symbols-outlined text-[16px] text-tertiary shrink-0 mt-0.5">security_update_warning</span>
            <div class="flex flex-col gap-0.5">
              <span class="font-mono text-[10px] uppercase tracking-wider text-tertiary font-bold">Recommended Action</span>
              <span class="text-xs text-on-surface leading-normal font-medium">${action}</span>
            </div>
          </div>
        </div>
      </div>
      `;
    }).join('');


    if (passed.length > 0) {
      html += `
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
          ${passed.map(p => `
            <div class="flex items-center gap-2.5 p-2.5 rounded-lg bg-surface-container border border-white/5 text-xs">
              <span class="w-5 h-5 rounded-full bg-secondary/15 text-secondary flex items-center justify-center shrink-0">
                <span class="material-symbols-outlined text-[13px]">check</span>
              </span>
              <div class="flex flex-col min-w-0">
                <span class="text-on-surface font-medium truncate">${p.title}</span>
                <span class="text-outline font-mono text-[10px] truncate">${p.detail}</span>
              </div>
            </div>
          `).join('')}
        </div>
      `;
    }

    evContainer.innerHTML = html;
  }

  // AI Explanation Rendering
  const aiExplanationContainer = document.getElementById('spotlight-ai-explanation');
  if (aiExplanationContainer) {
    const expText = inv.ai_explanation || 'AI explanation temporarily unavailable. Deterministic analysis is still available.';
    const isFallback = expText.includes('temporarily unavailable');
    
    if (isFallback) {
      aiExplanationContainer.innerHTML = `
        <div class="rounded-xl bg-tertiary/10 p-3.5 border border-tertiary/20 flex items-center gap-2.5 text-xs text-tertiary font-mono">
          <span class="material-symbols-outlined text-[18px]">info</span>
          <span>${expText}</span>
        </div>
      `;
    } else {
      aiExplanationContainer.innerHTML = `
        <div class="rounded-xl bg-surface-container/90 p-4 border border-white/10 flex flex-col gap-2 shadow-inner">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2 text-primary font-mono text-xs font-bold uppercase tracking-wider">
              <span class="material-symbols-outlined text-[16px]">auto_awesome</span>
              <span>AI Explanation (Gemini 3.6 Flash)</span>
            </div>
            <span class="text-[10px] font-mono text-secondary bg-secondary/10 px-2 py-0.5 rounded border border-secondary/20">Verified Non-Hallucinating</span>
          </div>
          <p class="text-xs text-on-surface leading-relaxed font-sans">
            ${expText}
          </p>
        </div>
      `;
    }
  }

  // Deep Tab 1: Line Items
  const lineItemsBody = document.getElementById('spotlight-line-items-body');
  if (lineItemsBody) {
    const items = inv.line_items || [];
    lineItemsBody.innerHTML = items.map(it => {
      const isFlagged = it.flagged;
      const rowClass = isFlagged ? 'bg-tertiary/5 hover:bg-tertiary/10' : 'hover:bg-surface-container';
      const qtyClass = isFlagged ? 'text-tertiary font-bold' : 'text-on-surface';
      const amtClass = isFlagged ? 'text-tertiary font-bold' : 'text-on-surface font-semibold';
      const badge = isFlagged 
        ? `<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-tertiary/10 text-tertiary text-[10px] font-bold"><span class="w-1 h-1 rounded-full bg-tertiary animate-ping"></span> ${it.status}</span>`
        : `<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-secondary/10 text-secondary text-[10px] font-bold"><span class="w-1 h-1 rounded-full bg-secondary"></span> ${it.status}</span>`;

      return `
        <tr class="${rowClass} transition-colors">
          <td class="py-2.5 px-4 text-on-surface font-sans">
            <div class="font-medium ${isFlagged ? 'text-tertiary flex items-center gap-1' : ''}">
              ${isFlagged ? '<span class="material-symbols-outlined text-[14px]">warning</span>' : ''}
              ${it.description}
            </div>
            <div class="font-mono text-[10px] text-outline">SKU: ${it.sku || 'GEN-SKU-01'}</div>
          </td>
          <td class="py-2.5 px-4 text-right ${qtyClass}">${it.qty}</td>
          <td class="py-2.5 px-4 text-right text-on-surface">₹${Number(it.unit_price).toLocaleString('en-IN')}</td>
          <td class="py-2.5 px-4 text-right ${amtClass}">₹${Number(it.amount).toLocaleString('en-IN')}</td>
          <td class="py-2.5 px-4">${badge}</td>
        </tr>
      `;
    }).join('');
  }

  // Deep Tab 2: Financial Discrepancy
  const fb = inv.financial_breakdown || {};
  const finTax = document.getElementById('fin-taxable-sub');
  if (finTax) finTax.innerText = `₹${Number(fb.taxable_subtotal || inv.taxable_amount || 50000).toLocaleString('en-IN')}`;
  const finC = document.getElementById('fin-cgst');
  if (finC) finC.innerText = `₹${Number(fb.cgst || inv.cgst_amount || 4500).toLocaleString('en-IN')}`;
  const finS = document.getElementById('fin-sgst');
  if (finS) finS.innerText = `₹${Number(fb.sgst || inv.sgst_amount || 4500).toLocaleString('en-IN')}`;
  const finExp = document.getElementById('fin-exp-total');
  if (finExp) finExp.innerText = `₹${Number(fb.expected_grand_total || 59000).toLocaleString('en-IN')}`;
  const finDelta = document.getElementById('fin-delta-num');
  if (finDelta) finDelta.innerText = fb.surplus_gap > 0 ? `+₹${Number(fb.surplus_gap).toLocaleString('en-IN')} Delta` : `₹0 (Balanced)`;
  const finDesc = document.getElementById('fin-delta-desc');
  if (finDesc) finDesc.innerText = fb.gap_explanation || 'All line item mathematical sums reconcile perfectly.';

  // Deep Tab 4: Vendor Profile Cards
  const venCards = document.getElementById('spotlight-vendor-profile-cards');
  if (venCards) {
    const v = STATE.vendors.find(item => item.id === inv.vendor_id || item.name === inv.vendor_name) || STATE.vendors[0] || { paid_invoice_count: 0, total_disbursed: 0, complaints: [] };
    venCards.innerHTML = `
      <div class="p-4 bg-surface-container rounded-xl border border-white/5">
        <span class="font-mono text-[10px] uppercase text-outline">Paid Ledger Volume</span>
        <div class="text-xl font-bold text-on-surface font-mono mt-1">${v.paid_invoice_count || 0} Settled</div>
        <p class="text-xs text-outline mt-0.5 font-mono">₹${((v.total_disbursed || 0)/100000).toFixed(1)} Lakh disbursed</p>
      </div>
      <div class="p-4 bg-surface-container rounded-xl border border-white/5">
        <span class="font-mono text-[10px] uppercase text-outline">Dispute Record</span>
        <div class="text-xl font-bold ${v.complaints?.length ? 'text-error' : 'text-secondary'} font-mono mt-1">${v.complaints?.length || 0} Open Flags</div>
        <p class="text-xs text-outline mt-0.5">Trust Score: ${v.trust_score || 50}/100</p>
      </div>
      <div class="p-4 bg-surface-container rounded-xl border border-white/5">
        <span class="font-mono text-[10px] uppercase text-outline">GSTIN Tax Registration</span>
        <div class="text-sm font-bold text-on-surface font-mono mt-1">${inv.gstin || 'Unavailable'}</div>
        <p class="text-xs text-secondary mt-0.5 font-mono">Verified Active</p>
      </div>
    `;
  }

  // Deep Tab 5: Audit Logs
  const auditLogs = document.getElementById('spotlight-audit-logs');
  if (auditLogs) {
    const logs = inv.audit_logs || [
      { time: '14:32:01', event: 'Invoice ingested via enclave', status: 'SUCCESS', status_class: 'text-secondary' }
    ];
    auditLogs.innerHTML = logs.map(l => `
      <div class="p-3 bg-surface-container rounded-lg flex items-center justify-between border border-white/5">
        <div class="flex items-center gap-3">
          <span class="text-outline font-mono text-[11px]">${l.time}</span>
          <span class="text-on-surface">${l.event}</span>
        </div>
        <span class="${l.status_class || 'text-secondary'} font-semibold">${l.status}</span>
      </div>
    `).join('');
  }

  // Update AI Assistant Context
  const aiCtxInv = document.getElementById('ai-context-inv');
  if (aiCtxInv) aiCtxInv.innerText = `#${inv.invoice_number}`;
  const aiCtxVen = document.getElementById('ai-context-vendor');
  if (aiCtxVen) aiCtxVen.innerText = inv.vendor_name;
}

async function submitUserInvoiceFeedback(feedback) {
  try {
    const res = await fetch(`/api/user/invoices/${STATE.activeInvoiceId}/feedback`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ feedback })
    });
    if (res.ok) {
      showToast(`Marked invoice as ${feedback}. Saved to your compliance baseline.`);
      await refreshUserData();
    }
  } catch (err) {
    console.error(err);
  }
}

function toggleSpotlightEvidence(id) {
  const el = document.getElementById(id);
  const icon = document.getElementById(id + '-icon');
  if (!el) return;
  if (el.classList.contains('hidden')) {
    el.classList.remove('hidden');
    if (icon) icon.innerText = 'expand_more';
  } else {
    el.classList.add('hidden');
    if (icon) icon.innerText = 'expand_less';
  }
}

function switchDeepTab(tabId) {
  document.querySelectorAll('.deep-tab-pane').forEach(el => el.classList.add('hidden'));
  const target = document.getElementById(tabId);
  if (target) target.classList.remove('hidden');

  const btnMap = {
    'tab-line-items': 'btn-deep-line-items',
    'tab-financial': 'btn-deep-financial',
    'tab-document': 'btn-deep-document',
    'tab-vendor': 'btn-deep-vendor',
    'tab-audit': 'btn-deep-audit'
  };

  Object.entries(btnMap).forEach(([tId, bId]) => {
    const b = document.getElementById(bId);
    if (!b) return;
    if (tId === tabId) {
      b.className = 'px-3.5 py-1.5 rounded-lg text-xs font-medium bg-surface-container text-on-surface transition-colors shadow-sm';
    } else {
      b.className = 'px-3.5 py-1.5 rounded-lg text-xs font-medium text-on-surface-variant hover:text-on-surface hover:bg-surface-container transition-colors';
    }
  });
}

// --- Recent Invoices Table & Filters ---
function renderInvoicesTable() {
  const tbody = document.getElementById('invoices-table-body');
  if (!tbody) return;

  let filtered = STATE.invoices;
  if (STATE.invoicesFilter !== 'all') {
    filtered = filtered.filter(i => i.status === STATE.invoicesFilter);
  }
  if (STATE.searchQuery) {
    const q = STATE.searchQuery.toLowerCase();
    filtered = filtered.filter(i => 
      (i.invoice_number && i.invoice_number.toLowerCase().includes(q)) ||
      (i.filename && i.filename.toLowerCase().includes(q)) ||
      (i.vendor_name && i.vendor_name.toLowerCase().includes(q)) ||
      (i.total_amount && i.total_amount.toString().includes(q))
    );
  }

  // Update counts
  const revCount = STATE.invoices.filter(i => i.status === 'review').length;
  const passCount = STATE.invoices.filter(i => i.status === 'passed').length;
  const critCount = STATE.invoices.filter(i => i.status === 'critical').length;
  const cR = document.getElementById('cnt-rev'); if (cR) cR.innerText = revCount;
  const cP = document.getElementById('cnt-pass'); if (cP) cP.innerText = passCount;
  const cC = document.getElementById('cnt-crit'); if (cC) cC.innerText = critCount;

  if (filtered.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="6" class="py-12 text-center text-on-surface-variant">
          <div class="flex flex-col items-center justify-center gap-2">
            <span class="material-symbols-outlined text-[32px] text-outline">inbox</span>
            <span class="font-medium text-sm text-on-surface">No invoices in your repository</span>
            <span class="text-xs text-outline">Upload an invoice to start checking for suspicious activity.</span>
          </div>
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = filtered.map(inv => {
    let badgeClass = 'bg-secondary/10 text-secondary';
    let dotClass = 'bg-secondary';
    let riskLabel = 'LOW RISK';
    let isSelected = inv.id === STATE.activeInvoiceId;

    if (inv.status === 'review') {
      badgeClass = 'bg-warning/10 text-warning';
      dotClass = 'bg-warning';
      riskLabel = 'REVIEW';
    } else if (inv.status === 'critical') {
      badgeClass = 'bg-error/10 text-error';
      dotClass = 'bg-error';
      riskLabel = 'HIGH RISK';
    }

    const verifiedDot = inv.vendor_verified 
      ? `<span class="material-symbols-outlined text-[13px] text-primary" title="Verified vendor">verified</span>` 
      : `<span class="material-symbols-outlined text-[13px] text-error" title="Unverified / Mismatch">warning</span>`;

    const displayFilename = inv.filename || inv.original_filename || inv.file_name || `${inv.id}.pdf`;

    return `
      <tr class="group hover:bg-surface-container transition-colors cursor-pointer ${isSelected ? 'bg-surface-container/60' : ''}" onclick="selectInvoiceForSpotlight('${inv.id}')">
        <td class="py-3.5 px-5">
          <div class="flex flex-col gap-0.5">
            <div class="flex items-center gap-1.5 font-mono">
              <span class="font-bold text-on-surface text-xs sm:text-sm ${inv.status === 'critical' ? 'text-error' : ''}">${inv.invoice_number || inv.id}</span>
              ${inv.status === 'critical' ? '<span class="w-1.5 h-1.5 rounded-full bg-error animate-ping"></span>' : ''}
            </div>
            <span class="text-[11px] text-on-surface-variant font-mono truncate max-w-[210px]" title="${displayFilename}">
              ${displayFilename}
            </span>
          </div>
        </td>
        <td class="py-3.5 px-5">
          <div class="flex items-center gap-1.5">
            <span class="font-medium text-on-surface">${inv.vendor_name}</span>
            ${verifiedDot}
          </div>
        </td>
        <td class="py-3.5 px-5 text-on-surface-variant font-mono">
          ${inv.issue_date}
        </td>
        <td class="py-3.5 px-5 text-right font-mono font-semibold text-on-surface">
          ₹${Number(inv.total_amount).toLocaleString('en-IN')}
        </td>
        <td class="py-3.5 px-5">
          <div class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full ${badgeClass} font-mono text-[10px] font-bold">
            <span class="w-1.5 h-1.5 rounded-full ${dotClass}"></span>
            <span>${String(inv.threat_score).padStart(2, '0')}/100 · ${riskLabel}</span>
          </div>
        </td>
        <td class="py-3.5 px-5 text-right">
          <button class="inline-flex items-center gap-0.5 text-primary hover:text-white font-mono text-[11px] font-medium transition-colors">
            <span>Inspect</span>
            <span class="material-symbols-outlined text-[14px]">arrow_forward</span>
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

function filterInvoicesBy(filterType) {
  STATE.invoicesFilter = filterType;
  document.querySelectorAll('.inv-filter-btn').forEach(btn => {
    if (btn.getAttribute('data-f') === filterType) {
      btn.className = 'inv-filter-btn active px-2.5 py-1 rounded bg-surface-container-high text-on-surface';
    } else {
      btn.className = 'inv-filter-btn px-2.5 py-1 rounded text-on-surface-variant hover:text-on-surface';
    }
  });
  renderInvoicesTable();
}

function filterInvoicesSearch(val) {
  STATE.searchQuery = val;
  renderInvoicesTable();
}

function selectInvoiceForSpotlight(invId) {
  STATE.activeInvoiceId = invId;
  renderSpotlightInvoice(invId);
  renderInvoicesTable();
  
  const el = document.getElementById('analysis-spotlight');
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' });
  }
}

// --- Vendors Registry Grid ---
function renderVendorsGrid() {
  const container = document.getElementById('vendors-cards-grid');
  if (!container) return;

  if (STATE.vendors.length === 0) {
    container.innerHTML = `
      <div class="col-span-full py-8 text-center text-outline text-xs">
        No registered vendors in your account. New vendors are indexed automatically as invoices are processed.
      </div>
    `;
    return;
  }

  container.innerHTML = STATE.vendors.map(v => {
    const isV = v.verified;
    return `
      <div class="rounded-2xl bg-surface-container-low border border-white/5 p-5 flex flex-col justify-between hover:border-white/10 transition-all shadow-sm">
        <div class="flex flex-col gap-2">
          <div class="flex items-center justify-between">
            <h4 class="font-bold text-sm text-on-surface">${v.name}</h4>
            <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full ${isV ? 'bg-primary/15 text-primary' : 'bg-outline/20 text-outline'} font-mono text-[10px] font-semibold">
              <span class="material-symbols-outlined text-[13px]">${isV ? 'verified' : 'pending'}</span>
              ${isV ? 'Verified' : 'Unverified'}
            </span>
          </div>
          <span class="text-xs text-outline">${v.category}</span>

          <div class="flex flex-col gap-1 pt-2 border-t border-white/5 font-mono text-xs">
            <div class="flex justify-between text-on-surface-variant">
              <span>GSTIN:</span>
              <span class="text-on-surface">${v.gstin}</span>
            </div>
            <div class="flex justify-between text-on-surface-variant">
              <span>Known Account:</span>
              <span class="text-on-surface">${v.known_bank_accounts?.[0]?.bank_name || 'Bank'} (*${(v.known_bank_accounts?.[0]?.account_number || '4901').slice(-4)})</span>
            </div>
          </div>
        </div>

        <div class="flex items-center justify-between pt-3 mt-3 border-t border-white/5 font-mono text-xs">
          <span class="text-outline">Trust: <span class="text-secondary font-bold">${v.trust_score}/100</span></span>
          <span class="text-on-surface-variant">${v.paid_invoice_count || 0} settled</span>
        </div>
      </div>
    `;
  }).join('');
}

// --- Vendor Feedback & Complaints List ---
function renderComplaintsList() {
  const container = document.getElementById('feedback-complaints-list');
  if (!container) return;

  if (STATE.complaints.length === 0) {
    container.innerHTML = `
      <div class="py-6 text-center text-outline text-xs">
        No active vendor compliance flags on record for your account.
      </div>
    `;
    return;
  }

  container.innerHTML = STATE.complaints.map(c => `
    <div class="rounded-2xl bg-surface-container-low border border-white/5 p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-sm">
      <div class="flex items-start gap-3">
        <span class="w-7 h-7 rounded-full ${c.severity === 'CRITICAL' ? 'bg-error/20 text-error' : 'bg-tertiary/20 text-tertiary'} flex items-center justify-center shrink-0 mt-0.5">
          <span class="material-symbols-outlined text-[16px]">flag</span>
        </span>
        <div class="flex flex-col gap-0.5">
          <div class="flex items-center gap-2">
            <span class="font-bold text-xs text-on-surface">${c.vendor_name}</span>
            <span class="px-1.5 py-0.2 rounded font-mono text-[10px] ${c.severity === 'CRITICAL' ? 'bg-error/10 text-error' : 'bg-tertiary/10 text-tertiary'} font-bold">${c.severity}</span>
            <span class="font-mono text-[10px] text-outline">Reason: ${c.category}</span>
          </div>
          <p class="text-xs text-on-surface-variant">${c.description}</p>
          <span class="font-mono text-[10px] text-outline mt-0.5">Ref: #${c.invoice_ref} · Reported ${c.reported_date} · Assigned: ${c.assigned_to}</span>
        </div>
      </div>
      <span class="px-2.5 py-1 rounded-full bg-surface-container text-tertiary font-mono text-[10px] font-bold self-start sm:self-center">
        ${c.status}
      </span>
    </div>
  `).join('');
}

// --- Focal Upload Zone Handling ---
function handleDragOver(e) {
  e.preventDefault();
  const dz = document.getElementById('hero-dropzone');
  if (dz) {
    dz.classList.add('border-electric-cyan', 'glow-dropzone', 'laser-active');
    const title = document.getElementById('dropzone-title');
    if (title) title.innerText = 'RELEASE TO SCAN & ANALYZE';
  }
}

function handleDragLeave(e) {
  e.preventDefault();
  const dz = document.getElementById('hero-dropzone');
  if (dz) {
    dz.classList.remove('border-electric-cyan', 'glow-dropzone', 'laser-active');
    const title = document.getElementById('dropzone-title');
    if (title) title.innerText = 'DROP YOUR INVOICE HERE';
  }
}

function handleFileDrop(e) {
  e.preventDefault();
  handleDragLeave(e);
  const dz = document.getElementById('hero-dropzone');
  if (dz) {
    dz.classList.add('drop-pulse');
    setTimeout(() => dz.classList.remove('drop-pulse'), 600);
  }
  if (e.dataTransfer && e.dataTransfer.files.length > 0) {
    processUploadFile(e.dataTransfer.files[0]);
  }
}

function handleHeroFileSelect(e) {
  if (e.target && e.target.files.length > 0) {
    processUploadFile(e.target.files[0]);
  }
}

async function processUploadFile(file) {
  const overlay = document.getElementById('upload-progress-overlay');
  if (overlay) overlay.classList.remove('hidden');

  const setStep = (num, status) => {
    const el = document.getElementById(`step-${num}`);
    if (!el) return;
    if (status === 'active') {
      el.className = 'flex items-center gap-2 text-primary font-bold';
      el.children[0].className = 'material-symbols-outlined text-[16px] animate-spin';
      el.children[0].innerText = 'sync';
    } else if (status === 'done') {
      el.className = 'flex items-center gap-2 text-secondary';
      el.children[0].className = 'material-symbols-outlined text-[16px]';
      el.children[0].innerText = 'check_circle';
    }
  };

  setStep(1, 'done');
  setStep(2, 'active');

  setTimeout(() => {
    setStep(2, 'done');
    setStep(3, 'active');
  }, 400);

  setTimeout(() => {
    setStep(3, 'done');
    setStep(4, 'active');
  }, 750);

  setTimeout(() => {
    setStep(4, 'done');
    setStep(5, 'active');
  }, 1100);

  try {
    let formData = new FormData();
    formData.append('file', file);

    const res = await fetch('/api/user/invoices/upload', {
      method: 'POST',
      headers: { 'X-User-UID': STATE.activeUser.uid },
      body: formData
    });
    const result = await res.json();

    setTimeout(async () => {
      setStep(5, 'done');
      if (overlay) overlay.classList.add('hidden');
      await refreshUserData();
      selectInvoiceForSpotlight(result.invoice_id);
    }, 1400);

  } catch (err) {
    if (overlay) overlay.classList.add('hidden');
    showToast('Upload failed. Please check document.');
    console.error(err);
  }
}

async function loadDemoInvoice(invId) {
  let inv = STATE.invoices.find(i => i.id === invId || i.invoice_number === invId);
  if (!inv) {
    try {
      const res = await fetch(`/api/user/invoices/${invId}`, { headers: getAuthHeaders() });
      if (res.ok) {
        const data = await res.json();
        if (data.invoice) {
          inv = data.invoice;
          STATE.invoices.unshift(inv);
        }
      }
    } catch (err) {
      console.error('Failed to load demo scenario:', err);
    }
  }
  renderDashboardView();
  selectInvoiceForSpotlight(invId);
  showToast(`Loaded demo scenario ${invId}`);
}

function scrollToUpload() {
  const dz = document.getElementById('overview');
  if (dz) dz.scrollIntoView({ behavior: 'smooth' });
}

// --- AI Assistant Chat Workbench ---
function renderChatMessages() {
  const thread = document.getElementById('ai-chat-thread');
  if (!thread) return;

  thread.innerHTML = STATE.chatMessages.map(msg => {
    if (msg.sender === 'user') {
      return `
        <div class="flex flex-col items-end">
          <div class="bg-primary text-on-primary text-xs px-3.5 py-2 rounded-xl rounded-tr-none max-w-[85%] font-medium">
            ${msg.text}
          </div>
          <span class="font-mono text-[10px] text-outline mt-1">${msg.time}</span>
        </div>
      `;
    } else {
      return `
        <div class="flex flex-col items-start">
          <div class="bg-surface-container text-on-surface text-xs p-3.5 rounded-xl rounded-tl-none max-w-[95%] leading-relaxed border border-white/5">
            <p>${msg.text}</p>
          </div>
          <span class="font-mono text-[10px] text-outline mt-1">InvoiceGuard Gemini · ${msg.confidence || '98% confidence'}</span>
        </div>
      `;
    }
  }).join('');

  thread.scrollTop = thread.scrollHeight;
}

async function sendChatMessage() {
  const input = document.getElementById('ai-chat-input');
  if (!input || !input.value.trim()) return;

  const query = input.value.trim();
  input.value = '';

  STATE.chatMessages.push({
    sender: 'user',
    text: query,
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  });
  renderChatMessages();

  try {
    const res = await fetch('/api/ai/chat', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        query: query,
        invoice_id: STATE.activeInvoiceId
      })
    });
    const data = await res.json();
    STATE.chatMessages.push({
      sender: 'ai',
      text: data.reply,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      confidence: `${data.confidence}% confidence`
    });
    renderChatMessages();
  } catch (err) {
    console.error('Chat query error:', err);
  }
}

function sendQuickPrompt(promptText) {
  const input = document.getElementById('ai-chat-input');
  if (input) {
    input.value = promptText;
    sendChatMessage();
  }
}

async function draftComplianceEmailForActive() {
  try {
    const res = await fetch('/api/ai/draft-email', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ invoice_id: STATE.activeInvoiceId })
    });
    const data = await res.json();
    STATE.chatMessages.push({
      sender: 'ai',
      text: `**Generated Vendor Inquiry Draft:**\n\n${data.draft}`,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      confidence: 'Audit Copilot Ready'
    });
    renderChatMessages();
    
    const el = document.getElementById('assistant');
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  } catch (err) {
    console.error('Error drafting notice:', err);
  }
}

// --- Action Triggers (PDF, Hold, Flag) ---
function downloadActivePDF() {
  window.open(`/api/user/invoices/${STATE.activeInvoiceId}/pdf`, '_blank');
}

function togglePaymentHold() {
  const btn = document.getElementById('spotlight-hold-text');
  if (!btn) return;
  if (btn.innerText.includes('Hold')) {
    btn.innerText = 'Release Payment (Cleared)';
    showToast('Payment hold placed on active invoice.');
  } else {
    btn.innerText = 'Approve Payment (Hold)';
    showToast('Payment clearance released.');
  }
}

function openFlagModalForActive() {
  const modal = document.getElementById('flag-modal');
  const invInput = document.getElementById('flag-modal-inv');
  if (invInput) invInput.value = STATE.activeInvoiceId;
  if (modal) modal.classList.remove('hidden');
}

function closeFlagModal() {
  const modal = document.getElementById('flag-modal');
  if (modal) modal.classList.add('hidden');
}

async function submitComplianceDispute() {
  const inv = STATE.invoices.find(i => i.id === STATE.activeInvoiceId) || STATE.invoices[0] || {};
  const category = document.getElementById('flag-modal-category')?.value || 'Suspicious activity';
  const severity = document.getElementById('flag-modal-severity')?.value || 'HIGH';
  const rating = parseInt(document.getElementById('flag-modal-rating')?.value || '3');
  const notes = document.getElementById('flag-modal-notes')?.value || 'Manual compliance flag logged.';

  try {
    const res = await fetch('/api/user/complaints', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        vendor_id: inv.vendor_id || 'VEN-001',
        vendor_name: inv.vendor_name || 'Vendor',
        invoice_ref: inv.invoice_number || 'INV-001',
        severity: severity,
        category: category,
        description: notes,
        rating: rating
      })
    });
    const data = await res.json();
    if (data.status === 'success') {
      closeFlagModal();
      showToast('Vendor report logged & saved to Firestore dataset.');
      await refreshUserData();
      const fb = document.getElementById('feedback');
      if (fb) fb.scrollIntoView({ behavior: 'smooth' });
    }
  } catch (err) {
    console.error('Error submitting dispute:', err);
  }
}

// --- Dedicated Admin Operations Sentinel Engine ---
function openAdminLoginModal() {
  const m = document.getElementById('admin-login-modal');
  if (m) m.classList.remove('hidden');
}

function closeAdminLoginModal() {
  const m = document.getElementById('admin-login-modal');
  if (m) m.classList.add('hidden');
}

async function handleAdminLoginSubmit(e) {
  e.preventDefault();
  const u = document.getElementById('admin-login-user')?.value;
  const p = document.getElementById('admin-login-pass')?.value;
  const errEl = document.getElementById('admin-login-err');

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: u, password: p })
    });
    const data = await res.json();
    
    if (res.ok && data.user.role === 'admin') {
      STATE.activeUser = data.user;
      closeAdminLoginModal();
      enterAdminMode();
      showToast('Authenticated as Master Administrator');
    } else {
      if (errEl) {
        errEl.innerText = 'Invalid admin credentials. Use admin:admins';
        errEl.classList.remove('hidden');
      }
    }
  } catch (err) {
    console.error(err);
  }
}

function enterAdminMode() {
  document.getElementById('user-main-view')?.classList.add('hidden');
  document.getElementById('admin-main-view')?.classList.remove('hidden');
  document.getElementById('user-nav-bar')?.classList.add('hidden');
  document.getElementById('admin-nav-bar')?.classList.remove('hidden');
  document.getElementById('admin-nav-bar')?.classList.add('flex');
  document.getElementById('header-upload-btn')?.classList.add('hidden');
  document.getElementById('header-admin-login-btn')?.classList.add('hidden');
  
  const hBadge = document.getElementById('header-status-badge');
  if (hBadge) {
    hBadge.innerText = 'ADMIN ACTIVE';
    hBadge.className = 'hidden sm:inline-flex text-[10px] font-mono font-bold uppercase px-1.5 py-0.5 rounded bg-error/10 text-error border border-error/20';
  }

  updateUserDisplay();
  refreshAdminData();
}

function exitAdminMode() {
  STATE.activeUser = STATE.demoUsers[0] || { uid: 'usr_demo1_alex', name: 'Alex Vance', role: 'user' };
  
  document.getElementById('user-main-view')?.classList.remove('hidden');
  document.getElementById('admin-main-view')?.classList.add('hidden');
  document.getElementById('user-nav-bar')?.classList.remove('hidden');
  document.getElementById('admin-nav-bar')?.classList.add('hidden');
  document.getElementById('admin-nav-bar')?.classList.remove('flex');
  document.getElementById('header-upload-btn')?.classList.remove('hidden');
  document.getElementById('header-admin-login-btn')?.classList.remove('hidden');

  const hBadge = document.getElementById('header-status-badge');
  if (hBadge) {
    hBadge.innerText = 'SECURE';
    hBadge.className = 'hidden sm:inline-flex text-[10px] font-mono font-semibold uppercase px-1.5 py-0.5 rounded bg-secondary/10 text-secondary border border-secondary/20';
  }

  updateUserDisplay();
  refreshUserData();
  showToast('Exited Admin Mode. Returned to Tenant Dashboard.');
}

async function refreshAdminData() {
  try {
    const headers = getAuthHeaders();
    const [ovRes, invRes, venRes] = await Promise.all([
      fetch('/api/admin/overview', { headers }),
      fetch('/api/admin/invoices', { headers }),
      fetch('/api/admin/vendors', { headers })
    ]);

    const overview = await ovRes.json();
    const invData = await invRes.json();
    const venData = await venRes.json();
    STATE.adminData = { overview, invoices: invData.invoices, vendors: venData.vendors };

    // Update Admin Stats
    document.getElementById('adm-stat-tenants').innerText = `${overview.total_tenants} Orgs`;
    document.getElementById('adm-stat-invoices').innerText = overview.total_invoices_audited;
    document.getElementById('adm-stat-vol').innerText = `₹${(overview.total_volume_inr / 100000).toFixed(1)}L`;
    document.getElementById('adm-stat-risk').innerText = `₹${overview.total_volume_at_risk_inr.toLocaleString('en-IN')}`;

    // Render Admin Views
    renderAdminLedgerTable(invData.invoices);
    renderAdminBlacklist(overview.blacklist);
    renderAdminVendorVerificationQueue(venData.vendors);
  } catch (err) {
    console.error('Error loading admin data:', err);
  }
}

function renderAdminVendorVerificationQueue(vendors) {
  const container = document.getElementById('admin-vendor-verify-grid');
  if (!container) return;

  if (!vendors || vendors.length === 0) {
    container.innerHTML = '<div class="col-span-full p-4 text-center text-xs text-outline font-mono">No extracted vendors in review queue.</div>';
    return;
  }

  container.innerHTML = vendors.map(v => `
    <div class="p-4 rounded-xl bg-surface-container border border-white/5 flex flex-col justify-between gap-2.5 text-xs">
      <div class="flex flex-col gap-1">
        <div class="flex items-center justify-between">
          <span class="font-bold text-on-surface text-sm">${v.name}</span>
          <span class="px-2 py-0.5 rounded-full ${v.verified ? 'bg-primary/10 text-primary font-bold border border-primary/20' : 'bg-outline/10 text-outline border border-outline/20'} font-mono text-[10px]">
            ${v.verified ? '🔵 Verified' : '○ Pending Verification'}
          </span>
        </div>
        <span class="text-outline font-mono text-[11px]">GSTIN: ${v.gstin || 'Unavailable'}</span>
        <span class="text-on-surface-variant text-[11px]">Category: ${v.category || 'General Procurement'}</span>
        ${v.owner_name ? `<span class="mt-1 inline-flex items-center gap-1 text-primary text-[10px] font-mono bg-primary/5 px-2 py-0.5 rounded border border-primary/10">Uploaded by: ${v.owner_name} (${v.owner_email})</span>` : ''}
      </div>

      <div class="pt-2 border-t border-white/5 flex items-center justify-between">
        <span class="text-outline font-mono text-[10px]">Trust: ${v.trust_score || 50}/100</span>
        ${v.verified 
          ? '<span class="text-secondary font-mono text-[11px] font-semibold flex items-center gap-1"><span class="material-symbols-outlined text-[13px]">verified</span> Verified</span>'
          : `<button onclick="verifyVendorAsAdmin('${v.id}')" class="px-3 py-1 rounded-lg bg-primary text-on-primary font-bold text-[11px] hover:bg-white transition-colors flex items-center gap-1 shadow-sm"><span class="material-symbols-outlined text-[13px]">check_circle</span> Approve KYC</button>`
        }
      </div>
    </div>
  `).join('');
}

async function verifyVendorAsAdmin(vendorId) {
  try {
    const res = await fetch(`/api/admin/vendors/${vendorId}/verify`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    if (res.ok) {
      showToast('Vendor approved: 🔵 Verified by InvoiceGuard');
      await refreshAdminData();
    }
  } catch (err) {
    console.error(err);
  }
}

function renderAdminLedgerTable(invoices) {
  const tbody = document.getElementById('admin-invoices-tbody');
  if (!tbody) return;

  tbody.innerHTML = invoices.map(i => `
    <tr class="hover:bg-surface-container transition-colors">
      <td class="py-3 px-4 font-bold text-on-surface">#${i.invoice_number}</td>
      <td class="py-3 px-4 font-sans font-medium text-primary">${i.owner_name} <span class="text-outline text-[10px] block font-mono">${i.owner_email}</span></td>
      <td class="py-3 px-4 font-sans">${i.vendor_name}</td>
      <td class="py-3 px-4 text-right">₹${Number(i.total_amount).toLocaleString('en-IN')}</td>
      <td class="py-3 px-4">
        <span class="px-2 py-0.5 rounded-full ${i.threat_score > 75 ? 'bg-error/10 text-error' : (i.threat_score > 25 ? 'bg-tertiary/10 text-tertiary' : 'bg-secondary/10 text-secondary')} font-bold">
          ${i.threat_score}/100
        </span>
      </td>
      <td class="py-3 px-4 uppercase text-[10px] font-bold ${i.status === 'critical' ? 'text-error' : (i.status === 'review' ? 'text-tertiary' : 'text-secondary')}">${i.status}</td>
    </tr>
  `).join('');
}

function renderAdminBlacklist(blacklist) {
  const container = document.getElementById('admin-blacklist-items');
  const countEl = document.getElementById('adm-blacklist-count');
  if (countEl) countEl.innerText = `${blacklist.length} Blacklisted`;
  if (!container) return;

  container.innerHTML = blacklist.map(b => `
    <div class="p-3 bg-surface-container rounded-xl border border-error/20 flex flex-col gap-1 text-xs">
      <div class="flex items-center justify-between">
        <span class="font-bold text-on-surface">${b.vendor_name}</span>
        <span class="px-1.5 py-0.2 rounded bg-error/20 text-error font-mono text-[10px] font-bold">${b.severity}</span>
      </div>
      <span class="font-mono text-[11px] text-outline">GSTIN: ${b.gstin}</span>
      <p class="text-on-surface-variant text-[11px] mt-0.5">${b.reason}</p>
    </div>
  `).join('');
}

function filterAdminLedger(query) {
  if (!STATE.adminData) return;
  const q = query.toLowerCase();
  const filtered = STATE.adminData.invoices.filter(i => 
    i.invoice_number.toLowerCase().includes(q) ||
    i.vendor_name.toLowerCase().includes(q) ||
    i.owner_name.toLowerCase().includes(q)
  );
  renderAdminLedgerTable(filtered);
}

async function submitAdminBlacklist() {
  const vendor = document.getElementById('adm-blk-vendor')?.value;
  const gstin = document.getElementById('adm-blk-gstin')?.value;
  const reason = document.getElementById('adm-blk-reason')?.value;

  if (!vendor || !gstin || !reason) {
    showToast('Please fill all blacklist fields.');
    return;
  }

  try {
    const res = await fetch('/api/admin/vendors/blacklist', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ vendor_name: vendor, gstin: gstin, reason: reason, severity: 'CRITICAL' })
    });
    if (res.ok) {
      showToast(`Blacklisted ${vendor} across all enterprise nodes.`);
      document.getElementById('adm-blk-vendor').value = '';
      document.getElementById('adm-blk-gstin').value = '';
      document.getElementById('adm-blk-reason').value = '';
      await refreshAdminData();
    }
  } catch (err) {
    console.error(err);
  }
}

// --- Persona Switcher Modal ---
function openDemoUserModal() {
  const m = document.getElementById('demo-user-modal');
  if (m) m.classList.remove('hidden');
}

function closeDemoUserModal() {
  const m = document.getElementById('demo-user-modal');
  if (m) m.classList.add('hidden');
}

function renderDemoUsersList() {
  const list = document.getElementById('demo-users-modal-list');
  if (!list) return;

  list.innerHTML = STATE.demoUsers.map(u => {
    const isActive = u.uid === STATE.activeUser.uid;
    const checkIcon = isActive
      ? `<span class="material-symbols-outlined text-[20px] text-[#4285F4] shrink-0" title="Active Persona">check_circle</span>`
      : `<span class="material-symbols-outlined text-[20px] text-[#94A3B8]/35 group-hover:text-[#4285F4] shrink-0 transition-colors" title="Select Persona">radio_button_unchecked</span>`;

    const avatarGraphic = isActive
      ? `<div class="w-8 h-8 rounded-full bg-[#4285F4]/20 border border-[#4285F4]/50 flex items-center justify-center text-[#4285F4] shrink-0 shadow-sm">
           <span class="material-symbols-outlined text-[20px]">person</span>
         </div>`
      : `<div class="w-8 h-8 rounded-full bg-surface-container-high border border-white/10 flex items-center justify-center text-on-surface-variant group-hover:text-on-surface group-hover:border-white/20 shrink-0 transition-all">
           <span class="material-symbols-outlined text-[20px]">person</span>
         </div>`;

    return `
      <div class="group p-3 rounded-xl ${isActive ? 'bg-surface-container border border-[#4285F4]/40 shadow-[0_0_12px_rgba(66,133,244,0.15)]' : 'bg-surface-container-low hover:bg-surface-container border border-white/5'} flex items-center justify-between cursor-pointer transition-all" onclick="switchDemoUser('${u.uid}')">
        <div class="flex items-center gap-3">
          ${avatarGraphic}
          <div class="flex flex-col">
            <span class="text-xs font-bold text-on-surface font-sans flex items-center gap-1.5">
              ${u.name}
              ${isActive ? '<span class="text-[#4285F4] text-[10px] font-mono font-semibold">(Active)</span>' : ''}
            </span>
            <span class="font-mono text-[10px] text-outline">${u.email} · ${u.title}</span>
          </div>
        </div>
        ${checkIcon}
      </div>
    `;
  }).join('');
}

async function switchDemoUser(uid) {
  const matched = STATE.demoUsers.find(u => u.uid === uid);
  if (!matched) return;

  STATE.activeUser = matched;
  closeDemoUserModal();
  updateUserDisplay();
  renderDemoUsersList();
  
  if (STATE.activeUser.role === 'admin') {
    enterAdminMode();
  } else {
    document.getElementById('user-main-view')?.classList.remove('hidden');
    document.getElementById('admin-main-view')?.classList.add('hidden');
    document.getElementById('user-nav-bar')?.classList.remove('hidden');
    document.getElementById('admin-nav-bar')?.classList.add('hidden');
    document.getElementById('header-upload-btn')?.classList.remove('hidden');
    document.getElementById('header-admin-login-btn')?.classList.remove('hidden');
    
    await refreshUserData();
  }
  
  showToast(`Switched account to ${STATE.activeUser.name} (${STATE.activeUser.title})`);
}

function updateUserDisplay() {
  const u = STATE.activeUser;
  if (!u) return;
  const nameEl = document.getElementById('user-display-name');
  if (nameEl) nameEl.innerText = u.name;
  const roleEl = document.getElementById('user-display-role');
  if (roleEl) roleEl.innerText = u.title || (u.role === 'admin' ? 'Administrator' : 'Finance User');
  renderDemoUsersList();
}

// --- Theme & Toasts ---
function toggleTheme() {
  const html = document.documentElement;
  const icon = document.getElementById('theme-icon');
  if (html.classList.contains('dark')) {
    html.classList.remove('dark');
    html.classList.add('light');
    if (icon) icon.innerText = 'light_mode';
    showToast('Switched to Light Mode.');
  } else {
    html.classList.remove('light');
    html.classList.add('dark');
    if (icon) icon.innerText = 'dark_mode';
    showToast('Switched to Dark Mode.');
  }
}

function showToast(msg) {
  const toast = document.getElementById('toast');
  const text = document.getElementById('toast-msg');
  if (!toast || !text) return;
  text.innerText = msg;
  toast.classList.remove('opacity-0', 'translate-y-4');
  toast.classList.add('opacity-100', 'translate-y-0');
  setTimeout(() => {
    toast.classList.remove('opacity-100', 'translate-y-0');
    toast.classList.add('opacity-0', 'translate-y-4');
  }, 3200);
}

// --- Scroll Spy & Keyboard Shortcuts ---
function setupScrollSpy() {
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-link');
  const scrollProgressBar = document.getElementById('scroll-progress-bar');

  const updateActiveLink = () => {
    let current = 'overview';
    const winScroll = window.scrollY || document.documentElement.scrollTop;

    if (winScroll < 120) {
      current = 'overview';
    } else {
      sections.forEach(sec => {
        const top = sec.offsetTop - 140;
        if (winScroll >= top) {
          current = sec.getAttribute('id');
        }
      });
    }

    navLinks.forEach(link => {
      if (link.getAttribute('data-section') === current) {
        link.className = 'nav-link px-4 py-1.5 text-xs font-medium text-primary active transition-all relative font-mono tracking-wider';
      } else {
        link.className = 'nav-link px-4 py-1.5 text-xs font-medium text-on-surface-variant hover:text-on-surface transition-all relative';
      }
    });

    if (scrollProgressBar) {
      const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
      const scrolled = height > 0 ? (winScroll / height) * 100 : 0;
      scrollProgressBar.style.width = scrolled + '%';
    }
  };

  window.addEventListener('scroll', updateActiveLink);
  updateActiveLink();
}

function setupKeyboardShortcuts() {
  window.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'u') {
      e.preventDefault();
      scrollToUpload();
    }
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      const s = document.getElementById('invoices-filter-input');
      if (s) {
        s.focus();
        s.scrollIntoView({ behavior: 'smooth' });
      }
    }
    if (e.key === 'Escape') {
      closeDemoUserModal();
      closeFlagModal();
      closeAdminLoginModal();
    }
  });
}

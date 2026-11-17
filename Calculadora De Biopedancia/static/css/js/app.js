(() => {
  const root = document.documentElement;
  const themeToggle = document.getElementById('themeToggle');

  function updateThemeButton() {
    if (!themeToggle) return;
    const dark = root.dataset.theme === 'dark';
    themeToggle.setAttribute('aria-label', dark ? 'Ativar modo claro' : 'Ativar modo noturno');
    const label = themeToggle.querySelector('.theme-label');
    if (label) label.textContent = dark ? 'Modo claro' : 'Modo noturno';
    const icon = themeToggle.querySelector('.theme-icon');
    if (icon) icon.textContent = dark ? '☼' : '◐';
  }

  themeToggle?.addEventListener('click', () => {
    root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem('corpofit-theme', root.dataset.theme); } catch (_) {}
    updateThemeButton();
  });
  updateThemeButton();

  const profileSelect = document.getElementById('profileSelect');
  const newProfileFields = document.getElementById('newProfileFields');
  const profileSex = document.getElementById('profileSex');
  const methodSelect = document.getElementById('method');
  const navyFields = document.getElementById('navyFields');
  const skinfoldFields = document.getElementById('skinfoldFields');

  function selectedSex() {
    if (profileSelect?.value === '__new__') return profileSex?.value || 'female';
    return profileSelect?.selectedOptions?.[0]?.dataset.sex || (document.querySelector('.locked-profile .muted')?.textContent.includes('masculina') ? 'male' : 'female');
  }

  function updateConditionalFields() {
    if (!methodSelect) return;
    const method = methodSelect.value;
    const sex = selectedSex();
    if (navyFields) navyFields.hidden = method !== 'navy';
    if (skinfoldFields) skinfoldFields.hidden = !['jp3', 'jp7'].includes(method);
    document.querySelectorAll('.method-field').forEach((wrapper) => {
      const shown = (wrapper.dataset.methodSex || '').split(' ').includes(`${method}:${sex}`);
      wrapper.hidden = !shown;
      const input = wrapper.querySelector('input');
      if (input) input.required = shown;
    });
    if (newProfileFields) {
      const isNew = profileSelect?.value === '__new__';
      newProfileFields.hidden = !isNew;
      const name = document.getElementById('newProfileName');
      if (name) name.required = isNew;
      if (profileSex) profileSex.required = isNew;
    }
  }

  [profileSelect, profileSex, methodSelect].forEach((element) => element?.addEventListener('change', updateConditionalFields));
  updateConditionalFields();

  document.querySelectorAll('form[data-confirm]').forEach((form) => {
    form.addEventListener('submit', (event) => {
      if (!window.confirm(form.dataset.confirm || 'Confirmar ação?')) event.preventDefault();
    });
  });

  const form = document.getElementById('assessmentForm');
  const errorBox = document.getElementById('clientErrors');
  form?.addEventListener('submit', (event) => {
    const requiredInputs = [...form.querySelectorAll('input[required], select[required]')].filter((input) => !input.closest('[hidden]'));
    const missing = requiredInputs.find((input) => !String(input.value).trim());
    if (missing) {
      event.preventDefault();
      if (errorBox) {
        errorBox.textContent = `Preencha o campo “${missing.labels?.[0]?.textContent?.trim() || 'obrigatório'}” para continuar.`;
        errorBox.hidden = false;
      }
      missing.focus();
      return;
    }
    if (errorBox) errorBox.hidden = true;
  });

  const historyElement = document.getElementById('historyData');
  if (!historyElement) return;
  let records = [];
  try { records = JSON.parse(historyElement.textContent || '[]'); } catch (_) { records = []; }

  function renderLineChart(containerId, key, color, formatter) {
    const container = document.getElementById(containerId);
    if (!container) return;
    if (records.length < 2) {
      container.innerHTML = '<div class="chart-empty">Registre ao menos duas avaliações neste perfil para visualizar uma tendência.</div>';
      return;
    }
    const values = records.map((item) => Number(item[key])).filter(Number.isFinite);
    if (values.length < 2) {
      container.innerHTML = '<div class="chart-empty">Ainda não há dados suficientes para desenhar este gráfico.</div>';
      return;
    }
    const width = 720;
    const height = 190;
    const left = 34;
    const right = 14;
    const top = 15;
    const bottom = 28;
    const minValue = Math.min(...values);
    const maxValue = Math.max(...values);
    const spread = Math.max(maxValue - minValue, Math.abs(maxValue) * 0.05, 1);
    const low = minValue - spread * 0.15;
    const high = maxValue + spread * 0.15;
    const plotW = width - left - right;
    const plotH = height - top - bottom;
    const points = records.map((item, index) => {
      const value = Number(item[key]);
      const x = left + (records.length === 1 ? 0 : index * plotW / (records.length - 1));
      const y = top + (high - value) * plotH / (high - low);
      return { x, y, value, date: item.date };
    });
    const NS = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(NS, 'svg');
    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
    svg.setAttribute('role', 'img');
    const seriesLabel = key === 'body_fat' ? 'Percentual de gordura' : (key === 'lean_mass' ? 'Massa livre de gordura' : 'Peso corporal');
    svg.setAttribute('aria-label', `${seriesLabel} em ${points.length} avaliações`);
    for (let i = 0; i < 3; i += 1) {
      const y = top + i * plotH / 2;
      const grid = document.createElementNS(NS, 'line');
      grid.setAttribute('x1', left); grid.setAttribute('x2', width - right);
      grid.setAttribute('y1', y); grid.setAttribute('y2', y);
      grid.setAttribute('stroke', 'var(--line)'); grid.setAttribute('stroke-dasharray', '3 5');
      svg.appendChild(grid);
    }
    const line = document.createElementNS(NS, 'polyline');
    line.setAttribute('points', points.map((point) => `${point.x},${point.y}`).join(' '));
    line.setAttribute('fill', 'none'); line.setAttribute('stroke', color); line.setAttribute('stroke-width', '3');
    line.setAttribute('stroke-linecap', 'round'); line.setAttribute('stroke-linejoin', 'round');
    svg.appendChild(line);
    points.forEach((point) => {
      const circle = document.createElementNS(NS, 'circle');
      circle.setAttribute('cx', point.x); circle.setAttribute('cy', point.y); circle.setAttribute('r', '5');
      circle.setAttribute('fill', 'var(--surface)'); circle.setAttribute('stroke', color); circle.setAttribute('stroke-width', '3');
      const title = document.createElementNS(NS, 'title');
      title.textContent = `${point.date}: ${formatter(point.value)}`;
      circle.appendChild(title); svg.appendChild(circle);
    });
    const first = document.createElementNS(NS, 'text');
    first.setAttribute('x', left); first.setAttribute('y', height - 7); first.setAttribute('fill', 'var(--muted)');
    first.setAttribute('font-size', '10'); first.textContent = points[0].date;
    const last = document.createElementNS(NS, 'text');
    last.setAttribute('x', width - right); last.setAttribute('y', height - 7); last.setAttribute('text-anchor', 'end');
    last.setAttribute('fill', 'var(--muted)'); last.setAttribute('font-size', '10'); last.textContent = points[points.length - 1].date;
    svg.append(first, last);
    container.replaceChildren(svg);
  }
  const pt = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1 });
  renderLineChart('fatChart', 'body_fat', '#5946d8', (value) => `${pt.format(value)}%`);
  renderLineChart('weightChart', 'weight', '#31aaa7', (value) => `${pt.format(value)} kg`);
  renderLineChart('leanChart', 'lean_mass', '#bd7d38', (value) => `${pt.format(value)} kg`);
})();

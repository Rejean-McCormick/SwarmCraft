// Minimal client to render a mock dashboard; to be wired to real endpoints later
(function(){
  const container = document.getElementById('dashboard');
  if(!container) return;
  const cards = [
    { title: 'Total', value: 0 },
    { title: 'In Progress', value: 0 },
    { title: 'Completed', value: 0 }
  ];
  cards.forEach(c => {
    const el = document.createElement('div');
    el.className = 'card';
    el.innerHTML = `<h3>${c.title}</h3><div class="value">${c.value}</div><div class="progress"><span style="width:${Math.min(100, c.value)}%"></span></div>`;
    container.appendChild(el);
  });
})();

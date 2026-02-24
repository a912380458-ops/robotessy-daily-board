function renderBoard(containerId, days) {
  const container = document.getElementById(containerId);
  container.innerHTML = "";

  if (!Array.isArray(days) || days.length === 0) {
    container.innerHTML = '<div class="empty">近14天暂无可展示内容</div>';
    return 0;
  }

  let count = 0;
  days.forEach((day) => {
    count += day.total || 0;
    const card = document.createElement("div");
    card.className = "day-card";

    const entries = (day.items || [])
      .map((item) => {
        const source = item.source ? `（${item.source}）` : "";
        return `<li><a href="${item.link}" target="_blank" rel="noopener noreferrer">${item.title}</a> ${source}</li>`;
      })
      .join("");

    card.innerHTML = `
      <div class="day-head">
        <span class="date">${day.date}</span>
        <span class="badge">共 ${day.total || 0} 条</span>
      </div>
      <ul>${entries || '<li>暂无条目</li>'}</ul>
    `;
    container.appendChild(card);
  });

  return count;
}

async function bootstrap() {
  const resp = await fetch(`./data/latest.json?t=${Date.now()}`);
  const data = await resp.json();

  const chinaCount = renderBoard("chinaBoard", data.china);
  const overseasCount = renderBoard("overseasBoard", data.overseas);

  document.getElementById("chinaCount").textContent = String(chinaCount);
  document.getElementById("overseasCount").textContent = String(overseasCount);
  document.getElementById("meta").textContent = `关键词：${data.keyword} | 最后更新：${data.updated_at || "-"}`;
}

bootstrap().catch((err) => {
  document.getElementById("meta").textContent = `加载失败：${err.message}`;
});

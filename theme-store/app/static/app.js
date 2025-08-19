const api = {
  info: () => fetch("/api/v1/info").then((r) => r.json()),
  listThemes: () => fetch("/api/v1/themes").then((r) => r.json()),
  saveTheme: (payload) =>
    fetch("/api/v1/themes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }).then((r) => (r.ok ? r.json() : r.json().then((e) => Promise.reject(e)))),
  listInstalled: () => fetch("/api/v1/install").then((r) => r.json()),
  install: (payload) =>
    fetch("/api/v1/install", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }).then((r) => (r.ok ? r.json() : r.json().then((e) => Promise.reject(e)))),
  uninstall: (id) =>
    fetch(`/api/v1/install/${encodeURIComponent(id)}`, {
      method: "DELETE",
    }).then((r) => (r.ok ? r.json() : r.json().then((e) => Promise.reject(e)))),
};

async function refresh() {
  const [info, themes, installed] = await Promise.all([
    api.info(),
    api.listThemes(),
    api.listInstalled(),
  ]);

  document.getElementById("info").textContent =
    `v${info.version} · uptime ${info.uptime_seconds}s`;

  const catBody = document.getElementById("catalog-body");
  catBody.innerHTML = "";
  themes.forEach((t) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${t.id}</td><td>${t.name}</td><td>${t.author ?? ""}</td><td>${t.description ?? ""}</td>`;
    catBody.appendChild(tr);
  });

  const instBody = document.getElementById("installed-body");
  instBody.innerHTML = "";
  installed.forEach((i) => {
    const tr = document.createElement("tr");
    const valid = i.valid
      ? `<span class="badge ok">valid</span>`
      : `<span class="badge bad">invalid</span>`;
    tr.innerHTML = `<td>${i.id}</td><td><code>${i.path}</code></td><td>${valid}</td><td><button data-id="${i.id}" class="btn-uninstall">Remove</button></td>`;
    instBody.appendChild(tr);
  });

  // Wire uninstall buttons
  document.querySelectorAll(".btn-uninstall").forEach((btn) => {
    btn.onclick = async () => {
      const id = btn.getAttribute("data-id");
      if (!confirm(`Remove ${id}?`)) return;
      try {
        await api.uninstall(id);
        await refresh();
      } catch (e) {
        alert("Error: " + (e.detail ?? JSON.stringify(e)));
      }
    };
  });
}

function wireForms() {
  const addForm = document.getElementById("add-theme-form");
  addForm.onsubmit = async (e) => {
    e.preventDefault();
    const fd = new FormData(addForm);
    try {
      await api.saveTheme({
        id: fd.get("id"),
        name: fd.get("name"),
        author: fd.get("author") || null,
        description: fd.get("description") || null,
      });
      addForm.reset();
      await refresh();
    } catch (err) {
      alert("Error: " + (err.detail ?? JSON.stringify(err)));
    }
  };

  const urlForm = document.getElementById("install-url-form");
  urlForm.onsubmit = async (e) => {
    e.preventDefault();
    const fd = new FormData(urlForm);
    try {
      await api.install({ id: fd.get("id"), url: fd.get("url") });
      urlForm.reset();
      await refresh();
    } catch (err) {
      alert("Error: " + (err.detail ?? JSON.stringify(err)));
    }
  };

  const contentForm = document.getElementById("install-content-form");
  contentForm.onsubmit = async (e) => {
    e.preventDefault();
    const fd = new FormData(contentForm);
    try {
      await api.install({ id: fd.get("id"), content: fd.get("content") });
      contentForm.reset();
      await refresh();
    } catch (err) {
      alert("Error: " + (err.detail ?? JSON.stringify(err)));
    }
  };
}

window.addEventListener("DOMContentLoaded", async () => {
  wireForms();
  await refresh();
});

const API = window.location.origin;

async function get(path) {
  const res = await fetch(`${API}${path}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

document.getElementById('loadProfile').onclick = async () => {
  const out = document.getElementById('profile');
  out.textContent = 'Loading...';
  try {
    const data = await get('/profile');
    out.textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    out.textContent = e.toString();
  }
};

document.getElementById('doSearch').onclick = async () => {
  const q = document.getElementById('q').value;
  const out = document.getElementById('search');
  out.textContent = 'Loading...';
  try {
    const data = await get(`/search?q=${encodeURIComponent(q)}`);
    out.textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    out.textContent = e.toString();
  }
};

document.getElementById('loadProjects').onclick = async () => {
  const skill = document.getElementById('skill').value;
  const out = document.getElementById('projects');
  out.textContent = 'Loading...';
  try {
    const qs = skill ? `?skill=${encodeURIComponent(skill)}` : '';
    const data = await get(`/projects${qs}`);
    out.textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    out.textContent = e.toString();
  }
};

document.getElementById('loadTopSkills').onclick = async () => {
  const out = document.getElementById('topskills');
  out.textContent = 'Loading...';
  try {
    const data = await get('/skills/top?limit=7');
    out.textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    out.textContent = e.toString();
  }
};

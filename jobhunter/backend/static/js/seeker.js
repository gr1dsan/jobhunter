const API_BASE_URL = '';
const SEEKER_ID = parseInt(window.location.pathname.split('/')[2]);

function showStatus(message, type) {
    const el = document.getElementById('status');
    el.textContent = message;
    el.style.color =
        type === 'error' ? 'red' :
        type === 'success' ? 'green' : '#4da3ff';
}

function getDropdownValues(name) {
    const dropdown = document.querySelector(`[data-multi="${name}"]`);
    return [...dropdown.querySelectorAll('input:checked')].map(x => x.value);
}

function setupDropdowns() {
    document.querySelectorAll('.dropdown').forEach(d => {
        const btn = d.querySelector('.dropdown-btn');
        const inputs = d.querySelectorAll('input');

        btn.addEventListener('click', e => {
            e.stopPropagation();
            d.classList.toggle('open');
        });

        inputs.forEach(i => {
            i.addEventListener('change', () => {
                const values = [...d.querySelectorAll('input:checked')].map(x => x.value);
                btn.textContent = values.length ? values.join(', ') : 'Select';
            });
        });
    });

    document.addEventListener('click', () => {
        document.querySelectorAll('.dropdown').forEach(d => d.classList.remove('open'));
    });
}

async function runSearch() {
    const keyword = document.getElementById('keyword').value;
    const cities = getDropdownValues('cities');
    const categories = getDropdownValues('categories');
    const working_hours = getDropdownValues('working_hours');
    const min_salary = document.getElementById('min_salary').value || null;

    showStatus('Searching...', 'loading');

    const res = await fetch(`${API_BASE_URL}/api/search_jobs/`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            keyword,
            cities: cities.length ? cities : null,
            categories: categories.length ? categories : null,
            working_hours: working_hours.length ? working_hours : null,
            min_salary: min_salary ? parseInt(min_salary) : null
        })
    });

    const data = await res.json();
    displayJobs(data.jobs || []);
}

async function saveFilters() {
    const res = await fetch(`${API_BASE_URL}/api/seeker/${SEEKER_ID}/save-filters/`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            keyword: document.getElementById('keyword').value,
            cities: getDropdownValues('cities'),
            categories: getDropdownValues('categories'),
            working_hours: getDropdownValues('working_hours'),
            min_salary: parseInt(document.getElementById('min_salary').value || 0)
        })
    });

    showStatus('Saved', 'success');
}

function displayJobs(jobs) {
    const el = document.getElementById('results');

    if (!jobs.length) {
        el.innerHTML = '<p>No jobs</p>';
        return;
    }

    el.innerHTML = jobs.map(j => `
        <div>
            <h3>${j.title}</h3>
            <p>${j.company}</p>
            <p>${j.min_salary || ''} - ${j.max_salary || ''}</p>
            <a href="${j.url}" target="_blank">Open</a>
        </div>
    `).join('');
}

async function loadSeeker() {
    const res = await fetch(`${API_BASE_URL}/api/seekers/`);
    const data = await res.json();

    const s = (data.seekers || []).find(x => x.id === SEEKER_ID);
    if (s) document.getElementById('seekerTitle').textContent = s.title;
}

async function loadFilters() {
    const res = await fetch(`${API_BASE_URL}/api/seeker/${SEEKER_ID}/filters/`);
    const data = await res.json();

    if (data.keyword) document.getElementById('keyword').value = data.keyword;
    if (data.min_salary) document.getElementById('min_salary').value = data.min_salary;

    if (data.cities && data.cities.length) {
        data.cities.forEach(city => {
            const checkbox = document.querySelector(`[data-multi="cities"] input[value="${city}"]`);
            if (checkbox) checkbox.checked = true;
        });
        const citiesDropdown = document.querySelector('[data-multi="cities"]');
        const btn = citiesDropdown.querySelector('.dropdown-btn');
        btn.textContent = data.cities.join(', ');
    }

    if (data.categories && data.categories.length) {
        data.categories.forEach(cat => {
            const checkbox = document.querySelector(`[data-multi="categories"] input[value="${cat}"]`);
            if (checkbox) checkbox.checked = true;
        });
        const categoriesDropdown = document.querySelector('[data-multi="categories"]');
        const btn = categoriesDropdown.querySelector('.dropdown-btn');
        btn.textContent = data.categories.join(', ');
    }

    if (data.working_hours && data.working_hours.length) {
        data.working_hours.forEach(wh => {
            const checkbox = document.querySelector(`[data-multi="working_hours"] input[value="${wh}"]`);
            if (checkbox) checkbox.checked = true;
        });
        const whDropdown = document.querySelector('[data-multi="working_hours"]');
        const btn = whDropdown.querySelector('.dropdown-btn');
        btn.textContent = data.working_hours.join(', ');
    }
}

async function loadJobs() {
    const res = await fetch(`${API_BASE_URL}/api/seeker/${SEEKER_ID}/jobs/`);
    const data = await res.json();
    displayJobs(data.jobs || []);
}

document.getElementById('runBtn').addEventListener('click', runSearch);
document.getElementById('saveBtn').addEventListener('click', saveFilters);

setupDropdowns();
loadSeeker();
loadFilters();
loadJobs();
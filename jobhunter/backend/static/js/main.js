const base_api = '';

const seekersList = document.getElementById('seekersList');
const statusEl = document.getElementById('status');
const modal = document.getElementById("modal");
const openModalBtn = document.getElementById("openModalBtn");
const closeModalBtn = document.getElementById("closeModalBtn");
const createBtn = document.getElementById("createBtn");
const titleInput = document.getElementById("title");

function showStatus(message, type) {
    statusEl.textContent = message;
    statusEl.className = 'status';
    statusEl.classList.add(type);
}

function openModal() {
    modal.classList.add("show");
    titleInput.focus();
}

function closeModal() {
    modal.classList.remove("show");
    titleInput.value = "";
}

openModalBtn.addEventListener("click", openModal);
closeModalBtn.addEventListener("click", closeModal);

modal.addEventListener("click", (e) => {
    if (e.target === modal) closeModal();
});

async function createSeeker() {
    const title = titleInput.value.trim();

    if (!title) {
        showStatus('Please enter a seeker name', 'error');
        return;
    }

    try {
        const response = await fetch(`${base_api}/api/seeker/create/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title })
        });

        if (!response.ok) {
            throw new Error('Failed to create seeker');
        }

        showStatus('Seeker created successfully!', 'success');

        closeModal();
        loadSeekers();

    } catch (error) {
        showStatus(error.message, 'error');
    }
}

createBtn.addEventListener("click", createSeeker);

function renderSeeker(seeker) {
    const card = document.createElement('a');
    card.className = 'seeker';
    card.href = `/seeker/${seeker.id}/`;

    const title = document.createElement('div');
    title.textContent = seeker.title;

    const date = document.createElement('p');
    date.textContent = `Created: ${new Date(seeker.created_at).toLocaleDateString()}`;

    card.appendChild(title);
    card.appendChild(date);

    return card;
}

async function loadSeekers() {
    try {
        const response = await fetch(`${base_api}/api/seekers/`);

        if (!response.ok) {
            throw new Error('Failed to load seekers');
        }

        const data = await response.json();
        const seekers = data.seekers || [];

        seekersList.innerHTML = '';

        if (seekers.length === 0) {
            seekersList.innerHTML = `
                <div class="empty-state">
                    <img src="/static/images/jobhuner-no-results.png" alt="No seekers yet">
                </div>
            `;
            return;
        }

        seekers.forEach(seeker => {
            seekersList.appendChild(renderSeeker(seeker));
        });

    } catch (error) {
        console.error(error);
        showStatus('Failed to load seekers', 'error');
    }
}

loadSeekers();
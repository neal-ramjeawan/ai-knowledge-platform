import './style.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const uploadStatusEl = document.querySelector('#upload-status');
const searchStatusEl = document.querySelector('#search-status');
const documentsListEl = document.querySelector('#documents-list');
const searchResultsEl = document.querySelector('#search-results');
const uploadForm = document.querySelector('#upload-form');
const searchForm = document.querySelector('#search-form');
const searchInput = document.querySelector('#search-input');
const semanticSearchButton = document.querySelector('#semantic-search-button');

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

async function loadDocuments() {
  try {
    const response = await fetch(`${API_URL}/documents`);
    const data = await response.json();
    const documents = data.documents || [];

    if (!documents.length) {
      documentsListEl.innerHTML = '<div class="card"><p>No documents uploaded yet.</p></div>';
      return;
    }

    documentsListEl.innerHTML = documents
      .map(
        (doc) => `
          <article class="card">
            <h3>${escapeHtml(doc.filename || 'Untitled document')}</h3>
            <div class="meta">Uploaded ${new Date(doc.created_at).toLocaleString()}</div>
            <div class="meta">Type: ${escapeHtml(doc.content_type || 'unknown')}</div>
            <div class="actions">
              <button class="secondary" type="button" data-doc-id="${doc.id}">View chunks</button>
            </div>
            <pre data-preview-for="${doc.id}">Loading chunks…</pre>
          </article>
        `,
      )
      .join('');
  } catch (error) {
    documentsListEl.innerHTML = `<div class="card"><p>Unable to load documents: ${escapeHtml(error.message)}</p></div>`;
  }
}

async function runSearch(endpoint) {
  const query = searchInput.value.trim();
  if (!query) {
    searchStatusEl.textContent = 'Please enter a search query.';
    return;
  }

  searchStatusEl.textContent = 'Searching…';
  try {
    const response = await fetch(`${API_URL}${endpoint}?q=${encodeURIComponent(query)}`);
    const data = await response.json();
    searchResultsEl.textContent = JSON.stringify(data, null, 2);
    searchStatusEl.textContent = 'Search complete.';
  } catch (error) {
    searchStatusEl.textContent = `Search failed: ${error.message}`;
  }
}

uploadForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const fileInput = document.querySelector('#file-input');
  const file = fileInput.files[0];

  if (!file) {
    uploadStatusEl.textContent = 'Please choose a file first.';
    return;
  }

  const formData = new FormData();
  formData.append('file', file);

  uploadStatusEl.textContent = 'Uploading…';
  try {
    const response = await fetch(`${API_URL}/documents/upload`, {
      method: 'POST',
      body: formData,
    });
    const data = await response.json();
    uploadStatusEl.textContent = `Uploaded ${data.chunk_count || 0} chunk(s).`;
    await loadDocuments();
    searchResultsEl.textContent = JSON.stringify(data, null, 2);
    fileInput.value = '';
  } catch (error) {
    uploadStatusEl.textContent = `Upload failed: ${error.message}`;
  }
});

searchForm.addEventListener('submit', (event) => {
  event.preventDefault();
  runSearch('/search');
});

semanticSearchButton.addEventListener('click', () => {
  runSearch('/semantic-search');
});

documentsListEl.addEventListener('click', async (event) => {
  const button = event.target.closest('[data-doc-id]');
  if (!button) {
    return;
  }

  const docId = button.getAttribute('data-doc-id');
  const previewEl = documentsListEl.querySelector(`[data-preview-for="${docId}"]`);
  if (!previewEl) {
    return;
  }

  previewEl.textContent = 'Loading chunks…';
  try {
    const response = await fetch(`${API_URL}/documents/${docId}/chunks`);
    const data = await response.json();
    previewEl.textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    previewEl.textContent = `Unable to load chunks: ${error.message}`;
  }
});

loadDocuments();

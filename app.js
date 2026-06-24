const grid = document.querySelector('#youtube-videos');
const modal = document.querySelector('#video-player-modal');
const frameWrap = document.querySelector('#video-player-frame-wrap');
const modalTitle = document.querySelector('#video-player-title');
const modalYoutube = document.querySelector('#video-player-youtube');
let lastFocusedElement = null;

function openVideo(video) {
  if (!modal || !frameWrap || !modalTitle || !modalYoutube) return;
  lastFocusedElement = document.activeElement;
  const iframe = document.createElement('iframe');
  iframe.className = 'video-player-frame';
  iframe.src = `https://www.youtube.com/embed/${encodeURIComponent(video.id)}?autoplay=1&rel=0&modestbranding=1`;
  iframe.title = video.title;
  iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
  iframe.allowFullscreen = true;
  iframe.referrerPolicy = 'strict-origin-when-cross-origin';
  frameWrap.replaceChildren(iframe);
  modalTitle.textContent = video.title;
  modalYoutube.href = video.url;
  modal.setAttribute('aria-hidden', 'false');
  document.body.classList.add('video-modal-open');
  const closeButton = modal.querySelector('.video-player-close');
  if (closeButton) closeButton.focus();
}

function closeVideo() {
  if (!modal || !frameWrap) return;
  frameWrap.replaceChildren();
  modal.setAttribute('aria-hidden', 'true');
  document.body.classList.remove('video-modal-open');
  if (lastFocusedElement && typeof lastFocusedElement.focus === 'function') lastFocusedElement.focus();
}

function videoCard(video) {
  const card = document.createElement('button');
  card.className = 'video-card';
  card.type = 'button';
  card.setAttribute('aria-label', `Play ${video.title}`);
  card.addEventListener('click', () => openVideo(video));

  const thumbWrap = document.createElement('span');
  thumbWrap.className = 'video-thumb-wrap';

  const image = document.createElement('img');
  image.className = 'video-thumb';
  image.src = video.thumbnail;
  image.alt = '';
  image.loading = 'lazy';

  const play = document.createElement('span');
  play.className = 'video-play';
  play.textContent = '▶';

  const body = document.createElement('span');
  body.className = 'video-card-body';

  const title = document.createElement('span');
  title.className = 'video-title';
  title.textContent = video.title;

  const meta = document.createElement('span');
  meta.className = 'video-meta';
  meta.textContent = video.publishedLabel || 'Recent release';

  thumbWrap.append(image, play);
  body.append(title, meta);
  card.append(thumbWrap, body);
  return card;
}

async function loadVideos() {
  if (!grid) return;
  try {
    const response = await fetch('youtube-videos.json', { cache: 'no-store' });
    if (!response.ok) throw new Error(`Video list unavailable: ${response.status}`);
    const data = await response.json();
    const videos = Array.isArray(data.videos) ? data.videos.slice(0, 10) : [];
    if (!videos.length) throw new Error('No videos found');
    grid.replaceChildren(...videos.map(videoCard));
  } catch (error) {
    grid.innerHTML = '<div class="video-loading">Recent videos could not load here. Use the YouTube button below to view the latest work.</div>';
  }
}

if (modal) {
  modal.addEventListener('click', (event) => {
    if (event.target.closest('[data-close-video]')) closeVideo();
  });
}

if (modalYoutube) {
  modalYoutube.addEventListener('click', () => {
    closeVideo();
  });
}

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && modal && modal.getAttribute('aria-hidden') === 'false') closeVideo();
});

loadVideos();

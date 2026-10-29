document.documentElement.classList.add('js');

const menuButton = document.querySelector('.nav-toggle');
const navigation = document.querySelector('#site-navigation');
if (menuButton && navigation) {
  menuButton.hidden = false;
  const setMenu = (open) => {
    menuButton.setAttribute('aria-expanded', String(open));
    navigation.dataset.open = String(open);
  };
  menuButton.addEventListener('click', () => setMenu(menuButton.getAttribute('aria-expanded') !== 'true'));
  navigation.addEventListener('click', (event) => {
    if (event.target.closest('a')) setMenu(false);
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && menuButton.getAttribute('aria-expanded') === 'true') {
      setMenu(false);
      menuButton.focus();
    }
  });
}

const publicationTools = document.querySelector('.publication-tools');
if (publicationTools) {
  publicationTools.hidden = false;
  const search = document.querySelector('#publication-search');
  const buttons = [...document.querySelectorAll('[data-publication-filter]')];
  const groups = [...document.querySelectorAll('.publication-group')];
  const entries = [...document.querySelectorAll('.publication')];
  const status = document.querySelector('#publication-status');
  const empty = document.querySelector('#no-publications');
  let category = 'all';
  const update = () => {
    const query = search.value.trim().toLocaleLowerCase();
    let count = 0;
    groups.forEach((group) => {
      let groupCount = 0;
      group.querySelectorAll('.publication').forEach((entry) => {
        const matches = (category === 'all' || group.dataset.category === category) && entry.textContent.toLocaleLowerCase().includes(query);
        entry.hidden = !matches;
        if (matches) { count += 1; groupCount += 1; }
      });
      group.hidden = groupCount === 0;
    });
    buttons.forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.publicationFilter === category)));
    status.textContent = `${count} of ${entries.length} outputs${query ? ' matching your search' : ''}`;
    empty.hidden = count > 0;
  };
  buttons.forEach((button) => button.addEventListener('click', () => {
    category = button.dataset.publicationFilter;
    update();
  }));
  search.addEventListener('input', update);
  update();
}

const figureDialog = document.querySelector('#figure-dialog');
if (figureDialog && typeof figureDialog.showModal === 'function') {
  const image = figureDialog.querySelector('.figure-dialog-image');
  const title = figureDialog.querySelector('#figure-dialog-title');
  const caption = figureDialog.querySelector('#figure-dialog-caption');
  const original = figureDialog.querySelector('.figure-original');
  let openedBy;
  document.querySelectorAll('a[data-figure-title]').forEach((link) => {
    link.addEventListener('click', (event) => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      openedBy = link;
      image.src = link.href;
      const thumbnail = link.querySelector('img');
      image.alt = thumbnail.alt;
      image.width = Number(thumbnail.getAttribute('width'));
      image.height = Number(thumbnail.getAttribute('height'));
      title.textContent = link.dataset.figureTitle;
      const sourceCaption = link.closest('figure').querySelector('figcaption');
      caption.replaceChildren(...Array.from(sourceCaption.childNodes, (child) => child.cloneNode(true)));
      original.href = link.href;
      figureDialog.showModal();
    });
  });
  figureDialog.querySelector('.figure-close').addEventListener('click', () => figureDialog.close());
  figureDialog.addEventListener('close', () => openedBy?.focus());
  figureDialog.addEventListener('click', (event) => {
    if (event.target !== figureDialog) return;
    const bounds = figureDialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) figureDialog.close();
  });
}

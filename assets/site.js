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
  const galleryNavigation = figureDialog.querySelector('.figure-gallery-nav');
  const galleryPosition = figureDialog.querySelector('.figure-gallery-position');
  const cmmFigures = [...document.querySelector('#cmm-gallery').content.querySelectorAll('figure')];
  let openedBy;
  let gallery = [];
  let currentFigure = 0;
  const renderFigure = () => {
    const item = gallery[currentFigure];
    image.src = item.src;
    image.alt = item.alt;
    image.width = item.width;
    image.height = item.height;
    title.textContent = item.title;
    caption.replaceChildren(...Array.from(item.caption.childNodes, (child) => child.cloneNode(true)));
    original.href = item.src;
    galleryNavigation.hidden = gallery.length < 2;
    galleryPosition.textContent = `Figure ${currentFigure + 1} of ${gallery.length}`;
    figureDialog.scrollTop = 0;
  };
  const moveFigure = (direction) => {
    currentFigure = (currentFigure + direction + gallery.length) % gallery.length;
    renderFigure();
  };
  document.querySelectorAll('a[data-figure-title]').forEach((link) => {
    link.addEventListener('click', (event) => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      openedBy = link;
      const thumbnail = link.querySelector('img');
      gallery = [{
        src: link.href, alt: thumbnail.alt,
        width: Number(thumbnail.getAttribute('width')), height: Number(thumbnail.getAttribute('height')),
        title: link.dataset.figureTitle, caption: link.closest('figure').querySelector('figcaption'),
      }];
      if (link.dataset.figureGallery === 'cmm') {
        gallery.push(...cmmFigures.map((figure) => {
          const figureImage = figure.querySelector('img');
          return {
            src: figureImage.dataset.src, alt: figureImage.alt,
            width: Number(figureImage.getAttribute('width')), height: Number(figureImage.getAttribute('height')),
            title: figure.dataset.figureTitle, caption: figure.querySelector('figcaption'),
          };
        }));
      }
      currentFigure = 0;
      renderFigure();
      figureDialog.showModal();
    });
  });
  figureDialog.querySelector('.figure-close').addEventListener('click', () => figureDialog.close());
  figureDialog.querySelector('.figure-previous').addEventListener('click', () => moveFigure(-1));
  figureDialog.querySelector('.figure-next').addEventListener('click', () => moveFigure(1));
  figureDialog.addEventListener('keydown', (event) => {
    if (gallery.length < 2) return;
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault();
      moveFigure(event.key === 'ArrowLeft' ? -1 : 1);
    }
  });
  let swipeStart;
  image.addEventListener('pointerdown', (event) => {
    if (event.pointerType !== 'mouse') swipeStart = { x: event.clientX, y: event.clientY };
  });
  image.addEventListener('pointercancel', () => { swipeStart = undefined; });
  image.addEventListener('pointerup', (event) => {
    if (!swipeStart) return;
    const dx = event.clientX - swipeStart.x;
    const dy = event.clientY - swipeStart.y;
    swipeStart = undefined;
    if (gallery.length > 1 && Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy) * 1.4) moveFigure(dx < 0 ? 1 : -1);
  });
  figureDialog.addEventListener('close', () => openedBy?.focus());
  figureDialog.addEventListener('click', (event) => {
    if (event.target !== figureDialog) return;
    const bounds = figureDialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) figureDialog.close();
  });
}

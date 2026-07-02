/* clo-author HTML Report Components */

(function() {
  'use strict';

  /* Tabs */
  document.querySelectorAll('.tab').forEach(function(btn) {
    btn.addEventListener('click', function() {
      var group = btn.closest('.tab-bar').parentElement;
      group.querySelectorAll('.tab').forEach(function(b) { b.classList.remove('active'); });
      group.querySelectorAll('.tab-content').forEach(function(s) { s.classList.remove('active'); });
      btn.classList.add('active');
      var target = document.getElementById(btn.getAttribute('data-target'));
      if (target) target.classList.add('active');
    });
  });

  /* Collapsibles */
  document.querySelectorAll('.collapsible-header').forEach(function(header) {
    header.addEventListener('click', function() {
      header.classList.toggle('open');
      var body = header.nextElementSibling;
      if (body && body.classList.contains('collapsible-body')) {
        body.classList.toggle('open');
      }
    });
  });

  /* Dark mode toggle */
  var darkToggle = document.getElementById('dark-toggle');
  if (darkToggle) {
    var saved = localStorage.getItem('clo-theme');
    if (saved === 'dark') document.documentElement.classList.add('dark');
    else if (saved === 'light') document.documentElement.classList.remove('dark');

    darkToggle.addEventListener('click', function() {
      var isDark = document.documentElement.classList.toggle('dark');
      localStorage.setItem('clo-theme', isDark ? 'dark' : 'light');
      darkToggle.textContent = isDark ? 'Light' : 'Dark';
    });
  }

  /* Print */
  var printBtn = document.getElementById('print-btn');
  if (printBtn) {
    printBtn.addEventListener('click', function() { window.print(); });
  }

  /* Copy to clipboard */
  document.querySelectorAll('.copy-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      var text = btn.getAttribute('data-copy');
      if (!text) {
        var target = document.getElementById(btn.getAttribute('data-copy-from'));
        if (target) text = target.textContent;
      }
      if (text) {
        navigator.clipboard.writeText(text).then(function() {
          var orig = btn.textContent;
          btn.textContent = 'Copied!';
          btn.classList.add('copied');
          setTimeout(function() {
            btn.textContent = orig;
            btn.classList.remove('copied');
          }, 1500);
        });
      }
    });
  });

  /* Filter engine */
  var filterBar = document.querySelector('.filter-bar');
  if (filterBar) {
    var cards = document.querySelectorAll('[data-filterable]');
    var searchInput = filterBar.querySelector('.filter-search');
    var filterBtns = filterBar.querySelectorAll('.filter-btn');

    function applyFilters() {
      var activeFilters = [];
      filterBtns.forEach(function(b) {
        if (b.classList.contains('active')) activeFilters.push(b.getAttribute('data-filter'));
      });
      var query = searchInput ? searchInput.value.toLowerCase().trim() : '';
      var shown = 0;

      cards.forEach(function(card) {
        var matchFilter = activeFilters.length === 0 ||
          activeFilters.some(function(f) { return card.getAttribute('data-category') === f || card.getAttribute('data-proximity') === f; });
        var matchSearch = !query ||
          (card.textContent || '').toLowerCase().indexOf(query) !== -1;
        var visible = matchFilter && matchSearch;
        card.style.display = visible ? '' : 'none';
        if (visible) shown++;
      });

      var counter = document.getElementById('filter-count');
      if (counter) counter.textContent = 'Showing ' + shown + ' of ' + cards.length;
    }

    filterBtns.forEach(function(btn) {
      btn.addEventListener('click', function() {
        btn.classList.toggle('active');
        applyFilters();
      });
    });

    if (searchInput) {
      searchInput.addEventListener('input', applyFilters);
    }
  }

  /* Smooth scroll for nav links */
  document.querySelectorAll('a[href^="#"]').forEach(function(link) {
    link.addEventListener('click', function(e) {
      var target = document.querySelector(link.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

})();

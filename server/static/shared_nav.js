(function() {
    var navItems = [
        { path: '/static/all_time.html', label: 'All Time Data' },
        { path: '/static/day_data_unified.html', label: 'Day Data' },
        { path: '/static/monthly_comparison.html', label: 'Monthly Data' },
        { path: '/static/year_over_year_by_day.html', label: 'Year Over Year' },
        { path: '/static/battery_simulator.html', label: 'Battery Simulator' }
    ];

    var currentPath = window.location.pathname;

    var excludedPaths = ['/static/main.html'];
    for (var i = 0; i < excludedPaths.length; i++) {
        if (currentPath === excludedPaths[i]) {
            return;
        }
    }

    document.addEventListener('DOMContentLoaded', function() {
        var navEl = document.createElement('nav');
        navEl.className = 'top-nav';

        var ulEl = document.createElement('ul');

        for (var i = 0; i < navItems.length; i++) {
            var liEl = document.createElement('li');
            var aEl = document.createElement('a');
            aEl.href = navItems[i].path;
            aEl.textContent = navItems[i].label;
            
            if (currentPath === navItems[i].path) {
                liEl.className = 'active';
            }
            
            liEl.appendChild(aEl);
            ulEl.appendChild(liEl);
        }

        navEl.appendChild(ulEl);

        var body = document.body;
        if (body) {
            body.insertBefore(navEl, body.firstChild);
        }
    });
})();

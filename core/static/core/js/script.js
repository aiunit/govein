(function () {
    var grid = [];
    for (var i = 0; i < 19; ++i) {
        var row = [];
        for (var j = 0; j < 19; ++j) {
            row.push(0);
        }
        grid.push(row);
    }
    window.app = new Vue({
        el: '#app',
        data: {
            auto: true,
            player: 1,
            grid: grid
        },
        methods: {
            isStar: function (r, c) {
                return (r == 3 || r == 9 || r == 15)
                    && (c == 3 || c == 9 || c == 15);
            }
        }
    });
})();



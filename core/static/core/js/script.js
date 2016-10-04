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
            draw: function () {
                var str = '';
                for (var i = 0; i < this.grid.length; ++i) {
                    for (var j = 0; j < this.grid[i].length; ++j) {
                        str += '.xo'[this.grid[i][j]];
                    }
                    str += '\n';
                }
                console.log(str);
            },
            go: function (r, c) {
                console.log('go(' + r + ', ' + c + ')');
                if (this.grid[r][c]) return false;
                this.grid[r][c] = this.player;
                this.grid[r].splice(c, 1, this.player);
                if (this.auto) this.player = 3 - this.player;
                this.draw();
            },
            isStar: function (r, c) {
                return (r == 3 || r == 9 || r == 15)
                    && (c == 3 || c == 9 || c == 15);
            }
        }
    });
})();



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
            label:{
                x: [
                    19, 18, 17, 16,
                    15, 14, 13, 12, 11,
                    10, 9, 8, 7, 6,
                    5, 4, 3, 2, 1
                ],
                y: 'ABCDEFGHJKLMNOPQRST'
            },
            autoSwitch: true,
            player: 1,
            grid: grid,
            rob: {
                x: -1,
                y: -1
            },
            history: [],
            history_cursor: -1
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
            prev: function () {
                if (this.history_cursor < 0) return false;
                var history = this.history[this.history_cursor--];
                this.go(
                    history.x,
                    history.y,
                    history.old_val,
                    true
                );
            },
            next: function () {
                if (this.history_cursor >= this.history.length - 1) return false;
                var history = this.history[++this.history_cursor];
                this.go(
                    history.x,
                    history.y,
                    history.new_val,
                    true
                );
            },
            go: function (x, y, action, nolog) {

                console.log('go(' + x + ', ' + y + ')');

                if (typeof(action) === 'undefined') {
                    action = parseInt(this.player);
                }

                if (action && this.grid[x][y]) {
                    return false;
                }

                var log = {
                    x: x,
                    y: y,
                    old_val: this.grid[x][y],
                    new_val: action
                };

                this.grid[x].splice(y, 1, action);

                if (!nolog) {

                    if (action && this.autoSwitch) {
                        this.player = 3 - action;
                    }

                    this.history.splice(
                        this.history_cursor,
                        this.history.length - 1 - this.history_cursor
                    );

                    this.history.push(log);

                    this.history_cursor = this.history.length - 1;

                }

                this.draw();
            },
            isStar: function (x, y) {
                return (x == 3 || x == 9 || x == 15)
                    && (y == 3 || y == 9 || y == 15);
            },
            applyCapture: function () {

            }
        }
    });
})();



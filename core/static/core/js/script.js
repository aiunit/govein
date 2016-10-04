(function () {
    var grid = [];
    for (var i = 0; i < 19; ++i) {
        var row = [];
        for (var j = 0; j < 19; ++j) {
            row.push(0);
        }
        grid.push(row);
    }
    var vm = window.app = new Vue({
        el: '#app',
        data: {
            label: {
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
                for (var i = 0; i < vm.grid.length; ++i) {
                    for (var j = 0; j < vm.grid[i].length; ++j) {
                        str += '.xo'[vm.grid[i][j]];
                    }
                    str += '\n';
                }
                console.log(str);
            },
            prev: function () {
                if (vm.history_cursor < 0) return false;
                var log = vm.history[vm.history_cursor--];
                vm.go(
                    log.x,
                    log.y,
                    log.old_val,
                    true
                );
                // 填回提子
                for (var i = 0; i < log.captured.length; ++i) {
                    var c = log.captured[i];
                    vm.grid[c.x].splice(c.y, 1, c.val);
                }
            },
            next: function () {
                if (vm.history_cursor >= vm.history.length - 1) return false;
                var log = vm.history[++vm.history_cursor];
                vm.go(
                    log.x,
                    log.y,
                    log.new_val,
                    true
                );
            },
            go: function (x, y, action, nolog) {

                if (typeof(action) === 'undefined') {
                    action = parseInt(vm.player);
                }

                if (action && vm.grid[x][y]) return false;

                var i;

                var log = {
                    x: x,
                    y: y,
                    old_val: vm.grid[x][y],
                    new_val: action
                };

                vm.grid[x].splice(y, 1, action);

                log.captured = vm.getCapturedStones(action);

                // 如果提不掉别人，自己却被提掉，即为自杀，禁入。
                if (!log.captured.length) {
                    var beCaptured = vm.getCapturedStones(3 - action);
                    var isCaptured = false;
                    for (i = 0; i < beCaptured.length; ++i) {
                        if (beCaptured[i].x === x && beCaptured[i].y === y) {
                            isCaptured = true;
                        }
                    }
                    if (isCaptured) {
                        vm.grid[x].splice(y, 1, log.old_val);
                        return false;
                    }
                }

                // 清除提子
                for (i = 0; i < log.captured.length; ++i) {
                    var c = log.captured[i];
                    vm.grid[c.x].splice(c.y, 1, 0);
                }

                if (!nolog) {
                    if (action && vm.autoSwitch) {
                        vm.player = 3 - action;
                    }
                    vm.history.splice(
                        vm.history_cursor,
                        vm.history.length - 1 - vm.history_cursor
                    );
                    vm.history.push(log);
                    vm.history_cursor = vm.history.length - 1;
                }

                vm.draw();
                return true;
            },
            isStar: function (x, y) {
                return (x == 3 || x == 9 || x == 15)
                    && (y == 3 || y == 9 || y == 15);
            },
            getCapturedStones: function (action) {

                // default action
                if (typeof(action) === 'undefined') {
                    return false;
                }

                // 19x19, unvisit: -1, pending: -2, live: 1, dead: 0
                var cgrid = [], i, j;
                for (i = 0; i < 19; ++i) {
                    var row = [];
                    for (j = 0; j < 19; ++j) {
                        row.push(-1);
                    }
                    cgrid.push(row);
                }

                var isAlive = function (x, y) {
                    // out of bound has no liberty, equal to death.
                    if (x < 0 || x >= 19 || y < 0 || y >= 19) return 0;
                    // if visited, return directly.
                    if (cgrid[x][y] !== -1) return cgrid[x][y];
                    // empty liberties are alive.
                    if (vm.grid[x][y] === 0) return cgrid[x][y] = 1;
                    // opportunity's liberties are dead.
                    if (vm.grid[x][y] === action) return cgrid[x][y] = 0;
                    // else, mark as pending
                    cgrid[x][y] = -2;
                    // depth first search
                    var dx = [1, 0, -1, 0];
                    var dy = [0, 1, 0, -1];
                    for (var d = 0; d < 4; ++d) {
                        x += dx[d];
                        y += dy[d];
                        if (isAlive(x, y) === 1) {
                            return cgrid[x - dx[d]][y - dy[d]] = 1;
                        }
                        x -= dx[d];
                        y -= dy[d];
                    }
                    return cgrid[x][y] = 0;
                };

                // 处理提子
                var deadStones = [];
                for (i = 0; i < 19; ++i) {
                    for (j = 0; j < 19; ++j) {
                        if (!isAlive(i, j) && vm.grid[i][j] == 3 - action) {
                            deadStones.push({x: i, y: j, val: 3 - action});
                        }
                    }
                }

                return deadStones;

            }
        }
    });
})();



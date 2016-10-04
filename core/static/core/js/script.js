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
            action: 1,
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
                // 恢复劫争禁入点
                vm.rob = {x: log.rob.x, y: log.rob.y};
                // 切换角色
                if (log.new_val && vm.autoSwitch) {
                    vm.action = log.new_val;
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
                // 恢复劫争禁入点
                vm.rob = {x: log.rob.x, y: log.rob.y};
                // 切换角色
                if (log.new_val && vm.autoSwitch) {
                    vm.action = 3 - log.new_val;
                }
            },
            getLabel: function (x, y) {
                return vm.label.x[x] + vm.label.y[y];
            },
            go: function (x, y, action, nolog) {

                if (typeof(action) === 'undefined') {
                    action = parseInt(vm.action);
                }

                // 如果已经有子，禁入
                if (action && vm.grid[x][y]) {
                    console.log(vm.getLabel(x, y) + ': 禁入点，已经有子');
                    return false;
                }

                // 如果正好打在劫争禁入点，禁入
                if (x === vm.rob.x && y === vm.rob.y) {
                    console.log(vm.getLabel(x, y) + ': 禁入点，劫争');
                    return false;
                }

                var i;

                var log = {
                    x: x,
                    y: y,
                    old_val: vm.grid[x][y],
                    new_val: action
                };

                vm.grid[x].splice(y, 1, action);

                // 对方没有气的子
                var captured = vm.getCapturedStones(action);
                // 我方没有气的子
                var beCaptured = vm.getCapturedStones(3 - action);

                // 如果提不掉别人，自己却被提掉，即为自杀，禁入。
                if (!captured.length) {
                    var isCaptured = false;
                    for (i = 0; i < beCaptured.length; ++i) {
                        if (beCaptured[i].x === x && beCaptured[i].y === y) {
                            isCaptured = true;
                        }
                    }
                    if (isCaptured) {
                        vm.grid[x].splice(y, 1, log.old_val);
                        console.log(vm.getLabel(x, y) + ': 禁入点，不能自杀');
                        return false;
                    }
                }

                // 处理劫争，互相咬住一子即为有劫
                if (captured.length === 1 && beCaptured.length === 1) {
                    vm.rob = {
                        x: captured[0].x,
                        y: captured[0].y
                    };
                } else {
                    // 清除劫争禁入状态
                    vm.rob = {x: -1, y: -1};
                }

                // 记录并清除提子
                log.captured = captured;
                log.rob = {x: vm.rob.x, y: vm.rob.y};
                for (i = 0; i < captured.length; ++i) {
                    var c = captured[i];
                    vm.grid[c.x].splice(c.y, 1, 0);
                }

                if (!nolog) {
                    if (action && vm.autoSwitch) {
                        vm.action = 3 - action;
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

                var collected = [];
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
                    // 被 collect 的点如果搜索死了可以被同一次搜索成功的部分复活
                    collected.push({x: x, y: y});
                    //console.log('spy: ' + vm.getLabel(x, y));
                    // depth first search
                    var dx = [1, 0, -1, 0];
                    var dy = [0, 1, 0, -1];
                    for (var d = 0; d < 4; ++d) {
                        x += dx[d];
                        y += dy[d];
                        //console.log(vm.getLabel(x, y), isAlive(x, y));
                        if (isAlive(x, y) === 1) {
                            cgrid[x - dx[d]][y - dy[d]] = 1;
                            while(collected.length) {
                                var pos = collected.pop();
                                cgrid[pos.x][pos.y] = 1;
                            }
                            return 1;
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
                        collected = [];
                        if (!isAlive(i, j) && vm.grid[i][j] == 3 - action) {
                            deadStones.push({x: i, y: j, val: 3 - action});
                        }
                    }
                }
                //console.log(cgrid);

                return deadStones;

            }
        }
    });
})();



(function () {

    var vm = window.app = new Vue({
        el: '#app',
        data: {
            label: {
                x: [1, 2, 3, 4, 5,
                    6, 7, 8, 9, 10,
                    11, 12, 13, 14, 15,
                    16, 17, 18, 19
                ],
                y: 'ABCDEFGHJKLMNOPQRST'
            },
            autoSwitch: true,
            action: 1,
            grid: null,
            rob: null,
            history: null,
            history_cursor: 0
        },
        computed: {
            pos: function () {
                return vm.history ? {
                    x: vm.history[vm.history_cursor].x,
                    y: vm.history[vm.history_cursor].y
                } : {x: -1, y: -1};
            }
        },
        methods: {
            //draw: function () {
            //    var str = '';
            //    for (var i = 0; i < vm.grid.length; ++i) {
            //        for (var j = 0; j < vm.grid[i].length; ++j) {
            //            str += '.xo'[vm.grid[i][j]];
            //        }
            //        str += '\n';
            //    }
            //    console.log(str);
            //},
            /**
             * 恢复历史位置
             * 1. 如果缺省 index，恢复最新的历史位置
             * 2. 如果指定 index = -1，恢复棋盘初始位置并且清空历史
             * 3. 否则，移动到某个历史状态
             */
            restore: function (index) {
                // default value for index
                if (typeof index === 'undefined') {
                    index = vm.history_cursor;
                } else {
                    vm.history_cursor = index
                }
                var log = vm.history[index];
                vm.grid = utils.grid(log.data);
                vm.x = log.x;
                vm.y = log.y;
                vm.rob = log.rob;
                // 如果是第 0 步，总是该黑子下
                vm.action = index ? log.action : 2;

                if (vm.action && vm.autoSwitch) {
                    vm.action = 3 - vm.action;
                }
            },
            prev: function () {
                if (vm.history_cursor <= 0) return false;
                vm.restore(vm.history_cursor - 1);
            },
            next: function () {
                if (vm.history_cursor >= vm.history.length - 1) return false;
                vm.restore(vm.history_cursor + 1);
            },
            /**
             * 翻转棋盘
             */
            flip: function () {
                utils.flip(vm.grid);
                vm.grid = JSON.parse(JSON.stringify(vm.grid));
                vm.action = vm.action ? 3 - vm.action : vm.action;
            },
            getLabel: function (x, y) {
                if (x < 0 || y < 0) return '-';
                return vm.label.y[y] + vm.label.x[x];
            },
            /**
             * 落子操作
             * @param x
             * @param y
             * @param action
             * @param nolog boolean 是否忽略历史记录
             * @returns {boolean}
             */
            go: function (x, y, action, nolog) {

                if (typeof(action) === 'undefined') {
                    action = parseInt(vm.action);
                }

                // 如果已经有子，禁入
                if (action && vm.grid[x][y]) {
                    console.log(vm.getLabel(x, y) + ': 禁入点，已经有子');
                    return false;
                }

                // 无子可以擦除
                if (!action && !vm.grid[x][y]) {
                    console.log(vm.getLabel(x, y) + ': 这里没有棋子可以擦除');
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
                    action: action
                };

                // 放入或者移除棋子
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
                        //vm.grid[x].splice(y, 1, log.old_val);
                        vm.restore();
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
                    var grid = JSON.parse(JSON.stringify(vm.grid));
                    // 如果刚刚下子的是黑子，马上翻转棋盘
                    if (vm.action === 1) utils.flip(grid);
                    vm.$http.post('/spy/', JSON.stringify({
                        grid: grid,
                        rob: [log.rob.x, log.rob.y]
                    })).then(function (resp) {
                        var data = JSON.parse(resp.body);
                        console.log('SPY', data.id);
                        log.id = data.id;
                        log.store = data.store;
                        log.data = utils.getDataFromGrid(vm.grid);
                        if (action && vm.autoSwitch) {
                            vm.action = 3 - action;
                        }
                        // 清除掉当前历史位置后面的所有记录并且插入一条
                        vm.history.splice(
                            vm.history_cursor + 1,
                            vm.history.length - 1 - vm.history_cursor,
                            log
                        );
                        vm.history_cursor = vm.history.length - 1;
                    });
                }

                //vm.draw();
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

                // 19x19, not-visit: -1, pending: -2, live: 1, dead: 0
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
                            while (collected.length) {
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

            },
            submit: function () {
                // 因为默认黑先，所以如果该白走，需要将所有棋子翻转
                var grid = JSON.parse(JSON.stringify(vm.grid));
                if (vm.action === 2) utils.flip(grid);
                // 发送请求
                vm.$http.post(
                    '/submit/',
                    JSON.stringify({
                        grid: grid,
                        rob: [vm.rob.x, vm.rob.y]
                    })
                ).then(function (resp) {
                    console.log(resp.body);
                });
            }
        },
        ready: function () {

            // set the initial grid
            var el = document.getElementById('init_data');
            this.grid = el.value ?
                JSON.parse(el.value) : utils.grid();

            // set the initial rob position
            this.rob = {
                x: parseInt(el.getAttribute('data-rob-x') || -1),
                y: parseInt(el.getAttribute('data-rob-y') || -1)
            };

            // set the base history stack
            var log = {
                x: -1, y: -1, action: 0, captured: [],
                data: utils.getDataFromGrid(this.grid),
                rob: JSON.parse(JSON.stringify(this.rob))
            };
            this.$http.post('/spy/', JSON.stringify({
                grid: this.grid,
                rob: [this.rob.x, this.rob.y]
            })).then(function (resp) {
                var data = JSON.parse(resp.body);
                console.log('SPY', data.id);
                log.id = data.id;
                log.store = data.store;
                this.history_cursor = 0;
                this.history = [log];
            });

        }
    });
})();



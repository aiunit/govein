var utils = {};

// Board state data length
// 1 position = 2 bits
// 1 byte = 4 positions
// 1 state = 19 * 19 positions = 90.25 bytes.
// So use 91 byte to store the data
const DATA_LENGTH = 91;

/**
 * 通过棋盘网格值获取二进制串
 */
utils.getDataFromGrid = function (grid) {

    // Empty data array
    var i, j, z, data = [];
    for (i = 0; i < DATA_LENGTH; ++i) {
        data.push(0);
    }

    // Fill in the data
    for (i = 0; i < 19; ++i) {
        for (j = 0; j < 19; ++j) {
            z = i * 19 + j;
            data[z >> 2] += (grid[i][j] << (z % 4 * 2));
        }
    }

    // Generates the string and return
    for (i = 0; i < DATA_LENGTH; ++i) {
        data[i] = String.fromCharCode(data[i]);
    }
    return data.join('');

};

/**
 * Generates a grid (2-D Array) with given data.
 * @param data string: Must be a binary string of data (length = 91)
 * @returns {Array}
 */
utils.grid = function (data) {

    // Generates an empty grid
    var grid = [];
    for (i = 0; i < 19; ++i) {
        var row = [];
        for (j = 0; j < 19; ++j) {
            row.push(0);
        }
        grid.push(row);
    }

    // If data specified, fill in the grid.
    if (data) {
        // Check if the data string is legal.
        if (data.length !== DATA_LENGTH) {
            throw Error('Grid construction with a error data string');
        }
        // Fill in the grid
        var i, j, z;
        for (i = 0; i < 19; ++i) {
            for (j = 0; j < 19; ++j) {
                z = i * 19 + j;
                grid[i][j] = (data.charCodeAt(z >> 2) >> (z % 4 * 2)) % 4;
            }
        }
    }

    return grid;

};

/**
 * 将所有黑白棋子翻转
 * @param grid
 */
utils.flip = function (grid) {
    for (var i = 0; i < grid.length; ++i) {
        for (var j = 0; j < grid[i].length; ++j) {
            grid[i][j] = grid[i][j] && 3 - grid[i][j];
        }
    }
    return grid;
};

/**
 *
 * @param grid
 * @param action
 */
utils.autoFlip = function (grid, action) {
    grid = JSON.parse(JSON.stringify(grid));
    if (!action || action === 1) {
        return grid;
    } else if (action === 2) {
        return utils.flip(grid);
    }
    throw new Error('参数错误');
};

/**
 * 通过 SPY 获取 Log
 */
utils.spy = function (grid, pos, rob, action, captured) {
    return Vue.http.post('/spy/', JSON.stringify({
        grid: utils.autoFlip(grid, action),
        rob: [rob.x, rob.y]
    })).then(function (resp) {
        var data = JSON.parse(resp.body);
        console.log('SPY', data.id);
        return {
            x: pos.x,
            y: pos.y,
            action: action,
            captured: captured || [],
            data: utils.getDataFromGrid(grid),
            rob: {x: rob.x, y: rob.y},
            id: data.id,
            store: data.store,
            comments: []
        };
    }).then(function(log) {
        // TODO: 在这里读取相关的评论
        return log;
    });
};

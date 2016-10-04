from django.db import models


class BoardState(models.Model):
    """
    chess-board state
    """
    id = models.CharField(
        max_length=40,
        primary_key=True,
        help_text='SHA1 hash for the board state',
    )

    rob_x = models.SmallIntegerField(
        verbose_name='Rob position x index',
        default=-1,
    )

    rob_y = models.SmallIntegerField(
        verbose_name='Rob position y index',
        default=-1,
    )

    DATA_EMPTY_BOARD = b'\0' * 91

    # The board state data, stores all the 19x19 grid state.
    # Every 2 bit represents a position, 0: empty, 1: Black and 2: White.
    # So all storage space is: 361 * 2bit = 90.25 bytes
    data = models.BinaryField(
        max_length=91,
        default=DATA_EMPTY_BOARD,
    )

    class Meta:
        db_table = 'go_core_board_state'
        verbose_name = 'Board State'
        verbose_name_plural = 'Board States'

    def __str__(self):
        result = '<Board: {}>\n'.format(id)
        grid = self.to_grid()
        for i in range(19):
            for j in range(19):
                result += ' xo#'[grid[i][j]]
            result += '\n'
        return result

    def save(self, *args, **kwargs):
        if not kwargs.get('skip_normalize'):
            self.normalize()
        super().save(*args, **kwargs)

    def rob(self):
        return self.rob_x, self.rob_y

    @staticmethod
    def get_data_from_grid(grid):
        b = bytearray(BoardState.DATA_EMPTY_BOARD)
        for i in range(19):
            for j in range(19):
                z = i * 19 + j
                b[z // 4] += (grid[i][j] << z % 4)
        return bytes(b)

    @staticmethod
    def get_grid_from_data(data):
        grid = [[0] * 19] * 19
        for i in range(19):
            for j in range(19):
                z = i * 19 + j
                byte = data[z // 4]
                grid[i][j] = (byte >> z * 2) & 3
        return grid

    @staticmethod
    def get_key_from_data(data, rob=(-1, -1)):
        import hashlib
        sha1 = hashlib.sha1(data + bytes(rob))
        return sha1.hexdigest()

    @staticmethod
    def transform(data, mode, rob=None):
        """
        Transform a set of board data (byte string) with an isomorphism way.
        :param data: The board state data before transform
        :param mode: The transform mode.
            Assume mode is a 3-bit mode binary explained as: 0bwxyz:
            Then the meaning of the bit are:
            * x: transposition the matrix.
            * yz: rotates the matrix 90-degree clockwise 0-3 times.
            note: we do transposition before rotation.
        :param rob: 2-val tuple of rob position,
            if given, returns the new rob position.
        :return: tuple of (data, rob) if rob is not None else data only
        """
        rob_x = rob[0] if rob else -1
        rob_y = rob[1] if rob else -1
        grid = BoardState.get_grid_from_data(data)
        if mode & 0b100:
            grid = list(zip(*grid))
            rob_x, rob_y = rob_y, rob_x
        for i in range(mode & 0b011):
            # http://stackoverflow.com/a/496056/2544762
            grid = list(zip(*grid[::-1]))
            rob_x, rob_y = rob_y, 18 - rob_x
        data = BoardState.get_data_from_grid(grid)
        return (data, (rob_x, rob_y)) if rob else data

    def to_grid(self):
        return self.get_grid_from_data(self.grid)

    @staticmethod
    def from_grid(grid, rob=(-1, -1)):
        return BoardState.from_data(BoardState.get_data_from_grid(grid), rob)

    @staticmethod
    def from_data(data, rob=(-1, -1)):
        bs = BoardState(
            data=data,
            rob_x=rob[0],
            rob_y=rob[1],
        )
        bs.normalize()
        objects = BoardState.objects.filter(id=bs.id)
        if objects.exists():
            return objects.first()
        bs.save(skip_normalize=True)
        return bs

    def normalize(self):
        self.data, (self.rob_x, self.rob_y) = min([BoardState.transform(
            self.data, mode, self.rob()
        ) for mode in range(8)])
        self.id = self.get_key_from_data(self.data, self.rob())

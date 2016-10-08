from django.db import models
from django.contrib.auth.models import User, Group


class UserOwnedModel(models.Model):
    author = models.ForeignKey(
        verbose_name='Author',
        to=User,
        related_name='%(class)ss',
    )

    time_created = models.DateTimeField(
        verbose_name='Created',
        auto_now_add=True,
    )

    time_updated = models.DateTimeField(
        verbose_name='Updated',
        auto_now=True,
    )

    class Meta:
        abstract = True


class Comment(UserOwnedModel):
    content = models.TextField(
        verbose_name='Content',
    )

    class Meta:
        db_table = 'go_core_comment'
        verbose_name = 'Comment'
        verbose_name_plural = 'Comment'


class CommentAvailableModel(models.Model):
    comments = models.ManyToManyField(
        verbose_name='Comments',
        to=Comment,
        related_name='%(class)ss',
    )

    class Meta:
        abstract = True


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Name',
        max_length=255,
    )

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        db_table = 'go_core_tag'

    def __str__(self):
        return self.name


class TagAvailableModel(models.Model):
    tags = models.ManyToManyField(
        verbose_name='Tags',
        to=Tag,
        related_name='%(class)ss'
    )

    class Meta:
        abstract = True


class BoardState(UserOwnedModel,
                 CommentAvailableModel,
                 TagAvailableModel):
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
        # result = '<Board: {}>\n'.format(self.id)
        # grid = self.to_grid()
        # for i in range(19):
        #     for j in range(19):
        #         result += '.xo#'[grid[i][j]]
        #     result += '\n'
        # return result
        return self.id[:6]

    def save(self, *args, **kwargs):
        if not kwargs.get('skip_normalize'):
            self.normalize()
        else:
            del kwargs['skip_normalize']
        print(self.id)
        super().save(*args, **kwargs)

    def get_preview_image_bytes(self):
        """
        :return: ByteArray
        """

        import io
        from PIL import Image, ImageDraw

        sz = 99
        board_fill = (222, 184, 135)
        image = Image.new('RGB', (sz, sz), board_fill)
        draw = ImageDraw.Draw(image, 'RGBA')

        # Board lines
        line_fill = (0, 0, 0)
        for i in range(4, sz, 5):
            draw.line((4, i, 94, i), fill=line_fill)
            draw.line((i, 4, i, 94), fill=line_fill)

        # Stars
        star_fill = (0, 0, 0, 84)
        for i in range(4 + 5 * 3, sz, 5 * 6):
            for j in range(4 + 5 * 3, sz, 5 * 6):
                draw.rectangle([i - 1, j - 1, i + 1, j + 1], fill=star_fill)

        # Stones
        grid = self.to_grid()
        white_fill = (255, 255, 255)
        black_fill = (0, 0, 0)
        for i in range(19):
            for j in range(19):
                if not grid[i][j]:
                    continue
                fill = [None, black_fill, white_fill][grid[i][j]]
                xy = (j * 5 + 2, i * 5 + 2, j * 5 + 6, i * 5 + 6)
                draw.ellipse(xy, fill)

        # Rob position
        rob_fill = (255, 0, 0)
        if self.rob_x >= 0 and self.rob_y >= 0:
            x = 4 + 5 * self.rob_x
            y = 4 + 5 * self.rob_y
            draw.line((y - 2, x, y + 2, x), fill=rob_fill)
            draw.line((y, x - 2, y, x + 2), fill=rob_fill)

        # Output the image streaming
        fs = io.BytesIO()
        image.save(fs, 'gif')
        return fs.getbuffer()

    def preview_url(self):
        from django.core.urlresolvers import reverse
        return reverse('preview', kwargs=dict(pk=self.id))

    def preview_html_tag(self):
        return r'<img src="{}"/>'.format(self.preview_url()) \
            if self.id else ''

    preview_html_tag.short_description = 'Preview'
    preview_html_tag.allow_tags = True

    def hex(self):
        return self.data.hex()

    hex.short_description = 'Data'
    hex.allow_tags = True

    def get_rob_label(self):
        return self.get_label(self.rob_x, self.rob_y)

    get_rob_label.short_description = 'Rob Position'
    get_rob_label.allow_tags = True

    def rob(self):
        return self.rob_x, self.rob_y

    @staticmethod
    def get_label(x, y):
        label_x = list(map(str, range(1, 20))) + ['-']
        label_y = 'ABCDEFGHJKLMNOPQRST-'
        return '{}{}'.format(label_y[y], label_x[x])

    @staticmethod
    def get_data_from_grid(grid):
        b = bytearray(BoardState.DATA_EMPTY_BOARD)
        for i in range(19):
            for j in range(19):
                z = i * 19 + j
                b[z // 4] += (grid[i][j] << (z % 4 * 2))
        return bytes(b)

    @staticmethod
    def get_grid_from_data(data):
        grid = [[0] * 19 for i in range(19)]
        for i in range(19):
            for j in range(19):
                z = i * 19 + j
                byte = data[z // 4]
                grid[i][j] = (byte >> (z % 4 * 2)) % 4
        return grid

    @staticmethod
    def get_key_from_data(data, rob=(-1, -1)):
        import hashlib
        sha1 = hashlib.sha1(
            data + bytes(map(lambda x: 255 if x < 0 else x, rob)))
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
        for i in range(mode % 4):
            # http://stackoverflow.com/a/496056/2544762
            grid = list(zip(*grid[::-1]))
            if rob_x >= 0 or rob_y >= 0:
                rob_x, rob_y = rob_y, len(grid) - 1 - rob_x
        data = BoardState.get_data_from_grid(grid)
        # print(data, (rob_x, rob_y))
        return (data, (rob_x, rob_y)) if rob else data

    def to_grid(self):
        return self.get_grid_from_data(self.data)

    @staticmethod
    def from_grid(grid, author, rob=(-1, -1)):
        return BoardState.from_data(
            BoardState.get_data_from_grid(grid),
            author,
            rob
        )

    @staticmethod
    def from_data(data, author, rob=(-1, -1)):
        bs = BoardState(
            data=data,
            author=author,
            rob_x=rob[0],
            rob_y=rob[1],
        )
        bs.get_normalization(data, rob)
        bs.normalize()
        objects = BoardState.objects.filter(id=bs.id)
        if objects.exists():
            return objects.first()
        bs.save(skip_normalize=True)
        return bs

    @staticmethod
    def get_normalization(data, rob):
        data, rob = min(
            [BoardState.transform(data, mode, rob)
             for mode in range(8)]
        )
        # print('result')
        # print(data, rob)
        # print(BoardState.get_key_from_data(data, rob))
        return data, rob

    def normalize(self):
        self.data, (self.rob_x, self.rob_y) = \
            self.get_normalization(self.data, self.rob())
        self.id = self.get_key_from_data(self.data, self.rob())


class StateTransition(UserOwnedModel,
                      CommentAvailableModel,
                      TagAvailableModel):
    label = models.CharField(
        verbose_name='Label',
        max_length=3,
        help_text='Mark the point on the board with 1-3 alphabets or numbers',
    )

    source = models.ForeignKey(
        verbose_name='Source',
        to=BoardState,
        db_index=True,
        related_name='next_transitions',
        help_text='The state transfer from',
    )

    target = models.ForeignKey(
        verbose_name='Target',
        to=BoardState,
        db_index=True,
        related_name='prev_transitions',
        help_text='The state transfer to',
    )

    class Meta:
        db_table = 'go_core_state_transition'
        verbose_name = 'State Transition'
        verbose_name_plural = 'State Transitions'
        unique_together = (
            ('source', 'label'),
            ('source', 'target'),
        )

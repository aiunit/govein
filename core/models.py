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
        result = '<Board: {}>\n'.format(self.id)
        grid = self.to_grid()
        for i in range(19):
            for j in range(19):
                result += '.xo#'[grid[i][j]]
            result += '\n'
        return result

    def save(self, *args, **kwargs):
        if not kwargs.get('skip_normalize'):
            self.normalize()
        else:
            del kwargs['skip_normalize']
        super().save(*args, **kwargs)

    def preview_url(self):
        from django.core.urlresolvers import reverse
        return reverse('preview', kwargs=dict(pk=self.id))

    def preview_html_tag(self):
        return r'<img src="{}"/>'.format(self.preview_url())

    preview_html_tag.short_description = 'Preview'
    preview_html_tag.allow_tags = True

    def rob(self):
        return self.rob_x, self.rob_y

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
            rob_x, rob_y = rob_y, len(grid) - 1 - rob_x
        data = BoardState.get_data_from_grid(grid)
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


class StateTransition(UserOwnedModel,
                      CommentAvailableModel,
                      TagAvailableModel):
    label = models.CharField(
        verbose_name='Label',
        max_length=2,
        help_text='Mark the point on the board with an alphabet or two',
    )

    source = models.ForeignKey(
        verbose_name='Source',
        to=BoardState,
        db_index=True,
        related_name='next_transitions',
    )

    target = models.ForeignKey(
        verbose_name='Source',
        to=BoardState,
        db_index=True,
        related_name='prev_transitions',
    )

    class Meta:
        db_table = 'go_core_state_transition'
        verbose_name = 'State Transition'
        verbose_name_plural = 'State Transitions'
        unique_together = (
            ('source', 'label'),
            ('source', 'target'),
        )

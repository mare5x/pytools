import time

from . import printer
from .filetools import format_seconds


class progressbar:
    """Simple progress bar.
    
    Usage:
        for i in progressbar(iterable):
            fuzz()
        
        p = progressbar(total=N)
        ... Elsewhere (in a callback):
        p.update()
        ... When done:
        p.close()

        with progressbar(total=N) as p:
            ...
            p.update()
            ...

        with progressbar() as p:
            p.update()
            or
            p.set_progress()

    For a thread-safe version, or if you want to display
    multiple progress bars use 'blockbar' (pytools.printer integration).
    """

    bar_fill = '#'

    def __init__(self, iterable=None, total=None, desc='', show_time=True, bar_width=36, max_width=None):
        self.iterable = iterable
        self.total = len(iterable) if iterable \
            else (total if total \
            else (0))
        self.desc = desc
        self.show_time = show_time
        self.bar_width = bar_width
        self.max_width = max_width

        self.count = 0
        self.progress = None  # float [0,1]
        self.start_time = time.time()
        self.max_length = 0

    def __iter__(self):
        # Implemented as a generator function.
        for item in self.iterable:
            yield item
            self.update()
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def __repr__(self):
        return self.format_bar()

    def update(self, amount=1):
        self.count += amount
        self.write()

    def set_progress(self, progress):
        self.progress = progress
        self.update(0)

    def close(self):
        self.progress = 1 if self.progress else None
        self.count = self.total
        self.write(end='\n')

    def format_bar(self):
        """
        Progress bar format:
        <desc> [####   ] <.2f> % [MM:SS | MM:SS]
               |-------|        elapsed | remaining
                 width

        The dummy progress bar's format (progress unknown):
        <desc> [####   ] [MM:SS]

        <max_width> will only shrink <desc>!
        """

        dt = time.time() - self.start_time

        dummy = self.progress is None and self.total <= 0
        if dummy:
            # # If there is no progress defined, animate a dummy progress bar.
            # animation_length = 0.5  # seconds
            # progress = (dt % animation_length) / animation_length
            M = 3
            progress = (self.count % (M + 1)) / M if self.count != self.total else 1
        else:
            progress = self.progress if self.progress \
                else (self.count / self.total if self.total > 0 \
                else (0))

        fill_count = round(progress * self.bar_width)
        bar = self.bar_fill * fill_count
        bar += (self.bar_width - fill_count) * ' '
        bar = "[{}]".format(bar)

        if not dummy:
            bar += " {:.2f} %".format(progress * 100)

        if self.show_time:
            elapsed = format_seconds(dt)
            if dummy:
                bar += " [{}]".format(elapsed)
            else:
                remaining = format_seconds((dt / progress) - dt) if progress > 0 else "inf"
                bar += " [{} | {}]".format(elapsed, remaining)
        
        if self.max_width:
            max_desc_len = max(0, self.max_width - len(bar) - 1)
            desc = printer.cut_line(self.desc, max_desc_len)
        else:
            desc = self.desc
        desc += " " + bar

        # Pad the string with blanks in case the bar shrunk ...
        # (Only the remaining time part can shrink.)
        pad = max(0, self.max_length - len(desc))
        self.max_length = max(self.max_length, len(desc))
        desc += ' ' * pad
        return desc

    def write(self, end=''):
        print(self.format_bar() + end, end='\r')


class blockbar(progressbar):
    """progressbar using printer.block."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        max_width = kwargs.get("max_width", 120)
        self.block = printer.block(max_line_width=max_width)

    def __enter__(self):
        self.block.__enter__()
        return super().__enter__()

    def __exit__(self, *exc):
        super().__exit__(*exc)
        # block will exit in write('\n')

    def __repr__(self):
        return super().__repr__()

    def write(self, end=''):
        self.block.print(self.format_bar())
        if end == '\n': self.block.exit()

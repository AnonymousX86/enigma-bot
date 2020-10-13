from random import choice


def colors() -> tuple:
    return (
        0x1abc9c,
        0x11806a,
        0x2ecc71,
        0x1f8b4c,
        0x3498db,
        0x206694,
        0x9b59b6,
        0x71368a,
        0xe91e63,
        0xad1457,
        0xf1c40f,
        0xc27c0e,
        0xe67e22,
        0xa84300,
        0xe74c3c,
        0x992d22,
        0x95a5a6,
        0x607d8b,
        0x979c9f,
        0x546e7a,
        0x7289da,
        0x99aab5
    )


def random_color() -> int:
    """Return random color in '0x000000' format
    Based on Discord.py documentation
    """
    return choice(colors())

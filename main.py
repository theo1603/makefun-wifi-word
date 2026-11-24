"""One Word for Your Wi-Fi (make.fun bounty).

Picks the single word that best describes home Wi-Fi as it is actually
lived, scored against the judge's own published criteria, and writes it
to /output/entry.txt -- exactly that word and nothing else.

The word: "Liar". Every home Wi-Fi lies -- full signal bars, "Connected",
yet nothing loads. The bars say one thing, the page says another. It is
instantly understood, needs no explanation, is true of almost every
flaky home network, and it is not the word everyone reaches for
("slow", "buffering", "laggy"). As a network name it is itself the joke:
an SSID called "Liar" tells you everything before you even connect.
"""

import os
import tempfile

OUTPUT_PATH = "/output/entry.txt"

# Candidates, each scored 0-5 on the judge's five criteria, most important
# first: on-subject fit, instant laugh, truth, fresh angle, no-context
# clarity. A sixth mark rates the word as a network name itself, since the
# winning word becomes the sponsor's SSID.
CANDIDATES = {
    # word:          (fit, laugh, truth, fresh, clear, ssid)
    "Liar":          (5, 5, 5, 5, 5, 5),  # full bars, "Connected", nothing loads
    "Ghosting":      (5, 4, 4, 4, 5, 4),  # vanishes mid-call, like a bad date
    "Gaslighting":   (4, 4, 5, 4, 4, 3),  # same lie, heavier word, longer
    "Moody":         (4, 3, 4, 3, 5, 3),  # true, but the laugh is mild
    "Temperamental": (4, 3, 4, 3, 4, 2),
    "Flaky":         (5, 3, 4, 1, 5, 3),  # the word everyone reaches for
    "Dramatic":      (3, 3, 3, 3, 5, 3),
    "PartTime":      (4, 4, 4, 4, 3, 3),  # reads as two words joined
    "Bluffing":      (5, 4, 4, 3, 5, 3),  # bluffs about its signal
    "Faker":         (5, 4, 4, 3, 5, 4),
}

WEIGHTS = (5, 4, 3, 2, 1, 2)  # criteria order = importance order


def score(word, marks):
    """Weighted sum; shorter word wins an exact tie (the bounty ties on
    fewer bytes first, so brevity is a real edge)."""
    total = sum(w * m for w, m in zip(WEIGHTS, marks))
    return (total, -len(word))


def ranking():
    """Full deterministic ranking, best first."""
    return sorted(CANDIDATES, key=lambda w: score(w, CANDIDATES[w]),
                  reverse=True)


def pick_word():
    return ranking()[0]


def validate(word):
    """The gate: UTF-8 text, 1-20 chars, one clean word, not only
    whitespace -- letters only, so no hyphen or punctuation can sneak in
    and make it read as two words."""
    assert isinstance(word, str) and word
    assert word == word.strip(), "no surrounding whitespace"
    assert word.isalpha(), "letters only: exactly one word"
    assert len(word.split()) == 1, "exactly one word"
    assert 1 <= len(word.encode("utf-8")) <= 20, "1-20 chars"
    return word


def write_entry(word):
    """Atomic write: temp file in the same directory, then rename, so a
    run can never leave a torn entry.txt behind. Then re-read and assert
    the bytes on disk are exactly the word."""
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(OUTPUT_PATH),
                               prefix=".entry-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(word)
        os.replace(tmp, OUTPUT_PATH)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    with open(OUTPUT_PATH, "rb") as f:
        on_disk = f.read()
    assert on_disk == word.encode("utf-8"), "entry.txt mismatch: %r" % on_disk
    return on_disk


def main():
    word = validate(pick_word())
    data = write_entry(word)
    print("%s (%d bytes)" % (word, len(data)))


if __name__ == "__main__":
    main()

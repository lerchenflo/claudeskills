#!/usr/bin/env python3
"""Pick the App Store / Play Store canvas closest to a source screenshot.

App Store Connect only accepts an exact list of pixel sizes - upload anything else and it is
rejected at submission time, after you have already built the whole set. So resolve the target
size from this table first, then render onto it.

Usage:
    nearest_size.py 1080x2424                 # nearest accepted size, all stores
    nearest_size.py 1080x2424 --store ios     # restrict to App Store sizes
    nearest_size.py --list                    # print the whole table
"""
import argparse
import sys

# (store, slot, width, height, required?)
SIZES = [
    # --- App Store, iPhone (portrait; swap w/h for landscape uploads) ---
    ("ios", "iPhone", 1206, 2622, True),
    ("ios", "iPhone", 1179, 2556, True),
    ("ios", "iPhone Duo", 2007, 2853, False),
    ("ios", "iPhone Duo", 1398, 2034, False),
    ("ios", "iPad", 2064, 2752, True),
    ("ios", "iPad", 2048, 2732, True),
    # --- Play Store (a range, not a fixed list; these are the sweet spots) ---
    ("android", "Phone", 1080, 1920, True),
    ("android", "Phone", 1080, 2160, True),
    ("android", "Phone", 1080, 2400, False),
    ("android", "7\" tablet", 1200, 1920, False),
    ("android", "10\" tablet", 1600, 2560, False),
]


def parse_size(text: str):
    try:
        w, h = text.lower().split("x")
        return int(w), int(h)
    except ValueError:
        sys.exit(f"could not read a WxH size from {text!r}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("size", nargs="?", help="source screenshot size, e.g. 1080x2424")
    ap.add_argument("--store", choices=["ios", "android"], help="restrict to one store")
    ap.add_argument("--list", action="store_true", help="print the full table")
    args = ap.parse_args()

    rows = [r for r in SIZES if not args.store or r[0] == args.store]

    if args.list or not args.size:
        for store, slot, w, h, req in rows:
            print(f"{store:8} {slot:14} {w}x{h}{'  (required)' if req else ''}")
        return

    sw, sh = parse_size(args.size)
    src_ratio = sw / sh
    landscape = sw > sh

    def candidate(row):
        _, _, w, h, _ = row
        return (h, w) if landscape else (w, h)

    # Rank by aspect-ratio distance first: a mismatched aspect means visible letterboxing or a
    # crop through the UI, which is far more damaging than resampling to a different pixel count.
    ranked = sorted(rows, key=lambda r: (abs(candidate(r)[0] / candidate(r)[1] - src_ratio),
                                         abs(candidate(r)[0] - sw)))
    store, slot, w, h, req = ranked[0]
    tw, th = candidate(ranked[0])
    drift = abs(tw / th - src_ratio) / src_ratio * 100

    print(f"source      {sw}x{sh}  (aspect {src_ratio:.4f})")
    print(f"nearest     {tw}x{th}  {store} {slot}{'  [required slot]' if req else ''}")
    print(f"aspect drift {drift:.1f}%")
    if drift > 4:
        print("note: >4% drift - do not stretch the screenshot to fit. Keep the shot's own aspect "
              "inside the device frame and let the background make up the difference.")
    print("\nother accepted sizes:")
    for store, slot, w, h, req in ranked[1:5]:
        tw, th = candidate((store, slot, w, h, req))
        print(f"  {tw}x{th}  {store} {slot}")


if __name__ == "__main__":
    main()

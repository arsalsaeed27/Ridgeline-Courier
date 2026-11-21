# Viva notes: Ridgeline Courier (instance 38bfda97)

_Laiba Rehman (505099) | M. Arsal Saeed (506676) | Ali Salman Mustafa (534732) | M. Rayyan (534733) | instance 38bfda97_

Likely questions with short answers, grouped by part. Every member should be able to answer all of them.

## Shared base (config, stamp, data)

**Q: How is the instance reproducible?**
A: `scripts/oel_instance.py` hashes our sorted CMS IDs with sha256 and seeds `numpy.random.default_rng` with the hash. The twist and elevation scripts seed from `sha256("38bfda97|twists")` and `sha256("38bfda97|elevation")`. `BASE_SEED` in `oel/config.py` comes from the sorted CMS IDs. Every run produces the same files.

**Q: How do you do a live change?**
A: All parameters live in one `Config` object. `parse_cli` applies flags such as `--slip 0.5 --stop 2=14,23 --no-hills` and validates them. For example, a moved stop must be inside the grid, not blocked, reachable from the depot and not on another stop.

**Q: How do you guarantee that every output is stamped?**
A: Figures, tables and logs are only written through `oel/stamp.py`. Figures get the stamp as a suptitle and in their PNG metadata. Tables get it on the first line. Logs get it on the first line. `tests/test_stamp.py` checks every file in `results/`, using `results/manifest.json` and the PNG metadata for images.

## Part A: Environment, PEAS, cost map

## Part B: Search planners and heuristic

## Part C: Adversarial search (rival blocker)

## Part D: LLM dispatcher

## Part E: UI and experiments

## Twists

### Twist 1: Fuel limit with charging stations

### Twist 2: Teleport tunnels

### Twist 3 (ours): Hills with regenerative braking

**Q: Why must REGEN < UP_FUEL?**
A: Climbing k units burns 2k extra fuel and descending k units gives back only k, so every up-and-down loop loses k fuel. With REGEN ≥ UP_FUEL, bouncing between two cells would create free fuel, the tank limit would mean nothing and the fuel part of the state would no longer be well-founded. `oel/config.py` asserts this.

**Q: How was the elevation map made?**
A: `scripts/make_elevation.py` adds 4–6 Gaussian bumps whose centres, peak heights and widths come from a seeded rng. It rescales the sum to 0..9 and rounds it to integers. Gaussians give smooth hills, so neighbouring cells differ by only a little, which makes sense for a city.

**Q: What changes for the planners?**
A: Moves become direction-dependent, because A→B ≠ B→A. Heuristic distance fields therefore have to be computed backwards over reversed edges. Fuel can also go up without a station, so feasibility checks can't assume fuel only decreases.

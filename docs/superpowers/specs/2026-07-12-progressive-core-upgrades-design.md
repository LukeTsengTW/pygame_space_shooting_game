# Progressive Core Upgrades Design

## Goal

Make weapon damage, projectile speed, and hull capacity upgrades gain progressively larger amounts per purchased level while retaining their existing purchase costs and unlimited level counts.

## Progression Formula

For an upgrade with cap `C`, the increment granted by purchasing from current level `L` is `min(L + 1, C)`.

The cumulative bonus at level `L` is:

```
ramp = min(L, C)
bonus = ramp * (ramp + 1) // 2 + max(L - C, 0) * C
```

- Weapon damage and projectile speed use `C = 30`.
- Hull capacity uses `C = 5`.
- The first upgrade grants `+1`; the thirtieth damage/speed upgrade grants `+30`; later damage/speed upgrades each grant `+30`.
- The fifth hull upgrade grants `+5`; later hull upgrades each grant `+5`.

## Runtime Integration

Add a pure `upgrade_scaling.py` module for next-level increments, cumulative bonuses, and multi-level purchase deltas. `main.py` uses it for all three core upgrades:

- Buying one or multiple levels adds the calculated delta instead of the raw level count.
- Save loading recalculates `player.damage`, `BULLET_SPEED`, and `max_lives` from the saved level counts and base values `50`, `20`, and `10`.
- Upgrade cards display the actual next increment rather than a fixed `+1`.

No save schema migration is required because existing saves persist levels, not final stat values. Existing saves therefore receive the new cumulative bonus when loaded.

## Scope

- Keep upgrade costs, level counts, sentry upgrades, tactical support, score, combat damage scaling, and save format unchanged.
- Preserve unlimited purchases after each cap.

## Validation

Unit-test pure progression helpers at first level, cap, and post-cap boundaries; test cumulative and multi-level deltas. Run the full pytest suite after integrating `main.py`.

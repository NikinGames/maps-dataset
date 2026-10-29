# maps-dataset

Geospatial dataset pool for NikinGames projects (Ankara 3D World game, maps/SaaS).
Regions are scanned on GitHub Actions; archives are stored privately.

| Layer | Source | Workflow |
|---|---|---|
| OSM vector + Copernicus DEM | Overpass + AWS Terrarium | `scan.yml` (monthly + manual) |
| Mapillary images | Mapillary Graph API | `scan-mapillary.yml` (manual) |
| Google Street View panoramas | Street View Static API | `scan-streetview.yml` (manual) |
| Google Photorealistic 3D Tiles | Map Tiles API | `scan-tiles3d.yml` (manual) |

Fetch code lives in [`NikinGames/3dworldgame/pipeline/fetch`](https://github.com/NikinGames/3dworldgame/tree/main/pipeline/fetch).
Scan scripts in `scripts/` call it. Each workflow uploads a `.tar.gz` to a dated
release on the **private** `NikinGames/maps-dataset-data` repo (secret
`DATA_REPO_TOKEN`); this public repo keeps no data of its own.

## Required secrets

| Secret | Workflow | Where to get it |
|---|---|---|
| `DATA_REPO_TOKEN` | all | Fine-grained PAT, owner `NikinGames`, **both** repos `maps-dataset-data` (Contents: Read and write) **and** `3dworldgame` (Contents: Read) |
| `GOOGLE_SV_KEY` | Street View | Google Cloud → Street View Static API enabled |
| `GOOGLE_MAPS_API_KEY` | 3D Tiles | Google Cloud → Map Tiles API enabled |
| `MAPILLARY_TOKEN` | Mapillary | dashboard.mapillary.com → Developers → Access Tokens |
| `APIFY_TOKENS` | Apify jobs | Apify Console → Settings → Integrations, comma-separated (one per shard) |
| `RCLONE_CONF` | all | Contents of `~/.config/rclone/rclone.conf` (not JSON, no quotes) |

### Gotchas that have actually broken runs

- **`DATA_REPO_TOKEN` must cover `3dworldgame` too.** Every workflow checks that
  private repo out as `engine/`. With a token scoped to `maps-dataset-data` only,
  `actions/checkout` fails with `Not Found - .../repos/NikinGames/3dworldgame` and
  every job dies before the first request.
- **Never paste `APIFY_TOKENS` with a BOM.** A leading UTF-8 BOM (`EF BB BF`) makes every call
  return 401 *and* defeats GitHub's own secret masking, so the live token ends up in
  the build log. `scripts/apify_preflight.py` strips it and prints the BOM warning.
- **`RCLONE_CONF` is the rclone.conf text**, starting with a `[gdrive]` section. Pasted
  as JSON it fails inside rclone with `invalid character 'a' looking for beginning of
  object key string`; `drive-push` now checks the shape and skips cleanly when empty.
- **`OVERTURE_RELEASE` (repository variable) is optional.** Leave it unset: the fetcher
  asks S3 for the newest published release. Overture publishes monthly and a pinned
  date silently stops existing.

## Add a region

Drop a YAML in `regions/` (same schema as `3dworldgame/config/regions/*.yaml`),
add its id to the matrix in `scan.yml` or pick it as a workflow input.

Attribution rules live in [DATA_LICENSES.md](DATA_LICENSES.md). Private archives
are internal; redistribution and the Zenodo path (`.zenodo.json`) are off by default.

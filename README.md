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
| `DATA_REPO_TOKEN` | all | Fine-grained PAT, owner `NikinGames`, repo `maps-dataset-data`, Contents: Read and write |
| `GOOGLE_SV_KEY` | Street View | Google Cloud → Maps JS/Static API, Street View Static API enabled |
| `GOOGLE_MAPS_API_KEY` | 3D Tiles | Google Cloud → Map Tiles API enabled |
| `MAPILLARY_TOKEN` | Mapillary | dashboard.mapillary.com → Developers → Access Tokens |

## Add a region

Drop a YAML in `regions/` (same schema as `3dworldgame/config/regions/*.yaml`),
add its id to the matrix in `scan.yml` or pick it as a workflow input.

Attribution rules live in [DATA_LICENSES.md](DATA_LICENSES.md). Private archives
are internal; redistribution and the Zenodo path (`.zenodo.json`) are off by default.

# maps-dataset

Open geospatial dataset pool for NikinGames projects (Ankara 3D World game, maps/SaaS).
Regions are scanned automatically from open sources; nothing is hand-edited.

| Layer | Source | License |
|---|---|---|
| Vector (buildings, roads, landuse, POIs) | OpenStreetMap via Overpass | ODbL 1.0 |
| Elevation tiles | Copernicus DEM GLO-30 (AWS Terrain Tiles) | Copernicus licence, attribution |

See [DATA_LICENSES.md](DATA_LICENSES.md). Never included: orthophotos, Google 3D tiles or
anything derived from them.

## How it works

- `regions/*.yaml` — one file per region (same schema as `3dworldgame/config/regions`).
- `scan.yml` — matrix job: checks out the pipeline from `NikinGames/3dworldgame`, runs
  `pipeline.cli fetch` per region, packs `data/raw/<id>` + DEM tiles + `manifest.json`
  (sha256, bbox, fetch date) into one archive per region.
- Data is stored privately: archives are uploaded as release assets of the private repo
  `NikinGames/maps-dataset-data` (secret `DATA_REPO_TOKEN`). This public repo only holds code,
  so Actions minutes are free and no data is redistributed. Zenodo publishing is optional
  later (`.zenodo.json` kept for that).

Add a region: drop a YAML into `regions/`, add its id to the matrix in `scan.yml`.

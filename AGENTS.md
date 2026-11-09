# AGENTS.md

Este repositorio NO es un proyecto de software. No hay código fuente, `package.json`, scripts de build/test/lint, ni CI. No busques puntos de entrada ni comandos de ejecución: no existen.

## Qué contiene
- `Maestro_Clientes.xlsx` — base de clientes (Excel).
- `polizas-20261102T231058Z-1-001.zip` — archivo comprimido de pólizas.
- `polizas-20261102T231058Z-1-001/polizas/` — PDFs extraídos, nombrados `Poliza_<TIPO>-2026-<NNNN>.pdf` (tipos: `SPC`, `PCS`, `AIS`).

## Gotchas
- El ZIP y la carpeta extraída contienen lo mismo. Si editas uno, sincroniza el otro.
- Git acaba de inicializarse (`git init`). No hay commits todavía: revisa `git status` antes de asumir qué está trackeado.

## Comandos útiles
- `git status` — ver estado de los archivos.
- `git add <archivo>` y `git commit` — versionar cambios.

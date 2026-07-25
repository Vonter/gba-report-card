# gba-report-card

How does your area in Bengaluru perform when it comes to civic grievances? See report cards for roads, garbage and more. Evaluated using citizen-submitted ratings from the Sahaaya app: [https://gba-report-card.urbanuru.in/](https://gba-report-card.urbanuru.in/)

Data from [bbmp-citizen-grievances](https://github.com/Vonter/bbmp-citizen-grievances). Inspired by [NYC 311 Report Card](https://reports.jehiah.cz/311_report_card/).

## Develop

- Install dependencies with `pnpm install` (or `npm install`)
- Process data with `pnpm data` (or `npm data`)
- Start local dev server with `pnpm run dev` (or `npm run dev`)
- Build site deployment assets with `pnpm run build` (or `npm run build`)

## Architecture

- Data sourced from [bbmp-citizen-grievances](https://github.com/Vonter/bbmp-citizen-grievances)
- Processing of data done by [data.py](data.py)
- Frontend built with [SvelteKit](https://kit.svelte.dev/)
- Hosted on [Cloudflare Pages](https://developers.cloudflare.com/pages/)

## Methodology

Complaint data is sourced from the Sahaaya app, filtered to those with citizen ratings (1–5 stars). Only the top 6 complaint categories are included as scored subjects. For each ward-category pair, marks are calculated as `(avg_rating - 1) × 25`, mapping a rating of 1 to 0 marks and 5 to 100 marks. A ward's overall marks is the sum of marks across scored subjects divided by the number of subjects where the ward has rated complaints. Grades are assigned based on the marks scored. Wards are ranked by overall marks, with ties broken alphabetically. Wards are combined into areas, to represent more commonly used location names, using the mapping defined in [data/ward-areas.json](data/ward-areas.json).

## License

The code is licensed under **MIT**. The data is available under **ODbL**.

## AI Declaration

Components of this repository, including code and documentation, were written with assistance from Claude AI.

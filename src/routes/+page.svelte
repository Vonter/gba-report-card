<script lang="ts">
	import type { PageData } from './$types';
	import Fuse from 'fuse.js';

	import { onMount } from 'svelte';
	import { base } from '$app/paths';

	type Subcategory = {
		sub_category: string;
		complaint_count: number;
		rated_count: number;
		marks: number | null;
		grade: string | null;
		rating_distribution: Record<string, number>;
	};

	type Subject = {
		category: string;
		complaint_count: number;
		rated_count: number;
		marks: number | null;
		max_marks: number;
		grade: string | null;
		subcategories: Subcategory[];
	};

	type Card = {
		complaint_count: number;
		rank: number | null;
		total_marks: number;
		max_possible_marks: number;
		categories_scored: number;
		categories_total: number;
		percentage: number;
		grade: string | null;
		subjects: Subject[];
	};

	type Ward = Card & { ward_name: string };

	type Area = Card & { area_name: string; ward_names: string[] };

	type RanksData = {
		metadata: {
			total_wards: number;
			total_areas: number;
		};
		city: Card;
		wards: Ward[];
		areas: Area[];
	};

	const CATEGORY_DISPLAY: Record<string, string> = {
		'Road Maintenance(Engg)': 'Road Maintenance',
		'Solid Waste (Garbage) Related': 'Solid Waste Management',
		Electrical: 'Electrical Maintenance',
		'Health Dept': 'Health Services',
		veterinary: 'Veterinary Services',
		Forest: 'Tree Maintenance'
	};

	const CATEGORY_ORDER = ['Road', 'Solid Waste', 'Electrical', 'Trees', 'Health', 'Veterinary'];

	const RATING_BAR_COLOR = [
		'',
		'bg-[#B42020]',
		'bg-[#C86020]',
		'bg-[#C4902A]',
		'bg-[#4A8C3A]',
		'bg-[#2A7840]'
	];

	function normalizeCategory(raw: string): string {
		return CATEGORY_DISPLAY[raw] ?? raw;
	}

	const SUBCATEGORY_DISPLAY: Record<string, string> = {
		// Electrical
		'Street Light Not Working': 'Street Light Not Working',
		'Requirement For New Street Lights': 'New Street Light Request',
		'Park Lights Not Working': 'Park Lights Not Working',
		'Street Lights Switched On During Day Time': 'Street Lights On During Daytime',
		'Open Electrical Junction Box': 'Open Electrical Junction Box',
		'Earthing Issue relate to Electric Poles/Panel Boards': 'Earthing Issue (Poles/Panel Boards)',
		// Forest
		'obstructions Branches / Trees.': 'Branch/Tree Obstruction',
		'Removal of dead/fallen trees': 'Dead/Fallen Tree Removal',
		'Issues related Snakes/Birds/Monkeys': 'Snake/Bird/Monkey Issues',
		// Health Department
		'Increase in mosquito density': 'Mosquito Density',
		'Air/Noise pollution': 'Air/Noise Pollution',
		Fogging: 'Fogging',
		'Unhygienic premises in Hotel etc': 'Unhygienic Hotel/Premises',
		Spraying: 'Spraying',
		'Dengue positive': 'Dengue',
		'Delay in issue of Trade licence': 'Trade Licence Delay',
		'Zonal Violation of the Building': 'Building Zone Violation',
		'Birth & Death Registration': 'Birth & Death Registration',
		'Unavailability of staff': 'Staff Unavailability',
		'Non availability of drugs': 'Drug Unavailability',
		'Unhygienic  premises in hospital': 'Unhygienic Hospital Premises',
		'Indira Canteen': 'Indira Canteen',
		'Non availability of vaccines': 'Vaccine Unavailability',
		// Road Maintenance
		Potholes: 'Potholes',
		'Road side drains': 'Roadside Drains',
		'footpath encroachment': 'Footpath Encroachment',
		'Debris Removal / Construction Material': 'Debris/Construction Material',
		'Road cutting': 'Road Cutting',
		Footpath: 'Footpath',
		'water stagnation': 'Water Stagnation',
		'UnAuthorised Constructions': 'Unauthorised Constructions',
		'water leakage on road': 'Water Leakage on Road',
		'Overhanging cables': 'Overhanging Cables',
		// Solid Waste Management
		'Garbage dump': 'Garbage Dump',
		'Garbage vehicle not arrived': 'Garbage Vehicle Not Arrived',
		'Sweeping not done': 'Sweeping Not Done',
		'Garbage dumping in vacant sites': 'Garbage in Vacant Sites',
		'Burning of Garbage in Open Space': 'Open Garbage Burning',
		'Complaint against SW collector/ SWM official for violation of SWM Rules':
			'SWM Official Violation',
		'Garbage transfer not as per norms & area not kept clean': 'Improper Garbage Transfer',
		'Dead animal(s)': 'Dead Animals',
		'Garbage nuisance while transporting': 'Garbage Transport Nuisance',
		'Public dustbins not cleaned': 'Dustbins Not Cleaned',
		'Segregation of waste is not done': 'Waste Not Segregated',
		// Veterinary
		'Stray dog related complaints': 'Stray Dog Complaints',
		'Animal birth control/neutering of stray dogs': 'Stray Dog Neutering',
		'Stray/Rabid dog bite': 'Stray/Rabid Dog Bite',
		'Stray cattle related complaints': 'Stray Cattle Complaints',
		'Mutton/Chicken/fish stall Unhygienic maintenance': 'Unhygienic Meat/Fish Stall',
		'Anti Rabies Vaccination of stray dogs': 'Anti-Rabies Vaccination',
		'Stray pig related complaints': 'Stray Pig Complaints',
		'Fatally injured - Needs immediate attention': 'Fatally Injured Animal',
		'Animal Rescue - Not well - Requires attention': 'Animal Rescue',
		'Pet dog licence': 'Pet Dog Licence',
		'shifting of the street dogs to other places': 'Street Dog Relocation',
		'Animal Cruelty/Ill-Treated / Abused': 'Animal Cruelty/Abuse',
		'Animal Cruelty/Relocated': 'Animal Cruelty/Relocation',
		'Request for ABC': 'ABC Request',
		'Street dog Adaptation process details': 'Street Dog Adoption',
		'Request for New feeder Points': 'New Feeder Point Request',
		'"Pet licensing / Pet shop licensing  / Breeder licensing "': 'Pet/Shop/Breeder Licensing',
		'Illegal pet shop / Animal cruelty / license check': 'Illegal Pet Shop/Cruelty Check',
		'Aged street dogs please take action': 'Aged Street Dogs',
		'Feeder Harassment  by Individual / Mob but no association':
			'Feeder Harassment (Individual/Mob)',
		'Dog, cat Poor conditions / Breeding license validation': 'Poor Conditions/Breeding Licence',
		'Awareness session / Request for a session': 'Awareness Session',
		'Animal caught disease post surgery': 'Post-Surgery Disease',
		'Feeder Harassment by Association / Gated Community': 'Feeder Harassment (Association)'
	};

	function normalizeSubcategory(raw: string): string {
		return SUBCATEGORY_DISPLAY[raw] ?? raw;
	}

	function categoryOrderIndex(raw: string): number {
		const display = normalizeCategory(raw);
		const idx = CATEGORY_ORDER.findIndex((prefix) => display.startsWith(prefix));
		return idx === -1 ? CATEGORY_ORDER.length : idx;
	}

	function sortedSubjects(subjects: Subject[]): Subject[] {
		return [...subjects].sort(
			(a, b) => categoryOrderIndex(a.category) - categoryOrderIndex(b.category)
		);
	}

	function maxDistCount(dist: Record<string, number>): number {
		const vals = Object.values(dist);
		return vals.length ? Math.max(...vals) : 0;
	}

	type Selection = { kind: 'ward'; item: Ward } | { kind: 'area'; item: Area };

	let { data }: { data: PageData } = $props();
	const ranks: RanksData = $derived(data.data);

	let query = $state('');
	let selection = $state<Selection | null>(null);
	let expanded = $state(new Set<string>());
	let expandedSub = $state(new Set<string>());
	let open = $state(false);
	let sharing = $state(false);
	let copied = $state(false);
	let reportCardEl: HTMLElement;
	let cachedShareBlob: Blob | null = null;
	let generatingPromise: Promise<Blob> | null = null;
	let shareToken = 0;

	function dataUrlToBlob(dataUrl: string): Blob {
		const [header, base64] = dataUrl.split(',');
		const mime = header.match(/data:([^;]+)/)?.[1] ?? 'image/png';
		const binary = atob(base64);
		const bytes = new Uint8Array(binary.length);
		for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
		return new Blob([bytes], { type: mime });
	}

	function generateShareImage(): Promise<Blob> {
		if (cachedShareBlob) return Promise.resolve(cachedShareBlob);
		if (generatingPromise) return generatingPromise;
		const token = shareToken;
		const timeout = new Promise<never>((_, reject) =>
			setTimeout(() => reject(new Error('Image generation timed out')), 10000)
		);
		generatingPromise = Promise.race([
			import('html-to-image').then(({ toPng }) => {
				const width = reportCardEl.offsetWidth;
				return toPng(reportCardEl, {
					pixelRatio: 2,
					backgroundColor: '#C8D8EC',
					skipFonts: true,
					width,
					style: { width: width + 'px', maxWidth: 'none', margin: '0' }
				});
			}),
			timeout
		])
			.then((dataUrl) => {
				const blob = dataUrlToBlob(dataUrl);
				// Only commit if the selection hasn't changed since this render started.
				// Otherwise a stale in-flight render would overwrite the current card.
				if (token === shareToken) {
					cachedShareBlob = blob;
					generatingPromise = null;
				}
				return blob;
			})
			.catch((e) => {
				if (token === shareToken) generatingPromise = null;
				throw e;
			});
		return generatingPromise;
	}

	type SearchItem = { kind: 'ward'; name: string; item: Ward } | { kind: 'area'; name: string; item: Area };

	const searchItems = $derived([
		...ranks.areas.map((a) => ({ kind: 'area' as const, name: a.area_name, item: a })),
		...ranks.wards.map((w) => ({ kind: 'ward' as const, name: w.ward_name, item: w }))
	]);

	const fuse = $derived(
		new Fuse(searchItems, { keys: ['name'], threshold: 0.4, distance: 200, minMatchCharLength: 1 })
	);

	const suggestions = $derived(
		open
			? query.length === 0
				? searchItems.slice(0, 8)
				: fuse.search(query, { limit: 8 }).map((r: { item: SearchItem }) => r.item)
			: []
	);

	function activeCard(sel: Selection | null, city: Card): Card & { name: string } {
		if (sel?.kind === 'ward') return { ...sel.item, name: sel.item.ward_name };
		if (sel?.kind === 'area') return { ...sel.item, name: sel.item.area_name };
		return { ...city, name: 'Greater Bengaluru Authority' };
	}
	const card = $derived(activeCard(selection, ranks.city));

	const remarks = $derived(generateRemarks(card, ranks.city));

	function generateRemarks(card: Card & { name: string }, city: Card): string[] {
		const scored = card.subjects.filter((s) => s.marks !== null);
		if (scored.length === 0) return [];

		const pool: string[] = [];
		const sorted = [...scored].sort((a, b) => b.marks! - a.marks!);
		const best = sorted[0];
		const worst = sorted[sorted.length - 1];

		if (selection && card.rank != null) {
			const isArea = selection.kind === 'area';
			const total = isArea ? ranks.metadata.total_areas : ranks.metadata.total_wards;
			const unit = isArea ? 'areas' : 'wards';
			const pct = (card.rank / total) * 100;
			if (card.rank <= 10) {
				pool.push(`Ranked #${card.rank}, among the top 10 ${unit}`);
			} else if (pct <= 25) {
				pool.push(`Ranked #${card.rank}, among the top 25% of ${unit}`);
			} else if (pct <= 50) {
				pool.push(`Ranked #${card.rank}, among the top 50% of ${unit}`);
			} else if (pct <= 75) {
				pool.push(`Ranked #${card.rank}, among the bottom 50% of ${unit}`);
			} else if (pct >= 75) {
				pool.push(`Ranked #${card.rank}, among the bottom 25% of ${unit}`);
			}
		}

		pool.push(
			`${normalizeCategory(best.category)} is the strongest subject with a ${best.grade} grade.`
		);

		if (sorted.length > 1) {
			if ((worst.marks ?? 0) < 40) {
				pool.push(
					`${normalizeCategory(worst.category)} is failing with a F grade, urgent improvement needed.`
				);
			} else {
				pool.push(`Most room for improvement in ${normalizeCategory(worst.category)}`);
			}
		}

		if (selection) {
			const cityScored = city.subjects.filter((s) => s.marks !== null);
			const above = scored.filter((s) => {
				const cs = cityScored.find((c) => c.category === s.category);
				return cs && s.marks! > cs.marks!;
			});
			const below = scored.filter((s) => {
				const cs = cityScored.find((c) => c.category === s.category);
				return cs && s.marks! < cs.marks!;
			});

			if (above.length === scored.length) {
				pool.push(`Performs above the average in all ${scored.length} subjects.`);
			} else if (below.length === scored.length) {
				pool.push(`Performs below the average in all ${scored.length} subjects.`);
			} else if (above.length > 0) {
				const names = above.map((s) => normalizeCategory(s.category)).join(', ');
				pool.push(`Above average in ${names}.`);
			} else {
				pool.push(`Below average across all scored subjects.`);
			}
		}

		if (pool.length < 3) {
			const pct = Math.round(card.percentage);
			if (pct >= 75) {
				pool.push(`Overall score of ${pct}/100 reflects strong performance.`);
			} else if (pct >= 50) {
				pool.push(`Overall score of ${pct}/100 suggests room for improvement across subjects.`);
			} else {
				pool.push(`Overall score of ${pct}/100 indicates significant gaps in performance.`);
			}
		}

		if (pool.length < 3) {
			pool.push(
				`${card.categories_scored} out of ${card.categories_total} service categories have sufficient data for scoring.`
			);
		}

		return pool;
	}

	function selectWard(ward: Ward) {
		selection = { kind: 'ward', item: ward };
		query = ward.ward_name;
		expanded = new Set();
		expandedSub = new Set();
		open = false;
	}

	function selectArea(area: Area) {
		selection = { kind: 'area', item: area };
		query = area.area_name;
		expanded = new Set();
		expandedSub = new Set();
		open = false;
	}

	function selectItem(s: SearchItem) {
		if (s.kind === 'ward') selectWard(s.item);
		else selectArea(s.item);
	}

	function clearSelection() {
		selection = null;
		query = '';
		expanded = new Set();
		expandedSub = new Set();
	}

	function randomPick() {
		const pool = [...ranks.areas, ...ranks.wards];
		const pick = pool[Math.floor(Math.random() * pool.length)];
		if ('area_name' in pick) selectArea(pick);
		else selectWard(pick);
	}

	const SITE_URL = 'https://gba-report-card.urbanuru.in/';

	$effect(() => {
		// Invalidate cached image whenever the card changes
		void card;
		shareToken++;
		cachedShareBlob = null;
		generatingPromise = null;
		// Pre-generate so share click is instant
		const timer = setTimeout(() => {
			if (reportCardEl) generateShareImage().catch(() => {});
		}, 300);
		return () => clearTimeout(timer);
	});

	function buildSharePayload(blob?: Blob): ShareData {
		const filename = `gba-${card.name.toLowerCase().replace(/\s+/g, '-')}.png`;
		const param = selection?.kind === 'ward' ? 'ward' : selection?.kind === 'area' ? 'area' : null;
		const permalink = param ? `${SITE_URL}?${param}=${encodeURIComponent(card.name)}` : SITE_URL;
		const label = param ? param[0].toUpperCase() + param.slice(1) : 'Name';
		const lines = [
			`${label}: ${card.name}`,
			card.grade && `Grade: ${card.grade}`,
			selection && card.rank != null && `Rank: #${card.rank}`,
		].filter(Boolean).join('\n');
		const shareText = `GBA Report Card\n\n${lines}\n\n${permalink}`;
		const base: ShareData = { title: 'GBA Report Card', text: shareText };
		if (blob) {
			const file = new File([blob], filename, { type: 'image/png' });
			const withFile: ShareData = { ...base, files: [file] };
			// On some mobile browsers, canShare fails if text/url are included with files.
			// Validate using a files-only probe and then share with the richer payload.
			if (!navigator.canShare || navigator.canShare({ files: [file] })) return withFile;
		}
		return base;
	}

	function copyImageToClipboard(blob: Blob) {
		if (typeof ClipboardItem !== 'undefined' && navigator.clipboard?.write) {
			return navigator.clipboard.write([new ClipboardItem({ 'image/png': blob })]);
		}
		return navigator.clipboard.writeText(SITE_URL);
	}

	function copyWithToast(blob: Blob) {
		return copyImageToClipboard(blob).then(() => {
			copied = true;
			setTimeout(() => (copied = false), 2000);
		});
	}

	// Two share paths only:
	// 1) Web Share API when available
	// 2) Fallback: copy image to clipboard
	//
	// Important: do not call navigator.share with a text-only payload unless image
	// generation failed, otherwise users see a successful share without the card image.
	function shareCard() {
		if (sharing) return;
		sharing = true;

		if (navigator.share) {
			const imagePromise = cachedShareBlob
				? Promise.resolve(cachedShareBlob)
				: generateShareImage();
			imagePromise
				.then((blob) => navigator.share(buildSharePayload(blob)))
				.catch((e) => {
					if (e instanceof Error && e.name === 'AbortError') return;
					// If image generation fails, still allow sharing text/link as a fallback.
					return navigator.share(buildSharePayload(undefined));
				})
				.catch((e) => {
					if (e instanceof Error && e.name !== 'AbortError') console.error('Share failed:', e);
				})
				.finally(() => {
					sharing = false;
				});
			return;
		}

		generateShareImage()
			.then((blob) => copyWithToast(blob))
			.catch((e) => {
				if (e instanceof Error && e.name !== 'AbortError') console.error('Share failed:', e);
			})
			.finally(() => {
				sharing = false;
			});
	}

	onMount(() => {
		const params = new URLSearchParams(window.location.search);
		const wardName = params.get('ward');
		const areaName = params.get('area');
		if (wardName) {
			const ward = ranks.wards.find((w) => w.ward_name === wardName);
			if (ward) selectWard(ward);
		} else if (areaName) {
			const area = ranks.areas.find((a) => a.area_name === areaName);
			if (area) selectArea(area);
		}
	});

	function toggle(category: string) {
		const next = new Set(expanded);
		if (next.has(category)) next.delete(category);
		else next.add(category);
		expanded = next;
	}

	function toggleSub(key: string) {
		const next = new Set(expandedSub);
		if (next.has(key)) next.delete(key);
		else next.add(key);
		expandedSub = next;
	}

	const GRADE_COLOR: Record<string, string> = {
		'A+': 'text-[#1a5c2e] bg-[#dceee3] border border-[#5a9e6e]',
		A: 'text-[#2a5c1a] bg-[#e4eedd] border border-[#7aae5a]',
		B: 'text-[#1a3c7a] bg-[#dce4f5] border border-[#5a7abe]',
		C: 'text-[#7a5c0a] bg-[#f5eed8] border border-[#b8985a]',
		D: 'text-[#7a3010] bg-[#f5e8de] border border-[#be7050]',
		F: 'text-[#8c1a1a] bg-[#f5dede] border border-[#be5050]'
	};

	function gradeColor(grade: string | null) {
		return grade ? (GRADE_COLOR[grade] ?? '') : 'text-gray-300';
	}
</script>

<svelte:head>
	<title>GBA Report Card</title>
</svelte:head>

<main class="min-h-screen bg-[#C8D8EC] px-2 py-6 sm:px-4 sm:py-10">
	<!-- Search + share controls (same row) -->
	<div class="mx-auto mb-4 max-w-3xl px-1 sm:px-0">
		<div class="flex items-center gap-2">
			<!-- Search group -->
			<div class="relative min-w-0 flex-1">
				<label for="ward-search" class="sr-only">Search ward or area</label>
				<div class="flex gap-2">
					<input
						id="ward-search"
						type="text"
						placeholder="Search ward or area…"
						bind:value={query}
						oninput={() => {
							open = true;
							if (selection && query !== card.name) selection = null;
						}}
						onfocus={() => {
							open = true;
						}}
						onblur={() => {
							open = false;
						}}
						class="w-full rounded border border-stone-400 bg-white px-4 py-2 text-sm shadow-sm focus:border-[#9A0000] focus:outline-none"
					/>
					{#if selection}
						<button
							type="button"
							onclick={clearSelection}
							class="shrink-0 rounded border border-stone-400 bg-white px-3 text-sm text-stone-400 hover:text-stone-700"
							title="Back to city view"
						>
							✕
						</button>
					{/if}
					<!-- Random ward (dice icon) -->
					<button
						type="button"
						onclick={randomPick}
						title="Random ward"
						class="shrink-0 rounded border border-stone-400 bg-white p-2 text-stone-500 hover:border-[#9A0000] hover:text-[#9A0000]"
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							viewBox="0 0 256 256"
							fill="currentColor"
							class="h-4 w-4"
						>
							<path
								d="M192 32H64A32 32 0 0 0 32 64v128a32 32 0 0 0 32 32h128a32 32 0 0 0 32-32V64a32 32 0 0 0-32-32zm16 160a16 16 0 0 1-16 16H64a16 16 0 0 1-16-16V64a16 16 0 0 1 16-16h128a16 16 0 0 1 16 16zM56 72a16 16 0 1 0 32 0 16 16 0 1 0-32 0zm112 0a16 16 0 1 0 32 0 16 16 0 1 0-32 0zm-56 56a16 16 0 1 0 32 0 16 16 0 1 0-32 0zM56 184a16 16 0 1 0 32 0 16 16 0 1 0-32 0zm112 0a16 16 0 1 0 32 0 16 16 0 1 0-32 0z"
							/>
						</svg>
					</button>
				</div>
				{#if suggestions.length > 0}
					<ul
						class="absolute z-10 mt-1 w-full rounded border border-stone-300 bg-white text-sm shadow-lg"
					>
						{#each suggestions as s (s.kind + s.name)}
							<li>
								<button
									type="button"
									class="flex w-full items-center justify-between px-4 py-2 text-left hover:bg-red-50"
									onmousedown={(e) => e.preventDefault()}
									onclick={() => selectItem(s)}
								>
									<span>{s.name}</span>
									<span class="ml-2 shrink-0 rounded bg-stone-100 px-1.5 py-0.5 text-[10px] font-semibold tracking-wide text-stone-500 uppercase">{s.kind === 'area' ? 'Area' : 'Ward'}</span>
								</button>
							</li>
						{/each}
					</ul>
				{/if}
			</div>

			<!-- Share icon -->
			<div class="relative shrink-0">
				<button
					type="button"
					onclick={shareCard}
					disabled={sharing}
					title={sharing ? 'Generating…' : 'Share report card'}
					class="rounded border border-stone-400 bg-white px-2 py-2 text-sm text-stone-500 shadow-sm hover:border-[#9A0000] hover:text-[#9A0000] disabled:opacity-50"
				>
					{#if sharing}
						<svg
							xmlns="http://www.w3.org/2000/svg"
							fill="none"
							viewBox="0 0 24 24"
							stroke-width="1.5"
							stroke="currentColor"
							class="h-4 w-4 animate-spin"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99"
							/>
						</svg>
					{:else}
						<svg
							xmlns="http://www.w3.org/2000/svg"
							fill="none"
							viewBox="0 0 24 24"
							stroke-width="1.5"
							stroke="currentColor"
							class="h-4 w-4"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								d="M7.217 10.907a2.25 2.25 0 1 0 0 2.186m0-2.186c.18.324.283.696.283 1.093s-.103.77-.283 1.093m0-2.186 9.566-5.314m-9.566 7.5 9.566 5.314m0 0a2.25 2.25 0 1 0 3.935 2.186 2.25 2.25 0 0 0-3.935-2.186zm0-12.814a2.25 2.25 0 1 0 3.933-2.185 2.25 2.25 0 0 0-3.933 2.185z"
							/>
						</svg>
					{/if}
				</button>
				{#if copied}
					<div
						class="pointer-events-none absolute bottom-full left-1/2 mb-2 -translate-x-1/2 rounded bg-stone-800 px-2 py-1 text-xs whitespace-nowrap text-white"
					>
						Copied to Clipboard
						<div
							class="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-stone-800"
						></div>
					</div>
				{/if}
			</div>
		</div>
	</div>

	<!-- Report card -->
	<div class="mx-auto max-w-3xl" bind:this={reportCardEl}>
		<div class="border-4 border-[#9A0000] bg-[#F5E8CC] p-1 shadow-2xl print:shadow-none">
			<div class="border-2 border-[#9A0000]">
				<!-- Letterhead band -->
				<div class="bg-[#9A0000] px-3 py-3 sm:px-6 sm:py-4">
					<div class="flex items-center gap-3 sm:gap-5">
						<div class="shrink-0">
							<img
								src="{base}/gba.png"
								alt="Greater Bengaluru Authority crest"
								class="h-12 w-12 rounded-full border-2 border-[#C4902A] object-cover sm:h-16 sm:w-16"
							/>
						</div>
						<div class="flex-1 text-center">
							<p
								class="font-display text-base font-bold tracking-[0.04em] text-[#E8D380] uppercase sm:text-2xl sm:tracking-[0.03em]"
							>
								Greater Bengaluru Authority
							</p>
							<h1
								class="mt-0.5 font-display text-sm font-semibold tracking-wider text-white uppercase sm:mt-1 sm:text-xl sm:tracking-[0.06em]"
							>
								Report Card
							</h1>
						</div>
						<div class="h-12 w-12 shrink-0 sm:h-16 sm:w-16"></div>
					</div>
				</div>

				<!-- Gold rule -->
				<div class="h-1 bg-[#C4902A]"></div>

				<!-- Details block -->
				<div class="bg-[#F5E8CC] px-4 py-3 sm:px-6 sm:py-4">
					<div
						class={`grid gap-x-6 gap-y-2 text-sm ${selection ? 'grid-cols-3' : 'grid-cols-1'}`}
					>
						<div
							class={selection
								? 'col-span-2 flex items-baseline gap-2'
								: 'flex items-baseline gap-2'}
						>
							<span class="shrink-0 text-xs font-semibold tracking-wider text-stone-500 uppercase">
								{selection?.kind === 'ward' ? 'Ward' : selection?.kind === 'area' ? 'Area' : 'Name'}
							</span>
							<span
								class={`flex-1 border-b border-dotted border-stone-400 pb-0.5 font-bold text-stone-900 ${selection ? 'truncate' : ''}`}
							>
								{card.name}
							</span>
						</div>
						{#if selection && card.rank != null}
							<div class="flex items-baseline gap-2">
								<span
									class="shrink-0 text-xs font-semibold tracking-wider text-stone-500 uppercase"
								>
									Rank
								</span>
								<span
									class="flex-1 border-b border-dotted border-stone-400 pb-0.5 font-bold text-stone-900"
								>
									#{card.rank}
								</span>
							</div>
						{/if}
					</div>
				</div>

				<!-- Marks table -->
				<div class="overflow-x-auto px-3 py-3 sm:px-6 sm:py-4">
					<table class="w-full border-collapse border-r border-stone-300 text-xs sm:text-sm">
						<thead>
							<tr class="bg-[#9A0000] text-white">
								<th
									class="border border-[#9A0000] px-1.5 py-1.5 text-left font-semibold tracking-wide sm:px-3 sm:py-2"
								>
									Subject
								</th>
								<th
									class="hidden w-14 border border-[#9A0000] px-1.5 py-1.5 text-center font-semibold tracking-wide sm:table-cell sm:w-20 sm:px-3 sm:py-2"
								>
									Max Marks
								</th>
								<th
									class="w-16 border border-[#9A0000] px-1.5 py-1.5 text-center font-semibold tracking-wide sm:w-28 sm:px-3 sm:py-2"
								>
									Marks Obtained
								</th>
								<th
									class="w-12 border border-[#9A0000] px-1.5 py-1.5 text-center font-semibold tracking-wide sm:w-16 sm:px-3 sm:py-2"
								>
									Grade
								</th>
							</tr>
						</thead>
						<tbody>
							{#each sortedSubjects(card.subjects.filter((s) => s.marks !== null)) as subject}
								{@const isExpanded = expanded.has(subject.category)}
								{@const scoredSubs = subject.subcategories.filter((s) => s.marks !== null)}
								{@const unscoredSubs = subject.subcategories.filter((s) => s.marks === null)}
								{@const displayCategory = normalizeCategory(subject.category)}
								<tr
									class="cursor-pointer border-b border-stone-300 bg-white hover:bg-[#F0EAD8]"
									onclick={() => toggle(subject.category)}
								>
									<td
										class="border-x border-stone-300 px-1.5 py-1.5 font-medium text-stone-800 sm:px-3 sm:py-2"
									>
										<span class="mr-1 text-stone-400">{isExpanded ? '▾' : '▸'}</span
										>{displayCategory}
									</td>
									<td
										class="hidden border-x border-stone-300 px-1.5 py-1.5 text-center text-stone-600 sm:table-cell sm:px-3 sm:py-2"
									>
										{subject.max_marks}
									</td>
									<td
										class="border-x border-stone-300 px-1.5 py-1.5 text-center font-bold text-stone-900 sm:px-3 sm:py-2"
									>
										{subject.marks != null ? Math.round(subject.marks) : ''}
									</td>
									<td class="border-x border-stone-300 px-1.5 py-1.5 text-center sm:px-3 sm:py-2">
										<span
											class="inline-block rounded px-1.5 py-0.5 font-bold {gradeColor(
												subject.grade
											)}"
										>
											{subject.grade}
										</span>
									</td>
								</tr>

								{#if isExpanded}
									{#each scoredSubs as sub}
										{@const subKey = `${subject.category}::${sub.sub_category}`}
										{@const isSubExpanded = expandedSub.has(subKey)}
										{@const maxCount = maxDistCount(sub.rating_distribution)}
										<tr
											class="cursor-pointer border-b border-stone-300 bg-[#F0EAD8] hover:bg-[#E8DCC8]"
											onclick={(e) => {
												e.stopPropagation();
												toggleSub(subKey);
											}}
										>
											<td
												class="border-x border-stone-300 py-1.5 pr-2 pl-2 text-xs text-stone-600 sm:pr-3 sm:pl-6"
											>
												<span class="mr-1 text-stone-400">{isSubExpanded ? '▾' : '▸'}</span
												>{normalizeSubcategory(sub.sub_category)}
											</td>
											<td
												class="hidden border-x border-stone-300 px-1.5 py-1.5 text-center text-xs text-stone-400 sm:table-cell sm:px-3"
												>—</td
											>
											<td
												class="border-x border-stone-300 px-1.5 py-1.5 text-center text-xs font-semibold text-stone-700 sm:px-3"
											>
												{sub.marks != null ? Math.round(sub.marks) : ''}
											</td>
											<td class="border-x border-stone-300 px-1.5 py-1.5 text-center sm:px-3">
												<span
													class="inline-block rounded px-1.5 py-0.5 text-xs font-bold {gradeColor(
														sub.grade
													)}"
												>
													{sub.grade}
												</span>
											</td>
										</tr>

										{#if isSubExpanded}
											<tr class="border-b border-stone-300 bg-[#F5E8CC]/60">
												<td
													colspan="4"
													class="border-x border-stone-300 px-3 py-2 pr-5 pl-5 sm:pr-12 sm:pl-12"
												>
													<div>
														<div
															class="mb-1 grid grid-cols-[2rem_1fr_16rem] items-center gap-1.5 pb-0.5"
														>
															<span
																class="text-[9px] font-semibold tracking-wide text-stone-500 uppercase"
																>Rating</span
															>
															<span></span>
															<span
																class="text-right text-[9px] font-semibold tracking-wide text-stone-500 uppercase"
																>Grievances</span
															>
														</div>
														<div class="space-y-1">
															{#each [5, 4, 3, 2, 1] as r}
																{@const count = sub.rating_distribution[r.toString()] ?? 0}
																{#if count > 0}
																	{@const pct = maxCount > 0 ? (count / maxCount) * 100 : 0}
																	<div
																		class="grid grid-cols-[2rem_1fr_2.5rem] items-center gap-1.5"
																	>
																		<span
																			class="text-[10px] font-semibold text-stone-500 tabular-nums sm:text-xs"
																			>{r}★</span
																		>
																		<div class="h-2 rounded-sm bg-stone-200">
																			<div
																				class="h-full rounded-sm {RATING_BAR_COLOR[r]}"
																				style="width:{pct}%"
																			></div>
																		</div>
																		<span
																			class="text-right text-[10px] font-semibold text-stone-700 tabular-nums sm:text-xs"
																			>{count.toLocaleString()}</span
																		>
																	</div>
																{/if}
															{/each}
														</div>
													</div>
												</td>
											</tr>
										{/if}
									{/each}

									{#each unscoredSubs as sub}
										<tr class="border-b border-stone-200 bg-[#F0EAD8]">
											<td
												class="border-x border-stone-300 py-1.5 pr-2 pl-4 text-xs text-stone-400 italic sm:pr-3 sm:pl-6"
											>
												{normalizeSubcategory(sub.sub_category)}
											</td>
											<td
												class="hidden border-x border-stone-300 px-1.5 py-1.5 text-center text-xs text-stone-300 sm:table-cell sm:px-3"
												>—</td
											>
											<td
												class="border-x border-stone-300 px-1.5 py-1.5 text-center text-xs text-stone-300 sm:px-3"
												>—</td
											>
											<td
												class="border-x border-stone-300 px-1.5 py-1.5 text-center text-xs text-stone-300 sm:px-3"
												>N/A</td
											>
										</tr>
									{/each}
								{/if}
							{/each}

							{#each sortedSubjects(card.subjects.filter((s) => s.marks === null)) as subject}
								{@const displayCategory = normalizeCategory(subject.category)}
								<tr class="border-b border-stone-200 bg-white">
									<td class="border-x border-stone-300 px-2 py-2 text-stone-400 italic sm:px-3"
										>{displayCategory}</td
									>
									<td
										class="hidden border-x border-stone-300 px-2 py-2 text-center text-stone-400 sm:table-cell sm:px-3"
										>{subject.max_marks}</td
									>
									<td class="border-x border-stone-300 px-2 py-2 text-center text-stone-300 sm:px-3"
										>—</td
									>
									<td
										class="border-x border-stone-300 px-2 py-2 text-center text-xs text-stone-300 sm:px-3"
										>N/A</td
									>
								</tr>
							{/each}

							<!-- Overall row -->
							<tr class="border-t-2 border-[#9A0000] bg-[#9A0000] font-bold text-white">
								<td class="border-x border-[#9A0000] px-2 py-2 tracking-wide sm:px-3">Overall</td>
								<td
									class="hidden border-x border-[#9A0000] px-2 py-2 text-center sm:table-cell sm:px-3"
								>
									100
								</td>
								<td class="border-x border-[#9A0000] px-2 py-2 text-center sm:px-3">
									{Math.round(card.percentage)}
								</td>
								<td class="border-x border-[#9A0000] px-2 py-2 text-center sm:px-3">
									<span
										class="inline-block rounded px-1.5 py-0.5 text-sm font-bold {gradeColor(
											card.grade
										)}"
									>
										{card.grade}
									</span>
								</td>
							</tr>
						</tbody>
					</table>
				</div>

				<!-- Remarks -->
				{#if remarks.length > 0}
					<div class="mx-4 sm:mx-6"></div>
					<div class="px-4 py-3 sm:px-6 sm:py-4">
						<p class="mb-2 text-xs font-semibold tracking-wider text-stone-500 uppercase">
							Remarks
						</p>
						<ul class="space-y-1">
							{#each remarks as remark}
								<li class="flex gap-2 text-xs text-stone-700 sm:text-sm">
									<span class="mt-0.5 shrink-0 text-[#9A0000]">•</span>
									<span>{remark}</span>
								</li>
							{/each}
						</ul>
					</div>
				{/if}

				<!-- Footer -->
				<div class="border-t border-stone-300 bg-[#F5E8CC] px-4 py-3 sm:px-6">
					<p class="text-xs text-stone-400">
						Select a subject in the report card for individual topic marks.
					</p>
					<p class="text-xs text-stone-400">
						Marks calculated from citizen-submitted ratings on the Sahaaya app.
					</p>
					<p class="text-xs text-stone-400">
						Average citizen-submitted rating is scaled to 100 and grade is assigned.
					</p>
					<p class="text-xs text-stone-400">
						Usage of Sahaaya app across wards is highly variable and leads to selection bias in
						results.
					</p>
					<div class="mt-3 flex flex-wrap items-center gap-2">
						<span class="text-xs font-medium text-stone-600">Try out Sahaaya on </span>
						<a
							href="https://play.google.com/store/apps/details?id=com.nammabengaluruNew.org&hl=en_IN"
							target="_blank"
							rel="noopener noreferrer"
							title="Sahaaya on Google Play"
							class="inline-flex items-center gap-1.5 rounded border border-stone-300 bg-white px-2 py-1 text-xs text-stone-600 hover:border-[#9A0000] hover:text-[#9A0000]"
						>
							<svg
								xmlns="http://www.w3.org/2000/svg"
								viewBox="0 0 24 24"
								fill="currentColor"
								class="h-3.5 w-3.5"
							>
								<path
									d="M3.18 23.76c.3.17.66.18.97.02l11.65-6.73-2.38-2.38-10.24 9.09zm17.32-10.14-2.78-1.6-2.64 2.64 2.64 2.64 2.8-1.62a1.5 1.5 0 0 0 0-2.06zM.44 1.56A1.5 1.5 0 0 0 0 2.62v18.76a1.5 1.5 0 0 0 .44 1.06l.06.06L10.69 12.5v-.24L.5 1.5l-.06.06zm14.8 8.07L4.15.24C3.85.07 3.43.1 3.12.27L13.42 10.5l1.82-1.87z"
								/>
							</svg>
							Android
						</a>
						<span class="text-xs font-medium text-stone-600">or </span>
						<a
							href="https://apps.apple.com/us/app/namma-bengaluru/id6755224744"
							target="_blank"
							rel="noopener noreferrer"
							title="Sahaaya on App Store"
							class="inline-flex items-center gap-1.5 rounded border border-stone-300 bg-white px-2 py-1 text-xs text-stone-600 hover:border-[#9A0000] hover:text-[#9A0000]"
						>
							<svg
								xmlns="http://www.w3.org/2000/svg"
								viewBox="0 0 24 24"
								fill="currentColor"
								class="h-3.5 w-3.5"
							>
								<path
									d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.8-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"
								/>
							</svg>
							iOS
						</a>
					</div>
				</div>
			</div>
		</div>
	</div>

	<!-- Attribution links -->
	<div class="mx-auto mt-8 w-4/5 max-w-[36rem] pt-3">
		<div class="flex w-full items-center justify-between gap-3">
			<a
				href="https://github.com/Vonter/gba-report-card?tab=readme-ov-file#methodology"
				target="_blank"
				rel="noopener noreferrer"
				class="text-xs font-medium text-stone-700 underline underline-offset-2 transition-colors hover:text-[#1a3f7a] hover:underline focus-visible:text-[#1a3f7a] focus-visible:underline focus-visible:outline-none"
				>Methodology</a
			>
			<a
				href="https://hyparam.github.io/demos/hyparquet/?key=https%3A%2F%2Fraw.githubusercontent.com%2FVonter%2Fbbmp-citizen-grievances%2Fmain%2Fdata%2Fcitizen-grievances.parquet"
				target="_blank"
				rel="noopener noreferrer"
				class="text-xs font-medium text-stone-700 underline underline-offset-2 transition-colors hover:text-[#1a3f7a] hover:underline focus-visible:text-[#1a3f7a] focus-visible:underline focus-visible:outline-none"
				>Data</a
			>
			<a
				href="https://reports.jehiah.cz/311_report_card/"
				target="_blank"
				rel="noopener noreferrer"
				class="text-xs font-medium text-stone-700 underline underline-offset-2 transition-colors hover:text-[#1a3f7a] hover:underline focus-visible:text-[#1a3f7a] focus-visible:underline focus-visible:outline-none"
				>Inspiration</a
			>
			<a
				href="mailto:hello@urbanuru.in"
				class="text-xs font-medium text-stone-700 underline underline-offset-2 transition-colors hover:text-[#1a3f7a] hover:underline focus-visible:text-[#1a3f7a] focus-visible:underline focus-visible:outline-none"
				>Feedback</a
			>
		</div>
	</div>
</main>

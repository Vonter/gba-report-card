<!-- SEO.svelte -->
<script lang="ts">
	let title = 'GBA Report Card';
	let description =
		'How does your area in Bengaluru perform when it comes to civic grievances? See report cards for roads, garbage and more. Evaluated using citizen-submitted ratings from the Sahaaya app.';
	let keywords =
		'gba,bbmp,blr,bangalore,bengaluru,ward,report card,civic services,sahaaya,grievance redressal,complaint ratings,road maintenance,solid waste,garbage,street lights,health,trees,veterinary,nagarika,namma bengaluru';
	let author = 'Vivek Matthew';
	let image = 'https://gba-report-card.urbanuru.in/sharecard.jpg';
	let url = 'https://gba-report-card.urbanuru.in/';
	let type = 'website';
</script>

<svelte:head>
	<!-- Favicon
	<link rel="icon" href="/favicon.ico" />
	 -->

	<!-- Basic Meta Tags -->
	<title>{title}</title>
	<meta name="description" content={description} />
	<meta name="keywords" content={keywords} />
	<meta name="author" content={author} />
	<meta name="robots" content="index, follow" />
	<meta name="viewport" content="width=device-width, initial-scale=1" />

	<!-- Canonical URL -->
	<link rel="canonical" href={url} />

	<!-- Open Graph Tags -->
	<meta property="og:title" content={title} />
	<meta property="og:site_name" content={title} />
	<meta property="og:description" content={description} />
	<meta property="og:image" content={image} />
	<meta property="og:url" content={url} />
	<meta property="og:type" content={type} />

	<!-- Twitter Card Tags -->
	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:title" content={title} />
	<meta name="twitter:description" content={description} />
	<meta name="twitter:image" content={image} />

	<!-- Additional Meta Tags -->
	<meta name="language" content="English" />
	<meta name="revisit-after" content="7 days" />
	<meta name="distribution" content="global" />
	<meta http-equiv="content-type" content="text/html; charset=utf-8" />
	<meta name="mobile-web-app-capable" content="yes" />
</svelte:head>

import type { PageLoad } from './$types';
import { base } from '$app/paths';

export const load: PageLoad = async ({ fetch }) => {
	const res = await fetch(`${base}/results.json`);
	const data = await res.json();
	return { data };
};

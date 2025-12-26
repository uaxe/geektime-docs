const policy = 'no-referrer';
const noRefererPrefixes = [
	'https://static001.geekbang.org/resource/image',
	'https://static001.geekbang.org/resource/avatar',
	'https://static001-test.geekbang.org/resource/image',
	'https://static001.infoq.cn/resource/image',
	'https://static001.geekbang.org/con'
];

document.querySelectorAll('p>img[src]').forEach((img) => {
	const src = img.getAttribute('src');
	if (src) {
		for (let index = 0; index < noRefererPrefixes.length; index++) {
			const prefix = noRefererPrefixes[index];
			if (src.startsWith(prefix)) {
				img.setAttribute('referrerpolicy', policy);
				return;
			}
		}
	}
});

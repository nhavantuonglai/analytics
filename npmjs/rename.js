function initTableOfContents() {
	const index = document.getElementById('index');
	if (!index) {
		console.warn('Không tìm thấy phần tử #index để chèn TOC');
		return;
	}

	const headings = document.querySelectorAll('h2, h3, h4');
	const tocList = document.createElement('ul');
	let currentParent = null;

	headings.forEach((heading) => {
		if (heading.id) {
			const listItem = document.createElement('li');
			const anchor = document.createElement('a');
			anchor.href = `#${heading.id}`;
			anchor.textContent = heading.textContent;
			listItem.appendChild(anchor);

			if (heading.tagName.toLowerCase() === 'h3') {
				listItem.style.fontStyle = 'italic';
			}

			if (heading.tagName.toLowerCase() === 'h3' || heading.tagName.toLowerCase() === 'h4') {
				if (currentParent) {
					const subList = currentParent.querySelector('ul') || document.createElement('ul');
					subList.appendChild(listItem);
					currentParent.appendChild(subList);
				}
			} else {
				tocList.appendChild(listItem);
				currentParent = listItem;
			}
		}
	});

	const items = tocList.querySelectorAll('li');
	const totalItems = items.length;
	const itemsToHide = Math.min(20, totalItems);

	for (let i = totalItems - itemsToHide; i < totalItems; i++) {
		items[i].style.display = 'none';
	}

	if (tocList.children.length > 0) {
		index.appendChild(tocList);
	} else {
		console.warn('Không tìm thấy tiêu đề hợp lệ để tạo TOC');
	}

	function destroy() {
		if (index && tocList && index.contains(tocList)) {
			index.removeChild(tocList);
		}
	}

	return { destroy };
}

document.addEventListener('DOMContentLoaded', () => {
	initTableOfContents();
});

module.exports = { initTableOfContents };
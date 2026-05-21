function toggleSubMenu(element, event) {
    if (event) {
        event.stopPropagation();
    }
    const navItem = element.closest('.nav-item');
    const subList = navItem.nextElementSibling;

    if (subList && subList.classList.contains('sub-nav-list')) {
        const isExpanded = navItem.classList.toggle('expanded');
        subList.classList.toggle('show');
    }
}

// Ensure expanded state is maintained if active item is inside
document.addEventListener('DOMContentLoaded', () => {
    const activeSubItem = document.querySelector('.sub-nav-item.active');
    if (activeSubItem) {
        const subList = activeSubItem.closest('.sub-nav-list');
        if (subList) {
            subList.classList.add('show');
            const prevNavItem = subList.previousElementSibling;
            if (prevNavItem && prevNavItem.classList.contains('nav-item')) {
                prevNavItem.classList.add('expanded');
            }
        }
    }
});

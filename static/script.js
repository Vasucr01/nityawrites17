// Mobile Navigation Toggle
const navToggle = document.getElementById('nav-toggle');
const navMenu = document.querySelector('.nav-menu');

if (navToggle) {
  navToggle.addEventListener('click', () => {
    navMenu.classList.toggle('active');
  });
}

// Update cart count from session
function updateCartCount() {
  // This will be updated when cart functionality is added
  const cartBadge = document.getElementById('cart-count');
  if (cartBadge) {
    // Get cart count from session storage or backend
    const cartCount = 0; // Replace with actual cart count
    cartBadge.textContent = cartCount;
  }
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    const href = this.getAttribute('href');
    if (href !== '#' && href.length > 1) {
      e.preventDefault();
      const target = document.querySelector(href);
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
        // Close mobile menu if open
        if (navMenu && navMenu.classList.contains('active')) {
          navMenu.classList.remove('active');
        }
      }
    }
  });
});

// Close mobile menu when clicking outside
document.addEventListener('click', (e) => {
  if (navMenu && navToggle) {
    if (!navMenu.contains(e.target) && !navToggle.contains(e.target)) {
      navMenu.classList.remove('active');
    }
  }
});

// Copy to Clipboard
function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    alert('UPI ID Copied: ' + text);
  }).catch(err => {
    console.error('Failed to copy: ', err);
  });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  updateCartCount();
});

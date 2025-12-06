// Smooth scrolling for anchor links (enhanced)
(function(){
  const navLinks = document.querySelectorAll('a[href^="#"]');
  for(const a of navLinks){
    a.addEventListener('click', function(e){
      const href = this.getAttribute('href');
      if(!href || href.charAt(0) !== '#') return;
      const target = document.querySelector(href);
      if(target){
        e.preventDefault();
        target.scrollIntoView({behavior:'smooth', block:'start'});
        history.pushState(null, '', href);
      }
    });
  }
})();

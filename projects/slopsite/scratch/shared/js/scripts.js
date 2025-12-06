// Lightweight anchor smooth-scroll behavior
(function(){
  // Enable smooth scrolling for in-page anchors
  const links = document.querySelectorAll('a[href^="#"]');
  for(let i=0;i<links.length;i++){
    const a = links[i];
    a.addEventListener('click', function(e){
      const targetId = this.getAttribute('href');
      if(targetId && targetId.startsWith('#')){
        const target = document.querySelector(targetId);
        if(target){
          e.preventDefault();
          target.scrollIntoView({behavior:'smooth', block:'start'});
          // Update URL hash without jumping
          history.pushState(null, '', targetId);
        }
      }
    });
  }
})();

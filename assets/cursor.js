/* rotor-site shared custom cursor — single source of truth.
   Used by: index.html, writing/* (via gen.py templates).
   Requires: #cdot, #cring, #ctrail1..3 elements in the page.
   Disabled automatically on touch / narrow screens via CSS. */
(function(){
  if(matchMedia('(hover:none)').matches) return;
  var dot=document.getElementById('cdot'),ring=document.getElementById('cring');
  if(!dot||!ring) return;
  var trails=[document.getElementById('ctrail1'),document.getElementById('ctrail2'),document.getElementById('ctrail3')].filter(Boolean);
  var lag=[.12,.08,.05],mx=innerWidth/2,my=innerHeight/2,rx=mx,ry=my;
  var tp=trails.map(function(){return {x:mx,y:my}});
  addEventListener('mousemove',function(e){
    mx=e.clientX;my=e.clientY;
    dot.style.left=mx+'px';dot.style.top=my+'px';
    document.body.classList.toggle('link-hover',!!e.target.closest('a,button,.work'));
  });
  (function loop(){
    rx+=(mx-rx)*.16;ry+=(my-ry)*.16;
    ring.style.left=rx+'px';ring.style.top=ry+'px';
    trails.forEach(function(el,i){var p=tp[i];p.x+=(mx-p.x)*lag[i];p.y+=(my-p.y)*lag[i];el.style.left=p.x+'px';el.style.top=p.y+'px';});
    requestAnimationFrame(loop);
  })();
})();

(function(){
 var inp=document.getElementById('dh-input'),
     clear=document.getElementById('dh-clear'),
     count=document.getElementById('dh-count'),
     cards=document.querySelectorAll('.dh-card'),
     accs=document.querySelectorAll('.dh-acc'),
     subs=document.querySelectorAll('.dh-sub'),
     noRes=document.getElementById('dh-no-results');

 function norm(s){return s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase()}
 var searching=false;

 function doSearch(){
  var q=norm(inp.value.trim());
  clear.className='dh-search-clear'+(q?' show':'');
  if(!q){
   searching=false;
   cards.forEach(function(c){c.classList.remove('dh-hidden')});
   accs.forEach(function(a){a.classList.remove('open','dh-sm');a.style.display=''});
   subs.forEach(function(s){s.classList.remove('open','dh-sm');s.style.display=''});
   count.className='dh-count';noRes.className='dh-no-results';
   return;
  }
  searching=true;
  var n=0;
  cards.forEach(function(c){
   var t=norm(c.getAttribute('data-name')||'');
   var p=norm(c.getAttribute('data-country')||'');
   var a=norm(c.getAttribute('data-aliases')||'');
   if(t.indexOf(q)>-1||p.indexOf(q)>-1||a.indexOf(q)>-1){c.classList.remove('dh-hidden');n++}
   else{c.classList.add('dh-hidden')}
  });
  subs.forEach(function(s){
   var vis=s.querySelectorAll('.dh-card:not(.dh-hidden)');
   if(vis.length){s.classList.add('open','dh-sm');s.style.display=''}
   else{s.style.display='none'}
  });
  accs.forEach(function(a){
   var vis=a.querySelectorAll('.dh-card:not(.dh-hidden)');
   if(vis.length){a.classList.add('open','dh-sm');a.style.display=''}
   else{a.style.display='none'}
  });
  var _l=document.documentElement.lang||'fr';count.textContent=n+' '+(n>1?(_l==='fr'?'destinations trouvées':'destinations found'):(_l==='fr'?'destination trouvée':'destination found'));
  count.className='dh-count show';
  noRes.className='dh-no-results'+(n===0?' show':'');
 }

 inp.addEventListener('input',doSearch);
 clear.addEventListener('click',function(){inp.value='';doSearch();inp.focus()});

 function toggleAcc(el,cls){
  el.addEventListener('click',function(){
   if(searching)return;
   var acc=el.parentElement;
   var wasOpen=acc.classList.contains('open');
   acc.classList.toggle('open');
   if(!wasOpen)setTimeout(function(){acc.scrollIntoView({behavior:'smooth',block:'start'})},80);
  });
 }
 document.querySelectorAll('.dh-acc-head').forEach(function(h){toggleAcc(h)});
 document.querySelectorAll('.dh-sub-head').forEach(function(h){toggleAcc(h)});
})();
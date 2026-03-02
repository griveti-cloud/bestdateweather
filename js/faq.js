function toggleFaq(btn){
  var a=btn.nextElementSibling;
  var opening=a.style.display!=="block";
  a.style.display=opening?"block":"none";
  btn.querySelector(".faq-icon").textContent=opening?"-":"+";
}

$(".dataModified").each(function(index){
  console.log($(this).text());
  dataModified_utc = $(this).text().replace("T", " ");
  console.log(dataModified_utc);
  dataModified_local = new Date(dataModified_utc+"Z");
  $(this).text(dataModified_local.toLocaleString());
});

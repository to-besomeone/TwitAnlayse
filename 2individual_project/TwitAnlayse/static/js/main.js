// $('#since-when').datepicker({
//     changeMonth: true,
//     changeYear: true,
//     dateFormat: "yy-mm-dd",
//     maxDate: "-3d",
//     onClose: function(selectedDate){
//         $('#until-when').datepicker("option", "minDate", selectedDate);
//         var date = $(this).datepicker('getDate');
//         date.setDate(date.getDate()+3);
//         $('#until-when').datepicker("option", "maxDate", date);
//     }
// });
// $('#until-when').datepicker({
//     changeMonth: true,
//     changeYear: true,
//     dateFormat: "yy-mm-dd",
//     maxDate: "0",
//     onClose: function(selectedDate){
//         $('#since-when').datepicker("option", "maxDate", selectedDate);
//     }
// });
//
// $(document).onsubmit(function(){
//     var emailPattern = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+\.([a-zA-Z0-9-]+)$/;
//     if(!emailPattern.test($('#email').val())){
//         alert("Please recheck your email");
//         $('#email').focus();
//         return false;
//     }
// });
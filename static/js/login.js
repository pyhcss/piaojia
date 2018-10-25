function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function getRandom(n){
    return Math.floor(Math.random()*n+1)
}

function getImage() {
    $(".form-login img").attr({"src":"/api/imagecode?rand="+getRandom(100)});
    return;
}

$(document).ready(function() {
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
    });
    $("#imagecode").focus(function(){
        $("#imagecode-err").hide();
    });
    $(".form-login").submit(function(e){
        e.preventDefault();
        $("#imgcode-err").hide();
        mobile = $("#mobile").val();
        passwd = $("#password").val();
        imgcode = $("#imagecode").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        } 
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        if (!imgcode) {
            $("#password-err span").html("请填写验证码!");
            $("#password-err").show();
            return;
        }
        var data = {};
        $(this).serializeArray().map(function(x){data[x.name] = x.value;});
        var jsonData = JSON.stringify(data);
        $.ajax({
            url:"/api/login",
            type:"POST",
            data: jsonData,
            contentType: "application/json",
            dataType: "json",
            headers:{
                "X-XSRFTOKEN":getCookie("_xsrf"),
            },
            success: function (data) {
                if ("4105" == data.errcode){
                    location.href = "/"
                } else if ("0" == data.errcode) {
                    location.href = "/home.html";
                    return;
                }
                else {
                    $("#imgcode-err span").html(data.errmsg);
                    $("#imgcode-err").show();
                    $(".form-login img").attr({"src":"/api/imagecode?rand="+getRandom(100)});
                    return;
                }
            }
        });
    });
});
//获取cookie
function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

//模态框居中的控制
function centerModals(){
    $('.modal').each(function(i){   //遍历每一个模态框
        var $clone = $(this).clone().css('display', 'block').appendTo('body');    
        var top = Math.round(($clone.height() - $clone.find('.modal-content').height()) / 2);
        top = top > 0 ? top : 0;
        $clone.remove();
        $(this).find('.modal-content').css("margin-top", top);  //-30);  //修正原先已经有的30个像素
    });
}

//清除车次模态框
function clearTrainModal(){
    if ($("#train_button").attr("data-target")){
        $("#train-btn").html("列车号");
        $("#train-btn").css({"color":"#999"});
        $("#train_button").removeAttr("data-target");
    }
}

//设置出发时间
function setStartDate() {
    var startDate = $("#start-date-input").val();
    if (startDate) {
        $("#start-date-btn").html(startDate);
        $("#start-date-btn").css({"color":"#555"});
    }
    $("#start-date-modal").modal("hide");
}

//设置车次信息
function setTrains(){
    var trains = "";
    $(".train-list input[type='checkbox']:checked").each(function () {
        trains += $(this).val() + ",";
    });
    trains = trains.substring(0,trains.length-1);
    if (trains){
        $("#train-btn").html(trains);
        $("#train-btn").css({"color":"#555"});
    } else{
        $("#train-btn").html("列车号");
        $("#train-btn").css({"color":"#999"});
    }
    $("#train-modal").modal("hide");
}

//设置座位类型
function setSeats(){
    var seats = "";
    $(".seat-list input[type='checkbox']:checked").each(function () {
        seats += $(this).val() + ",";
    });
    seats = seats.substring(0,seats.length-1);
    if (seats){
        $("#seat-btn").html(seats);
        $("#seat-btn").css({"color":"#555"});
    } else{
        $("#seat-btn").html("座位类型");
        $("#seat-btn").css({"color":"#999"});
    }
    $("#seat-modal").modal("hide");
}

//设置乘车人
function setPersons(){
    var persons = "";
    $(".person-list input[type='checkbox']:checked").each(function () {
        persons += $(this).val() + ",";
    });
    persons = persons.substring(0,persons.length-1);
    if (persons){
        $("#person-btn").html(persons);
        $("#person-btn").css({"color":"#555"});
    } else{
        $("#person-btn").html("乘车人");
        $("#person-btn").css({"color":"#999"});
    }
    $("#person-modal").modal("hide");
}

function getTrains(){
    $("#train_button").removeAttr("onclick");
    var from = $("#from").val();
    var to = $("#to").val();
    var date = $("#start-date-btn").html();
    if (!from){
        $("#from-err span").html("出发地不能为空");
        $("#from-err").show();
        $("#train_button").attr({"onclick":"getTrains();"});
        return;
    } else {
        $("#from-err").hide();
    }
    if (!to){
        $("#to-err span").html("目的地不能为空");
        $("#to-err").show();
        $("#train_button").attr({"onclick":"getTrains();"});
        return;
    } else {
        $("#to-err").hide();
    }
    if (!date || date=="出发日期"){
        $("#date-err span").html("出发日期不能为空");
        $("#date-err").show();
        $("#train_button").attr({"onclick":"getTrains();"});
        return;
    } else {
        $("#date-err").hide();
    }
    $.get(
        "/api/trainsinfo",
        {"from":from,"to":to,"date":date},
        function(data){
            if (data.errcode == "0"){
                $(".train-list").html(template("train-list-tmpl", {trains:data.trains}));
                $("#train-modal").modal("show");
                $("#train_button").attr({"data-target":"#train-modal"});
            } else if(data.errcode == "4101"){
                location.href="/login.html";
            } else {
                $("#date-err span").html(data.errmsg);
                $("#date-err").show();
            }
            $("#train_button").attr({"onclick":"getTrains();"});
        })
}

function updatePersons() {
    $("#update_persons").removeAttr("onclick");
    $("#update_persons").css({"background-color":"#ddd","border-color":"#ddd"});
    $.post(
        "/api/updatepersons",
        {"_xsrf":getCookie("_xsrf")},
        function(data){
            if (data.errcode == "0"){
                $(".person-list").html(template("person-list-tmpl", {persons:data.persons}));
                $("#person-modal").modal("show");
                $("#person_button").attr({"data-target":"#person-modal"});
            } else if(data.errcode == "4101"){
                location.href="/login.html";
            } else {
                $("#person-err span").html(data.errmsg);
                $("#person-err").show();
            }
        })
}

$(function() {
    $('.modal').on('show.bs.modal', centerModals);      //当模态框出现的时候
    $(window).on('resize', centerModals);               //当窗口大小变化的时候
    $("#start-date").datepicker({
        language: "zh-CN",
        keyboardNavigation: false,
        startDate: "today",
        format: "yyyy-mm-dd"
    });
    $("#start-date").on("changeDate", function() {
        var date = $(this).datepicker("getFormattedDate");
        $("#start-date-input").val(date);
    });  

    $.get("/api/personsinfo", function(data){
        if (data.errcode == "0"){
            $(".person-list").html(template("person-list-tmpl", {persons:data.persons}));
            $("#person_button").attr({"data-target":"#person-modal"});
            return;
        } else if("4101" == data.errcode){
            location.href="/login.html";
            return;
        } else {
            location.href="/submit.html";
            return;
            }
        });
    // 当用户点击表单提交按钮时执行自己定义的函数
    $(".form-register").submit(function (e) {
        // 阻止浏览器对于表单的默认行为
        e.preventDefault();
        // 校验用户填写的参数
        from = $("#from").val();
        to = $("#to").val();
        date = $("#start-date-btn").html();
        trains = $("#train-btn").html();
        seats = $("#seat-btn").html();
        persons = $("#person-btn").html();
        email = $("#email").val();
        if (!from) {
            $("#from-err span").html("出发地不能为空");
            $("#from-err").show();
            return false;
        } else{
            $("#from-err").hide();
        }
        if (!to) {
            $("#to-err span").html("目的地不能为空");
            $("#to-err").show();
            return false;
        } else{
            $("#to-err").hide();
        }
        if (!date || date=="出发日期") {
            $("#date-err span").html("出发日期不能为空");
            $("#date-err").show();
            return false;
        } else{
            $("#date-err").hide();
        }
        if (!trains || trains=="列车号") {
            $("#train-err span").html("列车号不能为空");
            $("#train-err").show();
            return false;
        } else{
            $("#train-err").hide();
        }
        if (!seats || seats=="座位类型") {
            $("#seat-err span").html("座位类型不能为空");
            $("#seat-err").show();
            return false;
        } else{
            $("#seat-err").hide();
        }
        if (!persons || persons=="乘车人") {
            $("#person-err span").html("乘车人不能为空");
            $("#person-err").show();
            return false;
        } else{
            $("#person-err").hide();
        }
        if (!email) {
            $("#email-err span").html("接收邮箱不能为空");
            $("#email-err").show();
            return false;
        } else{
            $("#email-err").hide();
        }

        // 声明一个要保存结果的变量
        var data = {"from":from,"to":to,"date":date,"trains":trains,"seats":seats,"persons":persons,"email":email};
        // 把data变量转为josn格式字符串
        var json_data = JSON.stringify(data);
        //向后端发送请求
        $.ajax({
            url: "/api/submitorder",
            method: "POST",
            data: json_data,
            contentType: "application/json", // 告诉后端服务器，发送的请求数据是json格式的
            dataType: "json",   // 告诉前端，收到的响应数据是json格式的
            headers: {
                "X-XSRFTOKEN": getCookie("_xsrf")
            },
            success: function (data) {
                if ("0" == data.errcode) {
                    alert("订单提交成功，请在我的订单中查看详细情况");
                    location.href = "/home.html";
                } else if("4101" == data.errcode){
                    location.href = "/login.html";
                }else {
                    $("#email-code-err span").html("注册失败、请稍后再试");
                    $("#email-code-err").show();
                }
            }
        })
    });
});
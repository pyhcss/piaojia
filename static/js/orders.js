//模态框居中的控制
function centerModals(){
    $('.modal').each(function(i){   //遍历每一个模态框
        var $clone = $(this).clone().css('display', 'block').appendTo('body');    
        var top = Math.round(($clone.height() - $clone.find('.modal-content').height()) / 2);
        top = top > 0 ? top : 0;
        $clone.remove();
        $(this).find('.modal-content').css("margin-top", top-30);  //修正原先已经有的30个像素
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    $('.modal').on('show.bs.modal', centerModals);      //当模态框出现的时候
    $(window).on('resize', centerModals);
    $.get("/api/myorder", function(data){
        if ("0" == data.errcode) {
            $(".orders-list").html(template("orders-list-tmpl", {orders:data.orders}));
            $(".order-comment").on("click", function(){
                var orderId = $(this).parents("li").attr("order-id");
                $(".modal-comment").attr("order-id", orderId);
            });
            $(".order-cancel").on("click",function(){
                var orderId = $(this).parents("li").attr("order-id");
                $(".modal-cancel").attr("order-id",orderId);
            });
            $(".modal-comment").on("click", function(){
                var orderId = $(this).attr("order-id");
                var comment = $("#comment").val();
                if (!comment) return;
                var data = {
                    order_id:orderId,
                    comment:comment,
                };
                $.ajax({
                    url:"/api/commentorder",
                    type:"POST",
                    data:JSON.stringify(data),
                    contentType:"application/json",
                    dataType:"json",
                    headers:{
                        "X-XSRFTOKEN":getCookie("_xsrf"),
                    },
                    success:function (data) {
                        if ("4101" == data.errcode) {
                            location.href = "/login.html";
                        } else if ("0" == data.errcode) {
                            $(".orders-list>li[order-id="+ orderId +"]>div.order-title>h4").html("已完成");
                            $(".orders-list>li[order-id="+ orderId +"]>div.order-content>div.order-text>div.order-operate").hide();
                            $("#comment-modal").modal("hide");
                        } else{
                            location.href = "/orders.html";
                        }
                    }
                });
            });
            $(".modal-cancel").on("click",function(){
                var orderId = $(this).attr("order-id");
                $.get(
                    "/api/cancelorder",
                    {"order_id":orderId},
                    function(data){
                        if ("4101" == data.errcode) {
                            location.href = "/login.html";
                        } else if ("0" == data.errcode) {
                            $(".orders-list>li[order-id="+ orderId +"]>div.order-title>h4").html("已取消");
                            $(".orders-list>li[order-id="+ orderId +"]>div.order-content>div.order-text>div.order-operate").hide();
                            $("#cancel-modal").modal("hide");
                        } else{
                            location.href = "/orders.html";
                        }
                    })
            });
        } else if("4101" == data.errcode){
            location.href = "/login.html";
        }
    });
});